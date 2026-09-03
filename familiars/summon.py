"""Familiars - small local workers that do the donkey running on this machine.

WHY THIS EXISTS

An agent that checks CI, then the live site, then five repositories, then a ceiling,
spends its thinking on clerical work and arrives at the interesting question already
tired. Every one of those checks is a script. None of them needs judgement.

So they are summoned instead: named workers, run in PARALLEL across this machine's
twenty cores, each returning one small fact. The caller reads a single merged answer
and spends what it saved on the part that actually needs a mind.

    python familiars/summon.py                 # all of them
    python familiars/summon.py ci live         # only these
    python familiars/summon.py --json          # machine-readable

MEASURED, NOT ASSUMED

Every familiar returns what it actually observed, and says so when it could not look.
A familiar that cannot reach its subject returns an error string - never a cheerful
default, because a false green here would be worse than no familiar at all.

WINDOWS NOTE

multiprocessing on Windows re-imports this file in each worker, so the pool lives
behind a __main__ guard and every worker is a module-level function. Heredoc-piped
code crashes the pool here; this is a real file for that reason.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ProcessPoolExecutor, as_completed

GITHUB = r'C:\Users\vikra\OneDrive\Documents\GitHub'
REPOS = ['gridatlas', 'globalgrid2050', 'pipelinenews', 'claude', 'cvaa',
         'data-grid-gb', 'data-gridatlas']
CEILINGS = {'sld-sandbox': 368640, 'substation-intelligence': 400000}


def _run(cmd, cwd=None, timeout=90):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, shell=False)
        return p.stdout.strip()
    except Exception as exc:
        return 'ERR ' + str(exc)[:80]


def _token():
    out = _run(['git', 'credential', 'fill'], cwd=GITHUB)
    for line in out.splitlines():
        if line.startswith('password='):
            return line[9:]
    return None


def _api(path, token, raw=False):
    req = urllib.request.Request('https://api.github.com/' + path)
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    req.add_header('Accept', 'application/vnd.github+json')
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if raw else json.load(r)


def _get(url, timeout=40):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read()
    except Exception as exc:
        return 0, str(exc).encode()


# ── the familiars ────────────────────────────────────────────────────────────

def fam_repo():
    """Working-tree truth for every repo: dirty, ahead, behind."""
    out = {}
    for name in REPOS:
        path = os.path.join(GITHUB, name)
        if not os.path.isdir(os.path.join(path, '.git')):
            continue
        _run(['git', 'fetch', '-q', 'origin'], cwd=path, timeout=120)
        head = _run(['git', 'rev-parse', '--short', 'HEAD'], cwd=path)
        dirty = _run(['git', 'status', '--porcelain'], cwd=path)
        ahead = _run(['git', 'rev-list', '--count', 'origin/main..HEAD'], cwd=path)
        behind = _run(['git', 'rev-list', '--count', 'HEAD..origin/main'], cwd=path)
        out[name] = {
            'head': head,
            'dirty': len([l for l in dirty.splitlines() if l.strip()]),
            'ahead': ahead, 'behind': behind,
        }
    return out


def fam_ci():
    """Latest conclusion per repo on its own default branch."""
    token = _token()
    out = {}
    for name in REPOS:
        try:
            d = _api('repos/Ventusltd/%s/actions/runs?branch=main&per_page=4' % name, token)
            runs = d.get('workflow_runs', [])
            if not runs:
                out[name] = 'no runs'
                continue
            sha = runs[0]['head_sha'][:7]
            same = [r for r in runs if r['head_sha'].startswith(sha)]
            bad = [r['name'][:28] for r in same if r['conclusion'] == 'failure']
            out[name] = {'sha': sha,
                         'state': 'RED' if bad else 'green',
                         'failing': bad}
        except Exception as exc:
            out[name] = 'ERR ' + str(exc)[:60]
    return out


def fam_live():
    """What the public actually receives right now."""
    out = {}
    st, body = _get('https://ventusltd.github.io/gridatlas/atlas/current.json')
    if st == 200:
        try:
            j = json.loads(body)
            out['gridatlas_generation'] = j.get('generation')
        except Exception:
            out['gridatlas_generation'] = 'unparseable'
    else:
        out['gridatlas_generation'] = 'HTTP %s' % st
    for label, url in [
        ('world', 'https://ventusltd.github.io/gridatlas/atlas/world/'),
        ('atlas', 'https://ventusltd.github.io/gridatlas/atlas/'),
        ('pipelinenews', 'https://globalgrid2050.com/pipelinenews_intelligence/202609031308/'),
        ('homepage', 'https://globalgrid2050.com/'),
    ]:
        st, _ = _get(url)
        out[label] = st
    return out


def fam_ceiling():
    """Cartridge size against its ceiling, in CHARACTERS - bytes are a different number."""
    out = {}
    carts = os.path.join(GITHUB, 'gridatlas', 'atlas', 'cartridges')
    if not os.path.isdir(carts):
        return {'error': 'no cartridges directory'}
    newest = {}
    for fn in os.listdir(carts):
        if not fn.endswith('.js'):
            continue
        for key in CEILINGS:
            if key in fn:
                if key not in newest or fn > newest[key]:
                    newest[key] = fn
    for key, fn in newest.items():
        with open(os.path.join(carts, fn), encoding='utf-8') as fh:
            text = fh.read()
        out[key] = {'file': fn, 'chars': len(text), 'bytes': len(text.encode('utf-8')),
                    'ceiling': CEILINGS[key], 'headroom': CEILINGS[key] - len(text)}
    return out


def fam_proof():
    """The STEP the runner runs - not a proof chosen by hand."""
    ga = os.path.join(GITHUB, 'gridatlas')
    runner = os.path.join(ga, 'tools', 'proofs', 'run-current.mjs')
    if not os.path.isfile(runner):
        return {'error': 'run-current.mjs missing'}
    t0 = time.time()
    try:
        p = subprocess.run(['node', runner], cwd=ga, capture_output=True,
                           text=True, timeout=900)
    except Exception as exc:
        return {'error': str(exc)[:100]}
    tail = [l for l in p.stdout.splitlines() if 'checks passed' in l or '[FAIL]' in l]
    return {'rc': p.returncode, 'seconds': round(time.time() - t0, 1),
            'lines': tail[-6:]}


FAMILIARS = {
    'repo': fam_repo,
    'ci': fam_ci,
    'live': fam_live,
    'ceiling': fam_ceiling,
    'proof': fam_proof,
}


def _call(name):
    try:
        return name, FAMILIARS[name]()
    except Exception as exc:
        return name, {'error': str(exc)[:140]}


def main(argv):
    as_json = '--json' in argv
    wanted = [a for a in argv if a in FAMILIARS] or list(FAMILIARS)
    t0 = time.time()
    results = {}
    with ProcessPoolExecutor(max_workers=min(len(wanted), os.cpu_count() or 4)) as pool:
        futures = [pool.submit(_call, n) for n in wanted]
        for fut in as_completed(futures):
            name, value = fut.result()
            results[name] = value
    results['_summoned'] = {'familiars': len(wanted),
                            'seconds': round(time.time() - t0, 1),
                            'cores': os.cpu_count()}
    if as_json:
        print(json.dumps(results, indent=1))
        return 0

    s = results
    print('summoned %d familiars in %ss on %d cores'
          % (s['_summoned']['familiars'], s['_summoned']['seconds'], s['_summoned']['cores']))
    if 'live' in s:
        L = s['live']
        print('  live      gridatlas %s | world %s atlas %s pipelinenews %s homepage %s'
              % (L.get('gridatlas_generation'), L.get('world'), L.get('atlas'),
                 L.get('pipelinenews'), L.get('homepage')))
    if 'ci' in s:
        red = [k for k, v in s['ci'].items() if isinstance(v, dict) and v.get('state') == 'RED']
        print('  ci        %d red: %s' % (len(red), ', '.join(red) or 'none'))
        for k in red:
            print('              %s %s -> %s' % (k, s['ci'][k]['sha'],
                                                 '; '.join(s['ci'][k]['failing'])))
    if 'repo' in s:
        busy = ['%s(d%s a%s b%s)' % (k, v['dirty'], v['ahead'], v['behind'])
                for k, v in s['repo'].items()
                if isinstance(v, dict) and (v['dirty'] or v['ahead'] != '0' or v['behind'] != '0')]
        print('  repos     %s' % (', '.join(busy) or 'all clean and level'))
    if 'ceiling' in s:
        for k, v in s['ceiling'].items():
            if isinstance(v, dict):
                print('  ceiling   %-26s %d/%d chars, %d left'
                      % (k, v['chars'], v['ceiling'], v['headroom']))
    if 'proof' in s:
        P = s['proof']
        print('  proof     rc=%s in %ss' % (P.get('rc'), P.get('seconds')))
        for line in P.get('lines', []):
            print('              %s' % line.strip())
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
