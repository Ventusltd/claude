import subprocess, os, sys, io, json, collections
sys.argv = ['extra', '../clones']
import datapoints as DP
import pyarrow.parquet as pq

ROOT = '../extra'
DATA = DP.DATA | {'.parquet'}
CODE = {'.py','.mjs','.js','.cjs','.ts','.tsx','.jsx','.sh','.bash','.ps1','.awk','.sql',
        '.rb','.go','.rs','.java','.c','.h','.cpp','.html','.htm','.svg','.css','.scss',
        '.xml','.yml','.yaml','.toml','.ini','.cfg'}

repos = sorted(d[:-4] for d in os.listdir(ROOT) if d.endswith('.git'))
tot_dp = tot_loc = tot_files = 0
rows = []

for r in repos:
    g = os.path.join(ROOT, r + '.git')
    ref = subprocess.run(['git', '-C', g, 'for-each-ref', '--format=%(refname:short)', 'refs/heads'],
                         capture_output=True, text=True).stdout.split('\n')[0].strip()
    if not ref:
        rows.append((r, 0, 0, 0)); continue

    # lines of code / markup / config
    out = subprocess.run(['git', '-C', g, 'grep', '-I', '-c', '', ref, '--', '.'],
                         capture_output=True, text=True, errors='replace').stdout
    loc = 0
    prefix = ref + ':'
    for line in out.splitlines():
        if not line.startswith(prefix):
            continue
        path, _, n = line[len(prefix):].rpartition(':')
        if not n.isdigit():
            continue
        base = path.rsplit('/', 1)[-1]
        ext = ('.' + base.rsplit('.', 1)[1].lower()) if '.' in base[1:] else ''
        if ext in CODE:
            loc += int(n)

    # datapoints
    tree = subprocess.run(['git', '-C', g, 'ls-tree', '-r', ref],
                          capture_output=True, text=True, errors='replace').stdout
    dp = nf = 0
    for line in tree.splitlines():
        try:
            meta, path = line.split('\t', 1)
            sha = meta.split()[2]
        except Exception:
            continue
        base = path.rsplit('/', 1)[-1]
        ext = ('.' + base.rsplit('.', 1)[1].lower()) if '.' in base[1:] else ''
        if ext not in DATA:
            continue
        nf += 1
        try:
            buf = subprocess.run(['git', '-C', g, 'cat-file', 'blob', sha],
                                 capture_output=True, timeout=300).stdout
        except Exception:
            continue
        if ext in ('.csv', '.tsv'):
            dp += DP.count_csv(buf, b'\t' if ext == '.tsv' else b',')[0]
        elif ext == '.parquet':
            try:
                f = pq.ParquetFile(io.BytesIO(buf))
                dp += f.metadata.num_rows * f.metadata.num_columns
            except Exception:
                pass
        else:
            dp += DP.count_json(buf)
    rows.append((r, loc, dp, nf))
    tot_loc += loc; tot_dp += dp; tot_files += nf

print('%-52s %10s %14s %7s' % ('repo', 'code lines', 'datapoints', 'files'))
print('-' * 88)
for r, loc, dp, nf in sorted(rows, key=lambda x: -x[2]):
    print('%-52s %10s %14s %7d' % (r[:52], f'{loc:,}', f'{dp:,}', nf))
print('-' * 88)
print('%-52s %10s %14s %7d' % ('TOTAL (14 repos, fork excluded)',
                               f'{tot_loc:,}', f'{tot_dp:,}', tot_files))
json.dump({'loc': tot_loc, 'datapoints': tot_dp, 'rows': rows}, open('extra.json', 'w'), indent=1)
