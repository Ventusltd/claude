"""Classify generation-stamp drift in a repo: genuine error vs session-archive convention.

monotonic-utc-generations flags any commit whose subject generation is more than 15 minutes from
its real UTC commit time. In an ARCHIVE repository that is ambiguous: a commit that files
sessions/202609021813-.../ is correctly titled with the session's generation, not the moment the
file landed. Those are a naming convention, not a clock error. A stamp AHEAD of its own commit is
never a convention - date -u cannot return the future.
"""
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

repo = Path(sys.argv[1])
sessions = set()
sdir = repo / 'sessions'
if sdir.is_dir():
    for d in sdir.iterdir():
        m = re.match(r'^(\d{12})', d.name)
        if m:
            sessions.add(m.group(1))

log = subprocess.run(['git', 'log', '--format=%H|%aI|%s', '-400'], cwd=repo,
                     capture_output=True, text=True).stdout

def to_min(stamp):
    return datetime(int(stamp[0:4]), int(stamp[4:6]), int(stamp[6:8]),
                    int(stamp[8:10]), int(stamp[10:12]), tzinfo=timezone.utc).timestamp() / 60

ahead, archive, behind, ok, unstamped = [], [], [], 0, 0
for line in log.splitlines():
    parts = line.split('|', 2)
    if len(parts) < 3:
        continue
    sha, when, subj = parts
    m = re.match(r'^(\d{12})', subj)
    if not m:
        unstamped += 1
        continue
    gen = m.group(1)
    utc = datetime.fromisoformat(when).astimezone(timezone.utc)
    delta = to_min(gen) - utc.timestamp() / 60      # positive = stamp is in the FUTURE
    if abs(delta) <= 15:
        ok += 1
    elif delta > 15:
        ahead.append((sha[:7], gen, int(delta), subj[:58]))
    elif gen in sessions:
        archive.append((sha[:7], gen, int(-delta), subj[:58]))
    else:
        behind.append((sha[:7], gen, int(-delta), subj[:58]))

print('repo: %s   commits examined: %d' % (repo.name, ok + len(ahead) + len(archive) + len(behind)))
print('  within 15 min (clean):            %d' % ok)
print('  stamp AHEAD of commit (ERROR):    %d   <- date -u cannot return the future' % len(ahead))
print('  behind, names a session dir:      %d   <- archive convention, not a clock error' % len(archive))
print('  behind, no session dir:           %d   <- unexplained' % len(behind))
print('  no generation stamp:              %d' % unstamped)

for label, rows in (('STAMPED AHEAD OF ITS OWN COMMIT', ahead),
                    ('BEHIND, UNEXPLAINED', behind),
                    ('BEHIND, FILES THAT SESSION', archive)):
    if not rows:
        continue
    print()
    print('%s:' % label)
    for sha, gen, d, subj in rows[:10]:
        print('  %s %s %5d min  %s' % (sha, gen, d, subj))
    if len(rows) > 10:
        print('  ... and %d more' % (len(rows) - 10))
