"""ci_history_mine.py - the whole CI history of every repository, not just its last run.

WHY THIS EXISTS, AND WHY IT IS NOT audit_estate.py

audit_estate.py answers "what is red right now?". It takes the LATEST run per workflow on
the default branch and files it. That is the right question at the start of a session and
the wrong question for a workflow that has never worked in its life, because a workflow
whose every run failed looks exactly like a workflow whose last run failed. One is a
regression. The other was never green, and the difference decides whether you are fixing
something or finishing it.

It also carries audit_estate.py's own blind spot, deliberately. That script's enumeration is

    success                                    -> green
    failure / timed_out / startup_failure      -> red
    everything else                            -> counted as neither  (its line 136)

so `cancelled`, `skipped`, `neutral`, `action_required` and `stale` fall through the reader
and are reported as nothing at all. A workflow that only ever gets cancelled reports state
'none' - indistinguishable from a workflow that has never run. This script counts those
conclusions by name and reports the total that the other reader drops, so the size of the
blind spot is a number rather than a suspicion.

WHAT IT MEASURES, per workflow, over its whole readable history (default 200 runs):

  ever_success      has this workflow EVER concluded success? The headline.
  census            every conclusion by name, including the ones audit_estate.py drops
  unenumerated      how many of this workflow's runs that other reader counts as nothing
  at_head           is the last run's sha the default branch's current head sha?
                    A red on a commit that is no longer head does not make today red.

THIS IS AN INFORMATIONAL SURVEY. IT EXITS 0 ON EVERY FINDING, ALWAYS.

A survey that exits non-zero is lying about its role - it is a report, not a gate - and in
GitHub Actions a non-zero exit mails the actor. The estate's rule is that informational
jobs are silent and gates are loud. Findings live in the JSON and the board file, never in
the exit code. If you are about to "fix" this into a gate: don't. Write a separate gate.

    python scripts/ci_history_mine.py --out ci-history.json --board docs/boards/ci-history.md

The token is read once, held in one variable, never printed and never written down.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

API = 'https://api.github.com/'

# audit_estate.py's enumeration, verbatim, so the blind spot is measured against the real
# reader rather than against a remembered version of it.
COUNTED_GREEN = {'success'}
COUNTED_RED = {'failure', 'timed_out', 'startup_failure'}
COUNTED = COUNTED_GREEN | COUNTED_RED


def token():
    """Actions hands it in the environment. On the laptop, git's credential helper holds it."""
    for var in ('GH_TOKEN', 'GITHUB_TOKEN'):
        if os.environ.get(var):
            return os.environ[var]
    try:
        p = subprocess.run(['git', 'credential', 'fill'],
                           input='protocol=https\nhost=github.com\n\n',
                           capture_output=True, text=True, timeout=30)
        for line in p.stdout.splitlines():
            if line.startswith('password='):
                return line[9:]
    except Exception:
        pass
    return None


TOKEN = token()


