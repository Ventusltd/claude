"""audit_estate.py - one pass over every repository the account owns: CI, then git.

WHY THIS EXISTS

The two questions asked at the start of a session - "what is red?" and "what is
uncommitted?" - were answered by hand, repo by repo, and answered differently each time.
Each hand answer cost six tool calls and got one thing wrong: a feature branch counted as
a red, a working tree counted as a state, a repo missing from the sweep because the sweep
enumerated disk instead of the account.

So it is one script.

    python scripts/audit_estate.py                 # human report
    python scripts/audit_estate.py --json out.json # machine-readable too

THE DISCIPLINES IT CARRIES, so they are not remembered

- Repos come from the GitHub API, never from disk. One session scanned 15 when the
  account had 30.
- CI is filtered to each repo's DEFAULT BRANCH. A feature branch fails on its first run
  and that is not a defect.
- A red names the failing JOB and STEP, read off the runner's own jobs API - not guessed
  from a workflow file, and not reproduced locally first.
- A dirty tree is UNMEASURABLE, never red and never green. It is reported as its own
  third state, with the paths that make it dirty, so another lane's work in progress is
  never filed as a defect.
- git-clean is not byte-clean: the CRLF count is reported separately, because digests
  taken from a working tree lie.
- The token is read once, held in one variable, never printed and never written down.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

GITHUB_DIR = r'C:\Users\vikra\OneDrive\Documents\GitHub'
API = 'https://api.github.com/'


def token():
    p = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
                       capture_output=True, text=True, cwd=GITHUB_DIR)
    for line in p.stdout.splitlines():
        if line.startswith('password='):
            return line[9:]
    return None


TOKEN = token()


def api(path, retries=2):
    req = urllib.request.Request(API + path, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'ventus-estate-audit',
        **({'Authorization': 'Bearer ' + TOKEN} if TOKEN else {}),
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as exc:
            if attempt == retries:
                return {'_error': str(exc)[:120]}
            time.sleep(1.5)


def git(repo, *args, timeout=60):
    try:
        p = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                           timeout=timeout)
        # rstrip only: a leading space is DATA in `status --porcelain` (' M path'),
        # and stripping it shifted every first-line path by one character.
        return p.stdout.rstrip() if p.returncode == 0 else ''
    except Exception:
        return ''


def repos():
    """Every repo the account can see, newest push first. From the API, never from disk."""
    out, page = [], 1
    while True:
        got = api('user/repos?per_page=100&affiliation=owner,organization_member'
                  '&sort=pushed&page=%d' % page)
        if not isinstance(got, list) or not got:
            break
        out += [{'name': r['name'], 'full': r['full_name'], 'default': r['default_branch'],
                 'pushed': r['pushed_at'], 'private': r['private']} for r in got]
        if len(got) < 100:
            break
        page += 1
    return out


def ci_for(repo):
    """Latest run per workflow ON THE DEFAULT BRANCH. Reds carry their failing steps."""
    name, branch = repo['name'], repo['default']
    runs = api('repos/%s/actions/runs?branch=%s&per_page=60' % (repo['full'], branch))
    if isinstance(runs, dict) and runs.get('_error'):
        return {'repo': name, 'state': 'unreachable', 'detail': runs['_error']}
    items = runs.get('workflow_runs', []) if isinstance(runs, dict) else []
    items = [r for r in items if r.get('head_branch') == branch]
    if not items:
        return {'repo': name, 'state': 'no-runs', 'workflows': [], 'reds': []}

    latest = {}
    for r in items:                      # API returns newest first
        latest.setdefault(r['name'], r)

    reds, waiting, green = [], [], []
    for wf, r in latest.items():
        row = {'workflow': wf, 'conclusion': r.get('conclusion'), 'status': r.get('status'),
               'sha': (r.get('head_sha') or '')[:7], 'run_id': r.get('id'),
               'at': r.get('updated_at')}
        if r.get('status') != 'completed':
            waiting.append(row)
        elif r.get('conclusion') == 'success':
            green.append(row)
        elif r.get('conclusion') in ('failure', 'timed_out', 'startup_failure'):
            jobs = api('repos/%s/actions/runs/%s/jobs' % (repo['full'], r['id']))
            failed = []
            for j in (jobs.get('jobs', []) if isinstance(jobs, dict) else []):
                if j.get('conclusion') in ('failure', 'timed_out'):
                    steps = [s['name'] for s in j.get('steps', [])
                             if s.get('conclusion') == 'failure']
                    failed.append({'job': j.get('name'), 'steps': steps,
                                   'url': j.get('html_url')})
            row['failed_jobs'] = failed
            reds.append(row)
        # cancelled / skipped / neutral are neither, and are not counted as either

    head = items[0]
    head_sha = head.get('head_sha') or ''
    for r in reds:
        r['at_head'] = head_sha.startswith(r['sha'])
    at_head = [r for r in reds if r['at_head']]
    stale = [r for r in reds if not r['at_head']]
    # A workflow whose LAST run failed weeks ago, on a commit that is no longer the head,
    # does not make today's head red. Counting the two together is a wrong denominator,
    # and a wrong denominator gets quoted rather than checked.
    return {'repo': name,
            'state': 'red' if at_head else ('stale-red' if stale else ('green' if green else 'none')),
            'reds_at_head': len(at_head), 'reds_stale': len(stale),
            'branch': branch, 'head_sha': (head.get('head_sha') or '')[:7],
            'workflows': len(latest), 'green': len(green), 'waiting': len(waiting),
            'reds': reds}


def git_for(repo):
    """Local clone state. A dirty tree is UNMEASURABLE, not a defect and not a state."""
    path = os.path.join(GITHUB_DIR, repo['name'])
    if not os.path.isdir(path):
        return {'repo': repo['name'], 'present': False}
    git(path, 'fetch', '--quiet', 'origin', timeout=120)
    branch = git(path, 'rev-parse', '--abbrev-ref', 'HEAD')
    upstream = git(path, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}')
    default = repo['default']
    counts = git(path, 'rev-list', '--left-right', '--count', 'origin/%s...HEAD' % default)
    behind, ahead = (counts.split() + ['?', '?'])[:2]
    porcelain = [l for l in git(path, 'status', '--porcelain').splitlines() if l]
    modified = [l for l in porcelain if not l.startswith('??')]
    untracked = [l for l in porcelain if l.startswith('??')]
    eol = git(path, 'ls-files', '--eol')
    crlf = sum(1 for l in eol.splitlines() if 'w/crlf' in l)
    worktrees = max(0, git(path, 'worktree', 'list').count('\n'))
    return {'repo': repo['name'], 'present': True, 'branch': branch,
            'upstream': upstream or None, 'default': default,
            'ahead': ahead, 'behind': behind,
            'modified': len(modified), 'untracked': len(untracked),
            'modified_paths': [l[3:] for l in modified][:12],
            'untracked_paths': [l[3:] for l in untracked][:12],
            'crlf_files': crlf, 'worktrees': worktrees,
            'local_head': git(path, 'rev-parse', 'HEAD')[:7],
            'remote_head': git(path, 'rev-parse', 'origin/%s' % default)[:7],
            'measurable': not modified}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', help='also write the full result here')
    ap.add_argument('--only', nargs='*', help='limit to these repo names')
    args = ap.parse_args()

    t0 = time.time()
    all_repos = repos()
    if args.only:
        all_repos = [r for r in all_repos if r['name'] in args.only]
    print('%d repositories from the API (auth: %s)' % (all_repos and len(all_repos) or 0,
                                                       'yes' if TOKEN else 'NO - 60/hr'))

    with ThreadPoolExecutor(max_workers=12) as pool:
        ci = list(pool.map(ci_for, all_repos))
    local = [r for r in all_repos if os.path.isdir(os.path.join(GITHUB_DIR, r['name']))]
    with ThreadPoolExecutor(max_workers=8) as pool:
        gits = list(pool.map(git_for, local))

    print('\n== CI on default branches ==')
    reds = [c for c in ci if c.get('state') == 'red']
    order = {'red': 0, 'stale-red': 1, 'green': 2}
    for c in sorted(ci, key=lambda x: (order.get(x.get('state'), 3), x['repo'])):
        st = c.get('state')
        if st in ('red', 'stale-red'):
            print('  %-9s %-28s %s  (%d workflows, %d green, %d red at head, %d stale red)' %
                  ('RED@HEAD' if st == 'red' else 'stale-red', c['repo'], c.get('head_sha', ''),
                   c.get('workflows', 0), c.get('green', 0),
                   c.get('reds_at_head', 0), c.get('reds_stale', 0)))
            for r in sorted(c['reds'], key=lambda x: not x['at_head']):
                print('          %-6s %-42s %s  %s' %
                      ('AT HEAD' if r['at_head'] else 'stale', r['workflow'][:42], r['sha'],
                       (r.get('at') or '')[:16]))
                for fj in r.get('failed_jobs', []):
                    print('            job %-28s step: %s' %
                          (str(fj['job'])[:28], '; '.join(fj['steps'][:3]) or '(none named)'))
        elif st == 'green':
            print('  green %-28s %d workflows, %d waiting' %
                  (c['repo'], c.get('workflows', 0), c.get('waiting', 0)))
        else:
            print('  %-5s %-28s %s' % (st, c['repo'], c.get('detail', '')))

    print('\n== git ==')
    for g in sorted(gits, key=lambda x: x['repo']):
        flags = []
        if g['branch'] != g['default']:
            flags.append('ON BRANCH %s' % g['branch'])
        if g['ahead'] not in ('0', '?'):
            flags.append('%s ahead' % g['ahead'])
        if g['behind'] not in ('0', '?'):
            flags.append('%s behind' % g['behind'])
        if g['modified']:
            flags.append('UNMEASURABLE: %d modified' % g['modified'])
        if g['untracked']:
            flags.append('%d untracked' % g['untracked'])
        print('  %-28s %s  crlf %-5d wt %-3d %s' %
              (g['repo'], g['local_head'], g['crlf_files'], g['worktrees'],
               ' | '.join(flags) or 'clean, at origin'))
        for p in g['modified_paths']:
            print('        M  %s' % p)

    print('\n%d red, %d clean-and-measurable of %d local clones, %.1fs'
          % (len(reds), sum(1 for g in gits if g['measurable'] and g['ahead'] == '0'),
             len(gits), time.time() - t0))

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as fh:
            json.dump({'measured_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                       'ci': ci, 'git': gits}, fh, indent=1)
        print('wrote %s' % args.json)


if __name__ == '__main__':
    main()
