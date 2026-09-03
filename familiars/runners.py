"""runners - a continuous pool that keeps this machine measuring while the model thinks.

WHY THIS EXISTS

`summon.py` answers a question when asked. That is still six seconds of the model's
attention spent on clerical work, and it is spent again every time anybody wonders
whether CI is green. Meanwhile the laptop - twenty cores - sits at idle.

So the checks are moved off the model's clock and onto the machine's. This is a
daemon. It runs the same familiars on their own cadences, forever, and leaves a
BOARD on disk. An agent that wants to know the state of the estate reads one file
instead of making six tool calls, and the answer is at most sixty seconds old.

    python familiars/runners.py --board logs/board.json    # run forever
    python familiars/runners.py --once                     # one sweep, for testing

WHAT THE BOARD PROMISES

Every entry names four things, because a measurement missing any of them is not a
measurement:

    what was measured · WHEN, in UTC · the commit, sha or URL it was read from · how long it took

There is no cheerful default anywhere in this file. A runner that cannot reach its
subject writes the error into its own slot and the slot says `error`. A false green
on a board that other agents will quote is worse than no board at all - it would be
read, believed, and repeated, and nothing downstream would ever check it again.

THE DISCIPLINES IT CARRIES, so nobody has to remember them

- `rc` is captured on its OWN line, into its own variable. `proof && echo PASS` is
  not a gate: under `set -e` the left side throws and the echo runs anyway.
- The cartridge ceiling is counted in CHARACTERS of decoded text. The current
  sld-sandbox is 371,622 bytes and 368,149 characters; `wc -c` would measure the
  wrong number against the right ceiling and report headroom that does not exist.
- The proof records gridatlas's HEAD and its dirty-file count alongside the result.
  A tree that moved mid-run produces neither a red nor a green - it produces
  UNMEASURABLE, and the board says so rather than picking one.
- CI is read from the runner's conclusion on the DEFAULT branch. A feature branch
  fails on its first run and that is not a defect.
- Nothing here prints or stores the GitHub token. It is fetched by the child that
  needs it, held in one variable, and dropped.

WINDOWS NOTE

multiprocessing re-imports this module in every worker, so the pool lives behind a
`__main__` guard and every worker is a module-level function in a real .py file.
Heredoc-piped code crashes the pool here; that is why this is a file.

CADENCES (--cadence name=seconds overrides any of them)

    live      60s   what the public receives right now
    ci        60s   conclusions on the default branch of the hot repos
    proof    300s   gridatlas `node tools/proofs/run-current.mjs`, rc on its own line
    ceiling  300s   cartridge characters against the ceiling
    estate   600s   the full 35-repo CI + git audit
    clicker  900s   two real Chromes on the live Atlas, 1400x900 and 393x852
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
import urllib.request
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool

GITHUB = r'C:\Users\vikra\OneDrive\Documents\GitHub'
CLAUDE_REPO = os.path.join(GITHUB, 'claude')
GRIDATLAS = os.path.join(GITHUB, 'gridatlas')

# The hot repos, checked every minute. The other 28 are covered by `estate` at 10 min.
HOT_REPOS = ['gridatlas', 'globalgrid2050', 'pipelinenews', 'claude', 'cvaa']

# Ceilings are on CHARACTERS of decoded text, never bytes.
CEILINGS = {'sld-sandbox': 368640, 'substation-intelligence': 400000}

LIVE_CURRENT = 'https://ventusltd.github.io/gridatlas/atlas/current.json'
LIVE_ATLAS = 'https://ventusltd.github.io/gridatlas/atlas/'
LIVE_URLS = [
    ('world', 'https://ventusltd.github.io/gridatlas/atlas/world/'),
    ('atlas', LIVE_ATLAS),
    ('homepage', 'https://globalgrid2050.com/'),
]

# Other lanes hold 8731, 8847, 9411-9413 and 9421-9422. These two are ours alone.
CLICKER_PORTS = {'desktop': 9431, 'mobile': 9432}

DEFAULT_CADENCE = {
    'live': 60,
    'ci': 60,
    'proof': 300,
    'ceiling': 300,
    'estate': 600,
    'clicker': 900,
}


def utc(t=None):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))


# ── small shared helpers (module level: the workers re-import this file) ──────

def _run(cmd, cwd=None, timeout=90):
    """Returns (rc, stdout, stderr). rc is a value, never inferred from a && chain."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, shell=False)
    except subprocess.TimeoutExpired:
        return None, '', 'timed out after %ss: %s' % (timeout, ' '.join(map(str, cmd))[:120])
    except Exception as exc:
        return None, '', '%s: %s' % (type(exc).__name__, str(exc)[:160])
    rc = p.returncode          # on its own line, from the process, not from an echo
    return rc, p.stdout, p.stderr