def api(path, retries=2):
    req = urllib.request.Request(API + path, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'ventus-ci-history-mine',
        **({'Authorization': 'Bearer ' + TOKEN} if TOKEN else {}),
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except urllib.error.HTTPError as exc:
            # 403/404 on a cross-repo read is a PERMISSION FACT, not a transient error.
            # Report it as such rather than retrying into the rate limit.
            if exc.code in (403, 404):
                return {'_error': 'HTTP %d' % exc.code, '_code': exc.code}
            if attempt == retries:
                return {'_error': 'HTTP %d' % exc.code, '_code': exc.code}
            time.sleep(1.5)
        except Exception as exc:
            if attempt == retries:
                return {'_error': str(exc)[:120], '_code': 0}
            time.sleep(1.5)


def repos(owner):
    """Every repo the account owns. From the API, never from disk - disk lies by omission."""
    out, page = [], 1
    while True:
        got = api('user/repos?per_page=100&affiliation=owner&sort=full_name&page=%d' % page)
        if not isinstance(got, list):
            # No credential, or a token that cannot list. Fall back to the public listing.
            got = api('users/%s/repos?per_page=100&sort=full_name&page=%d' % (owner, page))
            if not isinstance(got, list):
                break
        if not got:
            break
        out += [{'name': r['name'], 'full': r['full_name'], 'default': r['default_branch'],
                 'private': r['private'], 'archived': r['archived']} for r in got]
        if len(got) < 100:
            break
        page += 1
    return [r for r in out if r['full'].split('/')[0].lower() == owner.lower()]


def head_sha(repo):
    got = api('repos/%s/branches/%s' % (repo['full'], repo['default']))
    if isinstance(got, dict) and not got.get('_error'):
        return (got.get('commit') or {}).get('sha') or ''
    return ''


def runs_for(repo, wf_id, max_runs):
    """Newest first. Pages until max_runs or exhaustion."""
    out, page = [], 1
    while len(out) < max_runs:
        got = api('repos/%s/actions/workflows/%s/runs?per_page=100&page=%d'
                  % (repo['full'], wf_id, page))
        if not isinstance(got, dict) or got.get('_error'):
            return out, got.get('_error') if isinstance(got, dict) else 'unreadable'
        batch = got.get('workflow_runs') or []
        out += batch
        if len(batch) < 100:
            break
        page += 1
    return out[:max_runs], None


def mine(repo, max_runs):
    wfs = api('repos/%s/actions/workflows?per_page=100' % repo['full'])
    if not isinstance(wfs, dict) or wfs.get('_error'):
        return {'repo': repo['name'], 'full': repo['full'], 'private': repo['private'],
                'readable': False,
                'detail': wfs.get('_error') if isinstance(wfs, dict) else 'unreadable',
                'workflows': []}

    sha = head_sha(repo)
    rows = []
    for wf in wfs.get('workflows', []):
        runs, err = runs_for(repo, wf['id'], max_runs)
        census = Counter()
        for r in runs:
            if r.get('status') != 'completed':
                census[r.get('status') or 'unknown'] += 1
            else:
                census[r.get('conclusion') or 'null'] += 1

        completed = [r for r in runs if r.get('status') == 'completed']
        ever_success = any(r.get('conclusion') == 'success' for r in completed)
        unenumerated = sum(n for c, n in census.items()
                           if c not in COUNTED and c not in ('in_progress', 'queued',
                                                             'requested', 'waiting', 'pending'))

        # The last run ON THE DEFAULT BRANCH decides at-head vs stale. A workflow whose
        # last run was a branch push says nothing about the default branch's health.
        on_default = [r for r in runs if r.get('head_branch') == repo['default']]
        last = on_default[0] if on_default else None
        last_conc = (last.get('conclusion') if last and last.get('status') == 'completed'
                     else (last.get('status') if last else None))
        last_sha = (last.get('head_sha') or '') if last else ''

        rows.append({
            'workflow': wf.get('name'),
            'path': wf.get('path'),
            'state': wf.get('state'),
            'runs_read': len(runs),
            'runs_on_default': len(on_default),
            'ever_success': ever_success,
            'never_green': (len(completed) > 0 and not ever_success),
            'census': dict(sorted(census.items())),
            'unenumerated': unenumerated,
            'last_on_default': last_conc,
            'last_sha': last_sha[:7],
            'at_head': bool(sha and last_sha and last_sha == sha),
            'last_at': last.get('updated_at') if last else None,
            'last_url': last.get('html_url') if last else None,
            'read_error': err,
        })

    return {'repo': repo['name'], 'full': repo['full'], 'private': repo['private'],
            'archived': repo['archived'], 'readable': True, 'default': repo['default'],
            'head_sha': sha[:7], 'workflows': rows}


def board(result):
    """A committed markdown board. Short enough to read, specific enough to act on."""
    reps = result['repos']
    L = []
    A = L.append
    A('# CI history across the estate')
    A('')
    A('Generated by `scripts/ci_history_mine.py` in GitHub Actions. INFORMATIONAL: this')
    A('job exits 0 on every finding. Findings are here, never in the exit code.')
    A('')
    A('- surveyed at: `%s`' % result['generated_at'])
    A('- repositories: %d (%d readable, %d unreadable, %d private)'
      % (result['totals']['repos'], result['totals']['readable'],
         result['totals']['unreadable'], result['totals']['private']))
    A('- workflows: %d, runs read: %d' % (result['totals']['workflows'],
                                          result['totals']['runs_read']))
    A('- runs per workflow read: up to %d' % result['max_runs'])
    A('')

    ng = result['never_green']
    A('## Workflows that have NEVER concluded success (%d)' % len(ng))
    A('')
    if not ng:
        A('None.')
    else:
        A('| repo | workflow | runs read | census | last run |')
        A('|---|---|---|---|---|')
        for r in ng:
            A('| `%s` | %s | %d | %s | %s |'
              % (r['repo'], r['workflow'], r['runs_read'],
                 ', '.join('%s %d' % (k, v) for k, v in r['census'].items()),
                 r['last_at'] or '-'))
    A('')

    A('## Reds at head (%d) - the default branch is red on its current commit'
      % len(result['red_at_head']))
    A('')
    if not result['red_at_head']:
        A('None.')
    else:
        A('| repo | workflow | conclusion | sha | when |')
        A('|---|---|---|---|---|')
        for r in result['red_at_head']:
            A('| `%s` | %s | %s | `%s` | %s |'
              % (r['repo'], r['workflow'], r['last_on_default'], r['last_sha'],
                 r['last_at'] or '-'))
    A('')

    A('## Stale reds (%d) - last run failed on a commit that is no longer head'
      % len(result['red_stale']))
    A('')
    if not result['red_stale']:
        A('None.')
    else:
        A('| repo | workflow | conclusion | sha | when |')
        A('|---|---|---|---|---|')
        for r in result['red_stale']:
            A('| `%s` | %s | %s | `%s` | %s |'
              % (r['repo'], r['workflow'], r['last_on_default'], r['last_sha'],
                 r['last_at'] or '-'))
    A('')

    A('## Conclusions that `audit_estate.py` counts as nothing (%d runs)'
      % result['totals']['unenumerated'])
    A('')
    A('That reader files `success` as green, `failure`/`timed_out`/`startup_failure` as red,')
    A('and everything else as neither. These runs exist and are reported by it as absent.')
    A('')
    if not result['unenumerated_census']:
        A('None.')
    else:
        A('| conclusion | runs |')
        A('|---|---|')
        for k, v in result['unenumerated_census'].items():
            A('| `%s` | %d |' % (k, v))
    A('')

    if result['unreadable']:
        A('## Unreadable (%d)' % len(result['unreadable']))
        A('')
        A('A cross-repo Actions read the running token was not granted. Not a defect of')
        A('the repository - a fact about the token.')
        A('')
        for r in result['unreadable']:
            A('- `%s`: %s' % (r['repo'], r['detail']))
        A('')

    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--owner', default='Ventusltd')
    ap.add_argument('--max-runs', type=int, default=200)
    ap.add_argument('--out', default='ci-history.json')
    ap.add_argument('--board', default='')
    ap.add_argument('--workers', type=int, default=6)
    args = ap.parse_args()

    if not TOKEN:
        print('no token: running unauthenticated at 60 requests/hour, results will be partial',
              file=sys.stderr)

    rs = repos(args.owner)
    print('repositories: %d' % len(rs), file=sys.stderr)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        mined = list(ex.map(lambda r: mine(r, args.max_runs), rs))

    never_green, red_at_head, red_stale = [], [], []
    unenum = Counter()
    n_wf = n_runs = n_unenum = 0
    for m in mined:
        if not m['readable']:
            continue
        for w in m['workflows']:
            n_wf += 1
            n_runs += w['runs_read']
            n_unenum += w['unenumerated']
            for c, n in w['census'].items():
                if c not in COUNTED and c not in ('in_progress', 'queued', 'requested',
                                                  'waiting', 'pending'):
                    unenum[c] += n
            row = dict(w, repo=m['repo'], full=m['full'])
            if w['never_green']:
                never_green.append(row)
            if w['last_on_default'] in COUNTED_RED:
                (red_at_head if w['at_head'] else red_stale).append(row)

    result = {
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'owner': args.owner,
        'max_runs': args.max_runs,
        'totals': {
            'repos': len(mined),
            'readable': sum(1 for m in mined if m['readable']),
            'unreadable': sum(1 for m in mined if not m['readable']),
            'private': sum(1 for m in mined if m['private']),
            'workflows': n_wf,
            'runs_read': n_runs,
            'unenumerated': n_unenum,
        },
        'never_green': sorted(never_green, key=lambda r: (r['repo'], r['workflow'])),
        'red_at_head': sorted(red_at_head, key=lambda r: (r['repo'], r['workflow'])),
        'red_stale': sorted(red_stale, key=lambda r: (r['repo'], r['workflow'])),
        'unenumerated_census': dict(sorted(unenum.items(), key=lambda kv: -kv[1])),
        'unreadable': [{'repo': m['repo'], 'detail': m.get('detail')}
                       for m in mined if not m['readable']],
        'repos': mined,
    }

    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=1, sort_keys=False)
        f.write('\n')

    if args.board:
        os.makedirs(os.path.dirname(args.board) or '.', exist_ok=True)
        with open(args.board, 'w', encoding='utf-8', newline='\n') as f:
            f.write(board(result))

    t = result['totals']
    print('workflows %d over %d repos (%d unreadable); never green %d; '
          'red at head %d; stale red %d; runs the estate reader counts as nothing %d'
          % (t['workflows'], t['readable'], t['unreadable'], len(never_green),
             len(red_at_head), len(red_stale), t['unenumerated']), file=sys.stderr)

    # Informational. Always 0. See the module docstring before changing this.
    return 0


if __name__ == '__main__':
    sys.exit(main())
