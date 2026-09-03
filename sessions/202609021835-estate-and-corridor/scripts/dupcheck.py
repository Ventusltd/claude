import subprocess, collections, os, sys
sys.argv = ['dupcheck', '../clones']
import datapoints as DP
from concurrent.futures import ProcessPoolExecutor

ROOT = '../clones'
copies, meta = collections.Counter(), {}

def main():
    for r in DP.REPOS:
        ref = None
        for c in ('gh/main', 'gh/master'):
            if subprocess.run(['git', '-C', os.path.join(ROOT, r), 'rev-parse', '--verify', '-q', c],
                              capture_output=True).returncode == 0:
                ref = c
                break
        if not ref:
            continue
        out = subprocess.run(['git', '-C', os.path.join(ROOT, r), 'ls-tree', '-r', '-l', ref],
                             capture_output=True, text=True, errors='replace').stdout
        for line in out.splitlines():
            try:
                m, path = line.split('\t', 1)
                p = m.split()
                sha, size = p[2], (int(p[3]) if p[3].isdigit() else 0)
            except Exception:
                continue
            base = path.rsplit('/', 1)[-1]
            ext = ('.' + base.rsplit('.', 1)[1].lower()) if '.' in base[1:] else ''
            if ext not in DP.DATA:
                continue
            copies[sha] += 1
            meta.setdefault(sha, (r, sha, path, ext, size))

    jobs = [meta[s] for s in copies]
    jobs.sort(key=lambda j: -j[4])
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(DP.work, jobs))
    per = {j[1]: r['dp'] for j, r in zip(jobs, res)}
    uniq = sum(per.values())
    allc = sum(per[s] * copies[s] for s in per)
    print('datapoints, unique content only : %16s' % f'{uniq:,}')
    print('datapoints, counting every copy : %16s' % f'{allc:,}')
    print('inflation from duplicate copies : %16s   (x%.2f)' % (f'{allc - uniq:,}', allc / uniq))
    worst = sorted(copies.items(), key=lambda kv: -per.get(kv[0], 0) * (kv[1] - 1))[:5]
    print('\nmost-duplicated content by datapoint impact:')
    for sha, c in worst:
        if c > 1:
            print('   %3d copies  x %12s dp  = %14s inflated' %
                  (c, f'{per[sha]:,}', f'{per[sha] * (c - 1):,}'))

if __name__ == '__main__':
    main()
