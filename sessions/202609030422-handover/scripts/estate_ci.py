"""Estate CI status, from the API, filtered to each repo's own default branch.

Only possible cheaply since the 60/hour ceiling turned out to be fictional. Enumerates repos
from the API rather than from disk, because a disk scan has under-counted this estate twice.
"""
import json
import subprocess
import sys
import urllib.request

token = subprocess.run(
    ['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
    capture_output=True, text=True).stdout
token = [l[9:] for l in token.splitlines() if l.startswith('password=')]
token = token[0] if token else None
if not token:
    print('no credential'); sys.exit(1)


def api(path):
    req = urllib.request.Request('https://api.github.com/' + path)
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header('Accept', 'application/vnd.github+json')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


repos = []
page = 1
while True:
    batch = api('user/repos?per_page=100&affiliation=owner&page=%d' % page)
    if not batch:
        break
    repos.extend(batch)
    page += 1

print('repositories on the account: %d' % len(repos))
print()
print('%-46s %-8s %-10s %-9s %s' % ('repo', 'branch', 'CI', 'age', 'last run'))
print('-' * 104)

green = red = none = 0
reds = []
for r in sorted(repos, key=lambda x: x['name']):
    name = r['name']
    branch = r.get('default_branch') or 'main'
    try:
        runs = api('repos/%s/actions/runs?branch=%s&per_page=1' % (r['full_name'], branch))
    except Exception as exc:
        print('%-46s %-8s %-10s %-9s %s' % (name[:46], branch[:8], 'ERR', '-', str(exc)[:28]))
        continue
    wr = runs.get('workflow_runs') or []
    if not wr:
        none += 1
        print('%-46s %-8s %-10s %-9s %s' % (name[:46], branch[:8], '-', '-', 'no workflow runs'))
        continue
    run = wr[0]
    concl = run.get('conclusion') or run.get('status') or '?'
    if concl == 'success':
        green += 1
    elif concl in ('failure', 'startup_failure', 'timed_out'):
        red += 1
        reds.append((name, run.get('name', '')[:40], run.get('created_at', '')))
    print('%-46s %-8s %-10s %-9s %s' % (
        name[:46], branch[:8], concl[:10], run.get('created_at', '')[5:16].replace('T', ' '),
        (run.get('name') or '')[:34]))

print()
print('green %d   red %d   no runs %d   total %d' % (green, red, none, len(repos)))
if reds:
    print()
    print('RED on default branch:')
    for n, w, t in reds:
        print('  %-40s %-40s %s' % (n, w, t))
