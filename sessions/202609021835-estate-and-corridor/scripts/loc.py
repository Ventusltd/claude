import json, subprocess, collections, os, sys, pathlib, datetime, time
from concurrent.futures import ThreadPoolExecutor, as_completed

WORK  = pathlib.Path(sys.argv[1])
OUT   = sys.argv[2]
NPROC = os.cpu_count() or 8

REPOS = ["chatgpt-audits","companies","cvaa","data-centres-gb",
         "data-federation-map-for-globalgrid2050-all-repos","data-gb-electricity",
         "data-grid-gb","data-gridatlas","data-interconnectors","gb-electricity-ui",
         "globalgrid2050","grid-distance-maths","gridatlas","pipelinenews","spiders"]

# extension -> (language, class)  class: code | markup | config | data | docs
LANG = {
    '.py':('Python','code'), '.mjs':('JavaScript','code'), '.js':('JavaScript','code'),
    '.cjs':('JavaScript','code'), '.ts':('TypeScript','code'), '.tsx':('TypeScript','code'),
    '.jsx':('JavaScript','code'), '.sh':('Shell','code'), '.bash':('Shell','code'),
    '.ps1':('PowerShell','code'), '.awk':('Awk','code'), '.sql':('SQL','code'),
    '.r':('R','code'), '.rb':('Ruby','code'), '.go':('Go','code'), '.rs':('Rust','code'),
    '.java':('Java','code'), '.c':('C','code'), '.h':('C','code'), '.cpp':('C++','code'),
    '.html':('HTML','markup'), '.htm':('HTML','markup'), '.svg':('SVG','markup'),
    '.css':('CSS','markup'), '.scss':('CSS','markup'), '.xml':('XML','markup'),
    '.yml':('YAML','config'), '.yaml':('YAML','config'), '.toml':('TOML','config'),
    '.ini':('INI','config'), '.cfg':('INI','config'), '.gitattributes':('Git','config'),
    '.gitignore':('Git','config'), '.json':('JSON','data'), '.geojson':('GeoJSON','data'),
    '.csv':('CSV','data'), '.tsv':('TSV','data'), '.ndjson':('NDJSON','data'),
    '.md':('Markdown','docs'), '.txt':('Text','docs'), '.rst':('Text','docs'),
}
CODEISH = {'code', 'markup', 'config'}


def count(name):
    dst = WORK / name
    ref = None
    for r in ('gh/main', 'gh/master'):
        if subprocess.run(['git', '-C', str(dst), 'rev-parse', '--verify', '-q', r],
                          capture_output=True).returncode == 0:
            ref = r
            break
    if not ref:
        return {'name': name, 'error': 'no default branch'}

    r = subprocess.run(['git', '-C', str(dst), 'grep', '-I', '-c', '', ref, '--', '.'],
                       capture_output=True, text=True, errors='replace', timeout=1800)
    by_lang  = collections.Counter()
    by_files = collections.Counter()
    by_class = collections.Counter()
    cls_files = collections.Counter()
    total = files = 0
    prefix = ref + ':'
    for line in r.stdout.splitlines():
        if not line.startswith(prefix):
            continue
        rest = line[len(prefix):]
        path, _, n = rest.rpartition(':')
        if not n.isdigit():
            continue
        n = int(n)
        base = path.rsplit('/', 1)[-1]
        ext = ('.' + base.rsplit('.', 1)[1].lower()) if '.' in base[1:] else \
              (base.lower() if base.startswith('.') else '(none)')
        lang, cls = LANG.get(ext, ('Other', 'data' if ext == '(none)' else 'other'))
        by_lang[lang] += n
        by_files[lang] += 1
        by_class[cls] += n
        cls_files[cls] += 1
        total += n
        files += 1
    return {
        'name': name,
        'text_files': files,
        'lines_total': total,
        'lines_codeish': sum(by_class[c] for c in CODEISH),
        'files_codeish': sum(cls_files[c] for c in CODEISH),
        'by_class': [{'c': k, 'n': v, 'f': cls_files[k]} for k, v in by_class.most_common()],
        'by_lang': [{'l': k, 'n': v, 'f': by_files[k]} for k, v in by_lang.most_common(12)],
    }


t0 = time.time()
out = {}
with ThreadPoolExecutor(max_workers=NPROC) as ex:
    fs = {ex.submit(count, n): n for n in REPOS}
    for f in as_completed(fs):
        n = fs[f]
        try:
            out[n] = f.result()
        except Exception as e:
            out[n] = {'name': n, 'error': str(e)[:120]}

res = {'generated_utc': datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
       'elapsed_s': round(time.time() - t0, 1),
       'workers': NPROC,
       'repos': [out[n] for n in REPOS if n in out]}
json.dump(res, open(OUT, 'w'), indent=1)

W = 52
print('%-*s %10s %10s %10s' % (W, 'repository', 'text files', 'lines', 'code-ish'))
print('-' * (W + 33))
for r in res['repos']:
    if 'error' in r:
        print('%-*s %10s' % (W, r['name'], r['error']))
        continue
    print('%-*s %10s %10s %10s' % (W, r['name'], f"{r['text_files']:,}",
                                   f"{r['lines_total']:,}", f"{r['lines_codeish']:,}"))
print('-' * (W + 33))
print('%-*s %10s %10s %10s' % (W, 'TOTAL',
      f"{sum(r.get('text_files',0) for r in res['repos']):,}",
      f"{sum(r.get('lines_total',0) for r in res['repos']):,}",
      f"{sum(r.get('lines_codeish',0) for r in res['repos']):,}"))
print()
agg = collections.Counter()
aggf = collections.Counter()
for r in res['repos']:
    for e in r.get('by_lang', []):
        agg[e['l']] += e['n']; aggf[e['l']] += e['f']
print('%-16s %12s %10s' % ('language', 'lines', 'files'))
for l, n in agg.most_common(16):
    print('%-16s %12s %10s' % (l, f'{n:,}', f'{aggf[l]:,}'))
print('\nelapsed %.1fs  workers %d' % (res['elapsed_s'], NPROC), file=sys.stderr)
