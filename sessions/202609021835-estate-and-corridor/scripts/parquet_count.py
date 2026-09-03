"""Count datapoints held in parquet, which the text-based count could not see.

One datapoint = one cell = rows x columns, read from the parquet footer
metadata (no full decompression). Counted once per unique git blob.
"""
import subprocess, collections, os, io, sys, json
import pyarrow.parquet as pq

ROOT  = '../clones'
REPOS = ["chatgpt-audits","companies","cvaa","data-centres-gb",
         "data-federation-map-for-globalgrid2050-all-repos","data-gb-electricity",
         "data-grid-gb","data-gridatlas","data-interconnectors","gb-electricity-ui",
         "globalgrid2050","grid-distance-maths","gridatlas","pipelinenews","spiders"]

seen, jobs, copies = set(), [], 0
for r in REPOS:
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
            meta, path = line.split('\t', 1)
            p = meta.split()
            sha, size = p[2], (int(p[3]) if p[3].isdigit() else 0)
        except Exception:
            continue
        if not path.lower().endswith('.parquet'):
            continue
        copies += 1
        if sha in seen:
            continue
        seen.add(sha)
        jobs.append((r, sha, path, size))

rows = cells = ok = bad = 0
cols_seen = collections.Counter()
byrepo = collections.Counter()
for r, sha, path, size in jobs:
    try:
        blob = subprocess.run(['git', '-C', os.path.join(ROOT, r), 'cat-file', 'blob', sha],
                              capture_output=True, timeout=300).stdout
        f = pq.ParquetFile(io.BytesIO(blob))
        nr = f.metadata.num_rows
        nc = f.metadata.num_columns
        rows += nr
        cells += nr * nc
        cols_seen[nc] += 1
        byrepo[r] += nr * nc
        ok += 1
    except Exception:
        bad += 1

print('unique parquet blobs : %s   (of %s copies on disk)' % (f'{len(jobs):,}', f'{copies:,}'))
print('read successfully    : %s   unreadable %d' % (f'{ok:,}', bad))
print('rows                 : %s' % f'{rows:,}')
print('cells (datapoints)   : %s' % f'{cells:,}')
print('typical column counts: %s' % ', '.join(f'{c} cols x{n}' for c, n in cols_seen.most_common(5)))
print()
print('by repository (ordinal order withheld):')
for r, n in byrepo.most_common():
    print('   %-52s %14s' % (r, f'{n:,}'))
json.dump({'unique_blobs': len(jobs), 'copies': copies, 'rows': rows, 'cells': cells},
          open('parquet.json', 'w'), indent=1)
