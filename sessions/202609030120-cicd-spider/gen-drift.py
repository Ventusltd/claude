"""Split monotonic-utc-generations failures by KIND and by SIGN.

The rule asserts two things - ordering, and that a stamp sits within 15 minutes
of its real UTC commit time - and only one direction of the second is a defect.

A stamp BEHIND its commit can be innocent: an archive commit filing
sessions/202609021813-.../ is correctly titled with that session's generation.
A stamp AHEAD of its own commit cannot be innocent, because `date -u` does not
return the future. It means the generation was chosen when the work began and
the commit landed hours later - which is verbatim what the rule forbids:
"generations are read from date -u at commit time, never chosen."

Not a clock or timezone fault: BST-vs-UTC would give a constant 60-minute
offset, and the observed spread is 16 to 253 minutes. The remedy is a habit -
compute the stamp in the same command as the commit - not a tool.
"""
import subprocess, re, datetime, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
GH = "C:/Users/vikra/OneDrive/Documents/GitHub"
LIMIT = int(os.environ.get('GEN_DRIFT_LIMIT', '400'))
repos = sys.argv[1:] or ['pipelinenews','gridatlas','globalgrid2050','claude','cvaa','data-grid-gb']
print('%-22s %8s %7s %7s %8s   %s' % ('repo','stamped','AHEAD','behind','worst+','verdict'))
for repo in repos:
    path = os.path.join(GH, repo)
    if not os.path.isdir(os.path.join(path, '.git')): continue
    out = subprocess.run(['git','-C',path,'log','-%d'%LIMIT,'--format=%H%x09%aI%x09%s'],
                         capture_output=True, text=True, errors='replace').stdout
    ahead, behind, tot = [], [], 0
    for line in out.splitlines():
        p = line.split('\t')
        if len(p) < 3: continue
        m = re.match(r'^(\d{12})', p[2])
        if not m: continue
        tot += 1
        try:
            gen = datetime.datetime.strptime(m.group(1), '%Y%m%d%H%M').replace(tzinfo=datetime.timezone.utc)
            commit = datetime.datetime.fromisoformat(p[1]).astimezone(datetime.timezone.utc)
        except Exception:
            continue
        d = (gen - commit).total_seconds() / 60
        if d > 15: ahead.append((d, p[0][:7], p[2][:60]))
        elif d < -15: behind.append((-d, p[0][:7], p[2][:60]))
    if not tot: continue
    worst = max(a[0] for a in ahead) if ahead else 0
    verdict = ('%d chosen in advance' % len(ahead)) if ahead else 'clean'
    print('%-22s %8d %7d %7d %8.0f   %s' % (repo, tot, len(ahead), len(behind), worst, verdict))
    if '-v' in os.environ.get('GEN_DRIFT_OPTS',''):
        for d, sha, subj in sorted(ahead, reverse=True)[:5]:
            print('      +%4.0f min  %s  %s' % (d, sha, subj))
print('\nAHEAD is the defect. behind may be an archive commit correctly titled with')
print('the generation of the session it files. Remedy: compute the stamp in the')
print('same command as the commit - date -u +%Y%m%d%H%M - never at task start.')
