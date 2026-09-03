"""When did the datapoints actually arrive?

For every unique data blob, find the date its path first appeared in history,
then bucket datapoints by month. Answers whether growth is steady or lumpy.
"""
import subprocess, collections, os, io, sys, json
import pyarrow.parquet as pq
sys.argv = ['growth', '../clones']
import datapoints as DP

ROOT  = '../clones'
REPOS = DP.REPOS
TEXT  = DP.DATA


def first_added(repo, ref):
    """path -> earliest date the path was added."""
    out = subprocess.run(
        ['git', '-C', os.path.join(ROOT, repo), 'log', ref, '--reverse',
         '--diff-filter=A', '--name-only', '--date=short', '--format=%x01%ad'],
        capture_output=True, text=True, errors='replace').stdout
    date, m = None, {}
    for line in out.splitlines():
        if line.startswith('\x01'):
            date = line[1:].strip()
        elif line.strip() and date:
            m.setdefault(line.strip(), date)
    return m


def blob_points(repo, sha, path):
    ext = ('.' + path.rsplit('.', 1)[1].lower()) if '.' in path.rsplit('/', 1)[-1][1:] else ''
    try:
        buf = subprocess.run(['git', '-C', os.path.join(ROOT, repo), 'cat-file', 'blob', sha],
                             capture_output=True, timeout=600).stdout
    except Exception:
        return 0
    if ext in ('.csv', '.tsv'):
        return DP.count_csv(buf, b'\t' if ext == '.tsv' else b',')[0]
    if ext == '.parquet':
        try:
            f = pq.ParquetFile(io.BytesIO(buf))
            return f.metadata.num_rows * f.metadata.num_columns
        except Exception:
            return 0
    return DP.count_json(buf)


def main():
    seen = {}
    for r in REPOS:
        ref = None
        for c in ('gh/main', 'gh/master'):
            if subprocess.run(['git', '-C', os.path.join(ROOT, r), 'rev-parse', '--verify', '-q', c],
                              capture_output=True).returncode == 0:
                ref = c
                break
        if not ref:
            continue
        added = first_added(r, ref)
        out = subprocess.run(['git', '-C', os.path.join(ROOT, r), 'ls-tree', '-r', ref],
                             capture_output=True, text=True, errors='replace').stdout
        for line in out.splitlines():
            try:
                meta, path = line.split('\t', 1)
                sha = meta.split()[2]
            except Exception:
                continue
            base = path.rsplit('/', 1)[-1]
            ext = ('.' + base.rsplit('.', 1)[1].lower()) if '.' in base[1:] else ''
            if ext not in TEXT and ext != '.parquet':
                continue
            d = added.get(path, '9999-99-99')
            if sha not in seen or d < seen[sha][2]:
                seen[sha] = (r, path, d)

    by_month = collections.Counter()
    files_month = collections.Counter()
    for sha, (r, path, d) in seen.items():
        n = blob_points(r, sha, path)
        by_month[d[:7]] += n
        files_month[d[:7]] += 1

    total = sum(by_month.values())
    print('%-9s %16s %16s %8s' % ('month', 'datapoints', 'cumulative', 'files'))
    print('-' * 54)
    run = 0
    for m in sorted(by_month):
        run += by_month[m]
        print('%-9s %16s %16s %8d' % (m, f'{by_month[m]:,}', f'{run:,}', files_month[m]))
    print('-' * 54)
    print('%-9s %16s' % ('TOTAL', f'{total:,}'))
    json.dump({'by_month': dict(by_month), 'files_month': dict(files_month), 'total': total},
              open('growth.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