def _git(repo, *args, **kw):
    rc, out, _ = _run(['git', '-C', repo, *args], timeout=kw.get('timeout', 60))
    return out.rstrip() if rc == 0 else ''


def _token():
    """One variable, one caller, never printed and never written to the board."""
    try:
        p = subprocess.run(['git', 'credential', 'fill'],
                           input='protocol=https\nhost=github.com\n\n',
                           capture_output=True, text=True, cwd=GITHUB, timeout=45)
    except Exception:
        return None
    for line in p.stdout.splitlines():
        if line.startswith('password='):
            return line[9:]
    return None


def _api(path, token, timeout=45):
    req = urllib.request.Request('https://api.github.com/' + path, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'ventus-runners',
        **({'Authorization': 'Bearer ' + token} if token else {}),
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _get(url, timeout=40):
    """(status, body, headers). A failure returns status 0 and the reason - not a default."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except Exception as exc:
        return 0, ('%s: %s' % (type(exc).__name__, str(exc)[:160])).encode(), {}


# ── the runners ──────────────────────────────────────────────────────────────
#
# Each returns (value, read_from, fingerprint, note).
#   value       everything measured, for the JSON board
#   read_from   the URLs / shas / file paths the value was read from
#   fingerprint the small dict whose movement counts as NEWS
#   note        one human line for board.md
#
# Raising is allowed and expected: the wrapper turns it into this runner's error.

def run_live():
    """What the public receives right now, and the bytes it was read from."""
    st, body, hdrs = _get(LIVE_CURRENT)
    if st != 200:
        raise RuntimeError('%s -> HTTP %s (%s)' % (LIVE_CURRENT, st, body.decode('utf-8', 'replace')[:120]))
    digest = hashlib.sha256(body).hexdigest()
    doc = json.loads(body.decode('utf-8'))
    value = {
        'generation': doc.get('generation'),
        'previous_generation': doc.get('previous_generation'),
        'release_id': doc.get('release_id'),
        'current_json_sha256': digest,
        'current_json_bytes': len(body),
        'last_modified': hdrs.get('Last-Modified'),
        'http': {},
    }
    for label, url in LIVE_URLS:
        s, b, _ = _get(url)
        value['http'][label] = s if s else 'ERR ' + b.decode('utf-8', 'replace')[:80]
    read_from = [LIVE_CURRENT + ' sha256:' + digest[:16]] + [u for _, u in LIVE_URLS]
    fp = {'generation': value['generation'],
          'current_json_sha256': digest[:16]}
    fp.update({'http.' + k: v for k, v in value['http'].items()})
    note = 'generation %s · %s' % (
        value['generation'],
        ' '.join('%s %s' % (k, v) for k, v in value['http'].items()))
    return value, read_from, fp, note


def run_ci():
    """Conclusions on each hot repo's DEFAULT branch, at that branch's head sha."""
    token = _token()
    if not token:
        raise RuntimeError('no credential from `git credential fill` - unauthenticated '
                           'polling is 60/hour and would give a wrong answer within the hour')
    value, read_from, fp, bad = {}, [], {}, []
    for name in HOT_REPOS:
        full = 'Ventusltd/' + name
        try:
            meta = _api('repos/' + full, token)
            branch = meta.get('default_branch') or 'main'
            runs = _api('repos/%s/actions/runs?branch=%s&per_page=60' % (full, branch), token)
        except Exception as exc:
            value[name] = {'state': 'unreachable', 'detail': '%s: %s' % (type(exc).__name__, str(exc)[:120])}
            fp[name] = 'unreachable'
            continue
        items = [r for r in runs.get('workflow_runs', []) if r.get('head_branch') == branch]
        if not items:
            value[name] = {'state': 'no-runs', 'branch': branch}
            fp[name] = 'no-runs'
            continue
        head_sha = (items[0].get('head_sha') or '')[:7]
        latest = {}
        for r in items:                              # API returns newest first
            latest.setdefault(r['name'], r)
        reds_at_head, reds_stale, green, waiting = [], [], 0, 0
        for wf, r in latest.items():
            sha = (r.get('head_sha') or '')[:7]
            if r.get('status') != 'completed':
                waiting += 1
            elif r.get('conclusion') == 'success':
                green += 1
            elif r.get('conclusion') in ('failure', 'timed_out', 'startup_failure'):
                (reds_at_head if sha == head_sha else reds_stale).append(
                    {'workflow': wf, 'sha': sha, 'conclusion': r.get('conclusion'),
                     'at': r.get('updated_at'), 'run_id': r.get('id')})
        state = 'RED' if reds_at_head else ('stale-red' if reds_stale else
                                            ('green' if green else 'none-completed'))
        value[name] = {'state': state, 'branch': branch, 'head_sha': head_sha,
                       'workflows': len(latest), 'green': green, 'waiting': waiting,
                       'reds_at_head': reds_at_head, 'reds_stale': reds_stale}
        read_from.append('%s@%s (%s)' % (full, head_sha, branch))
        fp[name] = '%s %s' % (head_sha, state)
        if state == 'RED':
            bad.append('%s %s %s' % (name, head_sha,
                                     ','.join(r['workflow'][:24] for r in reds_at_head)))
    note = ('RED: ' + '; '.join(bad)) if bad else ('green at head: ' + ', '.join(
        '%s %s' % (k, v.get('head_sha')) for k, v in value.items() if v.get('state') == 'green'))
    return value, read_from, fp, note


def run_estate():
    """The full account-wide audit. Repos come from the API, never from disk."""
    script = os.path.join(CLAUDE_REPO, 'scripts', 'audit_estate.py')
    if not os.path.isfile(script):
        raise RuntimeError('scripts/audit_estate.py is missing at ' + script)
    out_json = os.path.join(CLAUDE_REPO, 'logs', 'runners-estate.json')
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    rc, out, err = _run([sys.executable, script, '--json', out_json],
                        cwd=CLAUDE_REPO, timeout=420)
    if rc is None:
        raise RuntimeError('audit_estate.py did not finish: ' + (err or 'no reason given'))
    if rc != 0:
        raise RuntimeError('audit_estate.py rc=%s: %s' % (rc, (err or out)[-300:]))
    with open(out_json, encoding='utf-8') as fh:
        doc = json.load(fh)
    ci, gits = doc.get('ci', []), doc.get('git', [])
    reds = [c for c in ci if c.get('state') == 'red']
    unreachable = [c['repo'] for c in ci if c.get('state') == 'unreachable']
    dirty = [g for g in gits if g.get('present') and not g.get('measurable')]
    drifted = [g for g in gits if g.get('present') and
               (g.get('ahead') not in ('0', '?') or g.get('behind') not in ('0', '?'))]
    value = {
        'audit_measured_utc': doc.get('measured_utc'),
        'repos_from_api': len(ci),
        'local_clones': len(gits),
        'red_at_head': [{'repo': c['repo'], 'sha': c.get('head_sha'),
                         'workflows': [r['workflow'] for r in c.get('reds', []) if r.get('at_head')]}
                        for c in reds],
        'stale_red': sorted(c['repo'] for c in ci if c.get('state') == 'stale-red'),
        'green': sorted(c['repo'] for c in ci if c.get('state') == 'green'),
        'unreachable': unreachable,
        # A dirty tree is UNMEASURABLE - never a red, never a green, never a defect.
        'unmeasurable_trees': [{'repo': g['repo'], 'modified': g['modified'],
                                'paths': g.get('modified_paths', [])[:6]} for g in dirty],
        'drifted': [{'repo': g['repo'], 'ahead': g['ahead'], 'behind': g['behind'],
                     'branch': g['branch']} for g in drifted],
        'crlf_worktrees': {g['repo']: g['crlf_files'] for g in gits if g.get('crlf_files')},
        'heads': {g['repo']: g.get('local_head') for g in gits if g.get('present')},
    }
    read_from = ['github api: %d repos, default branches only' % len(ci)] + [
        '%s@%s' % (c['repo'], c.get('head_sha')) for c in ci if c.get('head_sha')][:40]
    fp = {'repos': len(ci),
          'red': sorted('%s@%s' % (c['repo'], c.get('head_sha')) for c in reds),
          'stale_red': value['stale_red'],
          'unreachable': sorted(unreachable),
          'unmeasurable': sorted(g['repo'] for g in dirty)}
    note = '%d repos · %d red at head · %d stale-red · %d trees unmeasurable' % (
        len(ci), len(reds), len(value['stale_red']), len(dirty))
    return value, read_from, fp, note


def run_proof():
    """gridatlas `node tools/proofs/run-current.mjs`. rc is read, not inferred.

    The tree is fingerprinted before AND after, because another lane can move it
    mid-run. If it moved, this is UNMEASURABLE and says so - a third state that
    produces neither a red nor a green."""
    runner = os.path.join(GRIDATLAS, 'tools', 'proofs', 'run-current.mjs')
    if not os.path.isfile(runner):
        raise RuntimeError('run-current.mjs missing at ' + runner)
    head_before = _git(GRIDATLAS, 'rev-parse', 'HEAD')[:7]
    dirty_before = [l for l in _git(GRIDATLAS, 'status', '--porcelain').splitlines() if l]

    t0 = time.time()
    rc, out, err = _run(['node', runner], cwd=GRIDATLAS, timeout=900)
    node_seconds = round(time.time() - t0, 1)
    # rc, on its own line, out of the completed process. `node x && echo PASS`
    # would have printed PASS for the rc=1 this actually returns today.
    if rc is None:
        raise RuntimeError('node did not finish: ' + (err or 'no reason given'))

    head_after = _git(GRIDATLAS, 'rev-parse', 'HEAD')[:7]
    dirty_after = [l for l in _git(GRIDATLAS, 'status', '--porcelain').splitlines() if l]
    moved = (head_before != head_after) or (dirty_before != dirty_after)

    lines = out.splitlines()
    counts = [l.strip() for l in lines if 'checks passed' in l]
    fails, in_failures = [], False
    for l in lines:
        if l.strip().startswith('FAILURES'):
            in_failures = True
            continue
        if in_failures and l.strip():
            fails.append(l.strip())
    value = {
        'rc': rc,
        'verdict': 'UNMEASURABLE' if moved else ('pass' if rc == 0 else 'fail'),
        'node_seconds': node_seconds,
        'checks': counts[-1] if counts else None,
        'failures': fails[:12],
        'failure_count': len(fails),
        'gridatlas_head': head_before,
        'dirty_files_before': len(dirty_before),
        'dirty_files_after': len(dirty_after),
        'tree_moved_during_run': moved,
        'stderr_tail': err.strip()[-300:] or None,
    }
    if dirty_before:
        value['caveat'] = ('the working tree was dirty (%d files) - this measures a '
                           'workspace, not the committed artefact' % len(dirty_before))
    read_from = ['%s @ %s (%d dirty)' % (runner, head_before, len(dirty_before))]
    fp = {'rc': rc, 'checks': value['checks'], 'head': head_before,
          'failures': fails[:12], 'verdict': value['verdict']}
    note = 'rc=%s %s · %s · head %s%s' % (
        rc, value['verdict'], value['checks'] or 'no count line', head_before,
        ' · TREE MOVED MID-RUN' if moved else '')
    return value, read_from, fp, note


def run_ceiling():
    """Cartridge size in CHARACTERS of decoded text. Bytes are a different number."""
    carts = os.path.join(GRIDATLAS, 'atlas', 'cartridges')
    if not os.path.isdir(carts):
        raise RuntimeError('no cartridges directory at ' + carts)
    newest = {}
    for fn in sorted(os.listdir(carts)):
        if not fn.endswith('.js'):
            continue
        for key in CEILINGS:
            if key in fn and (key not in newest or fn > newest[key]):
                newest[key] = fn                     # names sort by their UTC stamp
    if not newest:
        raise RuntimeError('no cartridge matched %s in %s' % (sorted(CEILINGS), carts))
    value, read_from, fp, over = {}, [], {}, []
    for key, fn in sorted(newest.items()):
        path = os.path.join(carts, fn)
        with open(path, 'rb') as fh:
            raw = fh.read()
        text = raw.decode('utf-8')                   # CHARACTERS, after decoding
        chars, ceiling = len(text), CEILINGS[key]
        value[key] = {'file': fn, 'chars': chars, 'bytes': len(raw),
                      'ceiling_chars': ceiling, 'headroom_chars': ceiling - chars,
                      'over_ceiling': chars > ceiling,
                      'sha256': hashlib.sha256(raw).hexdigest()[:16]}
        read_from.append('%s sha256:%s' % (path, value[key]['sha256']))
        fp[key] = '%s %d/%d' % (fn, chars, ceiling)
        if chars > ceiling:
            over.append('%s %d > %d' % (key, chars, ceiling))
    note = ('OVER: ' + '; '.join(over)) if over else ' · '.join(
        '%s %d/%d chars, %d left' % (k, v['chars'], v['ceiling_chars'], v['headroom_chars'])
        for k, v in sorted(value.items()))
    return value, read_from, fp, note


def run_clicker():
    """Two real Chromes on the live Atlas: 1400x900 and 393x852.

    Each launches its OWN browser on its OWN port with its OWN profile, so two
    lanes cannot corrupt one another's readings. A journey that aborts because
    `document.hidden` was true is reported as an abort, never as a number - a
    backgrounded tab stalls MapLibre and produces confident false failures."""
    clicker = os.path.join(CLAUDE_REPO, 'familiars', 'clicker.py')
    if not os.path.isfile(clicker):
        raise RuntimeError('clicker.py missing at ' + clicker)

    # Name the generation the browsers actually saw, so the reading names its subject.
    st, body, _ = _get(LIVE_CURRENT)
    generation = None
    if st == 200:
        try:
            generation = json.loads(body.decode('utf-8')).get('generation')
        except Exception:
            generation = 'unparseable'

    shots = os.path.join(CLAUDE_REPO, 'logs', 'runners-shots')
    value, read_from, fp, notes = {'live_generation': generation}, [LIVE_ATLAS], {}, []
    for label, port in sorted(CLICKER_PORTS.items()):
        cmd = [sys.executable, clicker, '--port', str(port), '--url', LIVE_ATLAS,
               '--journey', 'atlas-rest', '--shots', os.path.join(shots, label)]
        if label == 'mobile':
            cmd.append('--mobile')
        rc, out, err = _run(cmd, cwd=CLAUDE_REPO, timeout=300)
        if rc is None:
            value[label] = {'error': err or 'clicker did not finish'}
            fp[label] = 'error'
            notes.append('%s ERROR' % label)
            continue
        try:
            got = json.loads(out)
        except Exception:
            value[label] = {'error': 'clicker rc=%s produced no JSON: %s'
                                     % (rc, (err or out).strip()[-260:])}
            fp[label] = 'no-json'
            notes.append('%s ERROR' % label)
            continue
        if got.get('ABORT'):
            value[label] = {'abort': got['ABORT'], 'viewport': got.get('viewport'), 'rc': rc}
            fp[label] = 'ABORT'
            notes.append('%s ABORT' % label)
            continue
        rest = got.get('at_rest') or {}
        value[label] = {
            'rc': rc,
            'viewport': rest.get('viewport'),
            'map_percent': rest.get('map_percent'),
            'chrome_percent': rest.get('chrome_percent'),
            'nothing_percent': rest.get('nothing_percent'),
            'chrome_owners': rest.get('chrome_owners', [])[:6],
            'console_errors': got.get('console_errors', [])[:4],
            'shots': got.get('shots', []),
        }
        read_from.append('%s at %s in a headless Chrome on port %d' % (LIVE_ATLAS, rest.get('viewport'), port))
        fp[label] = '%s map %s%%' % (rest.get('viewport'), rest.get('map_percent'))
        notes.append('%s %s map %s%% chrome %s%%' % (
            label, rest.get('viewport'), rest.get('map_percent'), rest.get('chrome_percent')))
    fp['generation'] = generation
    return value, read_from, fp, 'gen %s · %s' % (generation, ' · '.join(notes))


RUNNERS = {
    'live': run_live,
    'ci': run_ci,
    'estate': run_estate,
    'proof': run_proof,
    'ceiling': run_ceiling,
    'clicker': run_clicker,
}


def call(name):
    """The only thing a worker process ever runs. It cannot raise past here.

    A crash inside one runner becomes that runner's error on the board. It must
    never take the pool down and it must never be silently swallowed either."""
    started = time.time()
    try:
        value, read_from, fp, note = RUNNERS[name]()
        return {'runner': name, 'status': 'ok', 'measured_utc': utc(started),
                'finished_utc': utc(), 'seconds': round(time.time() - started, 2),
                'read_from': read_from, 'value': value, 'fingerprint': fp,
                'note': note, 'error': None, 'pid': os.getpid()}
    except Exception as exc:
        return {'runner': name, 'status': 'error', 'measured_utc': utc(started),
                'finished_utc': utc(), 'seconds': round(time.time() - started, 2),
                'read_from': [], 'value': None,
                # An error is NEWS: its fingerprint moves so the board reports it.
                'fingerprint': {'error': '%s: %s' % (type(exc).__name__, str(exc)[:200])},
                'note': 'ERROR %s: %s' % (type(exc).__name__, str(exc)[:200]),
                'error': {'type': type(exc).__name__, 'message': str(exc)[:400],
                          'traceback': traceback.format_exc()[-1200:]},
                'pid': os.getpid()}


# ── the board ────────────────────────────────────────────────────────────────

def diff_fingerprints(old, new):
    """Only what MOVED. Silence is the correct output when nothing did."""
    moves = []
    for runner in sorted(set(old) | set(new)):
        a = old.get(runner) or {}
        b = new.get(runner) or {}
        if not b:
            continue
        if not a:
            moves.append('%s: first reading' % runner)
            continue
        for key in sorted(set(a) | set(b)):
            va, vb = a.get(key, '(absent)'), b.get(key, '(absent)')
            if va != vb:
                moves.append('%s.%s: %s -> %s'
                             % (runner, key, json.dumps(va)[:110], json.dumps(vb)[:110]))
    return moves


def render_md(board):
    d, R = board['daemon'], board['runners']
    L = []
    L.append('# runners board')
    L.append('')
    L.append('written %s · started %s · up %s · ticks %d · full sweeps %d'
             % (board['written_utc'], d['started_utc'], d['uptime'], d['ticks'], d['full_sweeps']))
    L.append('')
    L.append('%d cores, pool cap %d workers (%d left free), %d runners'
             % (board['host']['cores'], board['host']['pool_workers'],
                board['host']['cores_left_free'], len(R)))
    L.append('')
    L.append(board['host']['note'])
    L.append('')
    L.append('| runner | state | measured (UTC) | took | age | runs | errors | reading |')
    L.append('|---|---|---|---|---|---|---|---|')
    for name in sorted(R):
        e = R[name]
        L.append('| %s | %s | %s | %ss | %ss | %d | %d | %s |'
                 % (name, e['status'].upper() if e['status'] != 'ok' else 'ok',
                    e.get('measured_utc') or '-', e.get('seconds', '-'),
                    e.get('age_seconds', '-'), e.get('runs', 0), e.get('errors', 0),
                    (e.get('note') or '').replace('|', '/')[:150]))
    L.append('')
    for name in sorted(R):
        e = R[name]
        L.append('## %s — %s at %s in %ss (every %ss)'
                 % (name, e['status'], e.get('measured_utc'), e.get('seconds'),
                    e.get('cadence_seconds')))
        for src in (e.get('read_from') or ['(nothing was read)']):
            L.append('    read from %s' % src)
        L.append('')
        L.append('    ' + (e.get('note') or '(no reading)'))
        if e.get('error'):
            L.append('    %s: %s' % (e['error']['type'], e['error']['message']))
        if e.get('in_flight'):
            L.append('    (a fresh run is in flight, started %s)' % e.get('in_flight_since'))
        L.append('')
    L.append('## CHANGES since %s' % (board['changes_since'] or 'the daemon started'))
    L.append('')
    if board['changes']:
        for line in board['changes']:
            L.append('- %s' % line)
    else:
        L.append('(nothing moved)')
    L.append('')
    return '\n'.join(L)


def write_atomic(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    os.replace(tmp, path)


# ── the daemon ───────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--board', default=os.path.join('logs', 'board.json'))
    ap.add_argument('--once', action='store_true',
                    help='run every runner once, write the board, exit')
    ap.add_argument('--only', nargs='*', help='limit to these runners')
    ap.add_argument('--tick', type=float, default=5.0, help='seconds between scheduling passes')
    ap.add_argument('--free-cores', type=int, default=4,
                    help='cores to leave for the human (default 4)')
    ap.add_argument('--cadence', nargs='*', default=[],
                    help='override a cadence, e.g. clicker=300')
    a = ap.parse_args(argv)

    cadence = dict(DEFAULT_CADENCE)
    for spec in a.cadence:
        key, _, val = spec.partition('=')
        if key not in cadence or not val.isdigit():
            print('bad --cadence %r; known: %s' % (spec, ', '.join(sorted(cadence))))
            return 2
        cadence[key] = int(val)

    wanted = [n for n in RUNNERS if not a.only or n in a.only]
    if not wanted:
        print('no such runner; known: %s' % ', '.join(sorted(RUNNERS)))
        return 2

    board_path = a.board if os.path.isabs(a.board) else os.path.join(CLAUDE_REPO, a.board)
    md_path = os.path.splitext(board_path)[0] + '.md'

    cores = os.cpu_count() or 4
    # The pool is capped so the machine stays usable. In practice only as many
    # workers as there are DUE runners are ever alive at once - but the estate
    # audit threads 12 API calls of its own and the clicker fleet runs two whole
    # Chromes, so the headroom under the cap is not wasted.
    cap = max(2, cores - max(0, a.free_cores))

    # Carry the previous board's fingerprints across a restart, so the first
    # CHANGES section after a restart still says what moved while we were down.
    prev_fp, started_wall = {}, time.time()
    if os.path.isfile(board_path):
        try:
            with open(board_path, encoding='utf-8') as fh:
                old = json.load(fh)
            prev_fp = {k: v.get('fingerprint') or {} for k, v in (old.get('runners') or {}).items()}
        except Exception as exc:
            print('previous board unreadable (%s) - starting the diff from empty' % str(exc)[:80])

    state = {n: {'runner': n, 'status': 'never-run', 'cadence_seconds': cadence[n],
                 'runs': 0, 'errors': 0, 'note': None, 'measured_utc': None,
                 'read_from': [], 'value': None, 'fingerprint': {}, 'error': None,
                 'seconds': None, 'in_flight': False, 'in_flight_since': None}
             for n in wanted}
    last_started = {n: 0.0 for n in wanted}
    inflight = {}
    ticks = 0
    full_sweeps = 0
    seen_since_sweep = set()
    # Changes accumulate across a sweep and reset when the sweep closes, so the
    # CHANGES section answers "what has moved since every runner last reported"
    # rather than "what moved in the last five-second scheduling pass".
    changes = []
    changes_since = utc(started_wall) + ' (daemon start)'

    print('runners: %d on %d cores, pool cap %d, board %s'
          % (len(wanted), cores, cap, board_path))
    print('cadences: %s' % ', '.join('%s %ss' % (n, cadence[n]) for n in sorted(wanted)))

    pool = ProcessPoolExecutor(max_workers=cap)
    try:
        while True:
            ticks += 1
            now = time.time()

            # 1. submit anything due that is not already in flight
            for name in wanted:
                if name in inflight:
                    continue
                due = state[name]['status'] == 'never-run' or (now - last_started[name]) >= cadence[name]
                if not due:
                    continue
                try:
                    inflight[name] = pool.submit(call, name)
                except (BrokenProcessPool, RuntimeError) as exc:
                    # The pool died under us. Rebuild it and record why, rather
                    # than exiting: a daemon that stops on a worker crash is worse
                    # than no daemon, because its board goes quietly stale.
                    print('pool broken (%s) - rebuilding' % str(exc)[:100])
                    try:
                        pool.shutdown(wait=False)
                    except Exception:
                        pass
                    pool = ProcessPoolExecutor(max_workers=cap)
                    inflight.clear()
                    break
                last_started[name] = now
                state[name]['in_flight'] = True
                state[name]['in_flight_since'] = utc(now)

            # 2. harvest whatever has finished
            new_fp = {}
            for name in list(inflight):
                fut = inflight[name]
                if not fut.done():
                    continue
                del inflight[name]
                try:
                    res = fut.result()
                except Exception as exc:
                    # A worker that died without returning (killed, BrokenProcessPool)
                    # is still this runner's error, and the board must say so.
                    res = {'runner': name, 'status': 'error', 'measured_utc': utc(),
                           'finished_utc': utc(), 'seconds': None, 'read_from': [],
                           'value': None,
                           'fingerprint': {'error': 'worker died: %s' % str(exc)[:160]},
                           'note': 'ERROR worker died: %s' % str(exc)[:160],
                           'error': {'type': type(exc).__name__, 'message': str(exc)[:400],
                                     'traceback': ''}}
                prev = state[name]
                res['cadence_seconds'] = cadence[name]
                res['runs'] = prev['runs'] + 1
                res['errors'] = prev['errors'] + (1 if res['status'] == 'error' else 0)
                res['in_flight'] = False
                res['in_flight_since'] = None
                state[name] = res
                new_fp[name] = res.get('fingerprint') or {}
                seen_since_sweep.add(name)
                # The console log is forced to ASCII. A background redirect can be
                # cp1252 here, and a UnicodeEncodeError in the logging line would
                # kill the daemon over a middot.
                line = '%s  %-8s %-5s %ss  %s' % (utc(), name, res['status'],
                                                  res.get('seconds'), (res.get('note') or '')[:150])
                print(line.encode('ascii', 'replace').decode('ascii'), flush=True)

            # 3. only the runners that just reported are diffed. A runner that did
            #    not run this pass has not moved, and claiming it did would be news
            #    about nothing.
            if new_fp:
                stamp = utc()
                changes += ['%s  %s' % (stamp, line)
                            for line in diff_fingerprints(prev_fp, new_fp)]
                prev_fp = {**prev_fp, **new_fp}

            # 4. a full sweep is every runner having reported since the last one
            sweep_closed = False
            if seen_since_sweep >= set(wanted):
                full_sweeps += 1
                seen_since_sweep = set()
                sweep_closed = True

            # 5. write the board whenever anything moved (and on a sweep close)
            if new_fp or sweep_closed:
                for name in state:
                    e = state[name]
                    e['age_seconds'] = (round(time.time() - last_started[name], 1)
                                        if e.get('measured_utc') else None)
                    e['next_due_utc'] = utc(last_started[name] + cadence[name]) if last_started[name] else None
                board = {
                    'board': 'familiars.runners.v1',
                    'written_utc': utc(),
                    'host': {'cores': cores, 'pool_workers': cap,
                             'cores_left_free': max(0, cores - cap),
                             'python': sys.version.split()[0],
                             'note': ('CPU only. The GPU is exercised only through the '
                                      'clicker fleet\'s WebGL; the NPU is not addressable '
                                      'from this process.')},
                    'daemon': {'started_utc': utc(started_wall),
                               'uptime': '%ds' % int(time.time() - started_wall),
                               'ticks': ticks, 'full_sweeps': full_sweeps,
                               'in_flight': sorted(inflight)},
                    'cadence_seconds': {n: cadence[n] for n in sorted(wanted)},
                    'changes_since': changes_since,
                    'changes': changes,
                    'runners': state,
                }
                write_atomic(board_path, json.dumps(board, indent=1, default=str))
                write_atomic(md_path, render_md(board))
                if sweep_closed:
                    # The sweep is the unit. Its news is published once, then the
                    # slate is clean and silence means silence.
                    changes = []
                    changes_since = '%s (sweep %d closed)' % (board['written_utc'], full_sweeps)

            if a.once and not inflight and all(
                    state[n]['status'] != 'never-run' for n in wanted):
                break
            time.sleep(a.tick if not a.once else 0.5)
    except KeyboardInterrupt:
        print('stopped by keyboard at %s' % utc())
    finally:
        try:
            pool.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            pool.shutdown(wait=False)
    print('board: %s\nmd:    %s' % (board_path, md_path))
    return 0


if __name__ == '__main__':
    sys.exit(main())
