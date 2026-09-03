"""Count datapoints across the estate under an explicit, stated definition.

DEFINITION USED
  CSV / TSV : one datapoint = one non-empty cell in a non-header row.
  JSON / GeoJSON / NDJSON : one datapoint = one scalar VALUE leaf
                            (string, number, true, false, null).
                            Object KEYS are not counted.

Counted once per unique git blob, so the same file copied into many
immutable release folders is counted once, not once per copy.
"""
import subprocess, collections, os, re, sys, json, datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT  = sys.argv[1]
REPOS = ["chatgpt-audits","companies","cvaa","data-centres-gb",
         "data-federation-map-for-globalgrid2050-all-repos","data-gb-electricity",
         "data-grid-gb","data-gridatlas","data-interconnectors","gb-electricity-ui",
         "globalgrid2050","grid-distance-maths","gridatlas","pipelinenews","spiders"]
DATA = {'.csv', '.tsv', '.json', '.geojson', '.ndjson'}

TOK = re.compile(rb'"(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null|:')


def count_json(buf):
    """Scalar value leaves. A string immediately followed by ':' is a key."""
    toks = TOK.findall(buf)
    n = 0
    for i, t in enumerate(toks):
        if t == b':':
            continue
        if t.startswith(b'"') and i + 1 < len(toks) and toks[i + 1] == b':':
            continue          # object key
        n += 1
    return n


def count_csv(buf, sep):
    n = rows = 0
    for i, line in enumerate(buf.split(b'\n')):
        line = line.strip(b'\r')
        if not line.strip():
            continue
        if i == 0:
            continue          # header
        rows += 1
        n += sum(1 for c in line.split(sep) if c.strip())
    return n, rows


def work(job):
    repo, sha, path, ext, size = job
    try:
        buf = subprocess.run(['git', '-C', os.path.join(ROOT, repo), 'cat-file', 'blob', sha],
                             capture_output=True, timeout=900).stdout
    except Exception:
        return {'ext': ext, 'dp': 0, 'rows': 0, 'bytes': 0, 'skipped': 1}
    if ext in ('.csv', '.tsv'):
        dp, rows = count_csv(buf, b'\t' if ext == '.tsv' else b',')
    else:
        dp, rows = count_json(buf), 0
    return {'ext': ext, 'dp': dp, 'rows': rows, 'bytes': len(buf), 'skipped': 0}


def main():
    seen, jobs = {}, []
    copies = 0
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
            base = path.rsplit('/', 1)[-1]
            ext = ('.' + base.rsplit('.', 1)[1].lower()) if '.' in base[1:] else ''
            if ext not in DATA:
                continue
            copies += 1
            if sha not in seen:
                seen[sha] = True
                jobs.append((r, sha, path, ext, size))

    jobs.sort(key=lambda j: -j[4])          # biggest first, better packing
    by = collections.defaultdict(lambda: {'dp': 0, 'rows': 0, 'files': 0, 'bytes': 0})
    skipped = 0
    with ProcessPoolExecutor(max_workers=min(10, os.cpu_count() or 4)) as ex:
        futs = [ex.submit(work, j) for j in jobs]
        for i, f in enumerate(as_completed(futs)):
            r = f.result()
            b = by[r['ext']]
            b['dp'] += r['dp']; b['rows'] += r['rows']
            b['files'] += 1;    b['bytes'] += r['bytes']
            skipped += r['skipped']
            if (i + 1) % 200 == 0:
                print('  ... %d/%d' % (i + 1, len(jobs)), file=sys.stderr)

    total = sum(v['dp'] for v in by.values())
    print()
    print('%-10s %10s %16s %14s' % ('type', 'files', 'datapoints', 'bytes'))
    print('-' * 54)
    for e in sorted(by, key=lambda k: -by[k]['dp']):
        v = by[e]
        print('%-10s %10s %16s %13.1f MB' %
              (e, f"{v['files']:,}", f"{v['dp']:,}", v['bytes'] / 2**20))
    print('-' * 54)
    print('%-10s %10s %16s' % ('TOTAL', f"{sum(v['files'] for v in by.values()):,}", f"{total:,}"))
    print()
    print('unique data blobs counted : %s' % f"{len(jobs):,}")
    print('file copies on disk       : %s  (%s duplicates not double-counted)'
          % (f"{copies:,}", f"{copies - len(jobs):,}"))
    print('csv/tsv data rows         : %s' % f"{sum(by[e]['rows'] for e in ('.csv', '.tsv')):,}")
    print('skipped (unreadable)      : %d' % skipped)

    json.dump({'generated_utc': datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
               'total_datapoints': total,
               'unique_blobs': len(jobs), 'file_copies': copies,
               'by_type': {e: dict(v) for e, v in by.items()}},
              open('datapoints.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
