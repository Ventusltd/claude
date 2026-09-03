import json, io, sys

src = json.load(open('deep.json'))

KEEP = ['ref', 'head_iso', 'first_iso', 'span_days', 'commits', 'merges', 'per_day',
        'c1', 'c7', 'c30', 'add_total', 'del_total', 'files_touched', 'files_median',
        'files_max', 'gap_med_h', 'gap_max_h', 'authors_total', 'tracked_files',
        'tracked_human', 'depth_avg', 'depth_max', 'branches', 'worktrees',
        'workflow_files', 'hours', 'dow']

out = {'generated_utc': src['generated_utc'], 'workers': src['workers'],
       'elapsed_s': src['elapsed_s'], 'repos': []}

for r in src['repos']:
    o = {k: r[k] for k in KEEP if k in r}
    if 'error' in r:
        o['error'] = 'unavailable'
        out['repos'].append(o)
        continue

    o['authors']     = [{'c': a['c']} for a in r.get('authors', [])[:5]]
    o['exts']        = [{'e': e['e'], 'n': e['n']} for e in r.get('exts', [])[:6]]
    o['biggest']     = [{'b': b['b']} for b in r.get('biggest', [])[:3]]
    o['branch_rows'] = [{'d': b['d'], 'ahead': b['ahead']} for b in r.get('branch_rows', [])[:5]]
    o['days30']      = [{'n': d['n']} for d in r.get('days30', [])]

    h = r.get('http') or {}
    o['http'] = {'status': h.get('status'), 'bytes': h.get('bytes'),
                 'ms': h.get('ms'), 'last_modified': h.get('last_modified')}

    c = r.get('ci') or {}
    if c.get('sampled'):
        o['ci'] = {k: c.get(k) for k in
                   ('sampled', 'total_count', 'success', 'failure', 'cancelled',
                    'window', 'dur_med', 'dur_max', 'dur_sum', 'deploy_consec_fail')}
        o['ci']['events'] = [{'e': e['e'], 'n': e['n']} for e in c.get('events', [])]
        o['ci']['workflows'] = [{'t': w['t'], 'f': w['f'], 'med': w['med'],
                                 'last': w['last'], 'lc': w['lc']}
                                for w in c.get('workflows', [])[:10]]
    else:
        o['ci'] = {'sampled': 0, 'total_count': c.get('total_count', 0)}

    l = r.get('loc')
    if l:
        o['loc'] = {'text_files': l['text_files'], 'lines_total': l['lines_total'],
                    'lines_codeish': l['lines_codeish'], 'files_codeish': l['files_codeish'],
                    'by_lang': [{'l': x['l'], 'n': x['n'], 'f': x['f']} for x in l['by_lang'][:6]]}
    out['repos'].append(o)

json.dump(out, open('payload.json', 'w'), indent=1)

blob = json.dumps(out)
NAMES = ['chatgpt-audits', 'companies', 'cvaa', 'data-centres-gb', 'data-gb-electricity',
         'data-grid-gb', 'data-gridatlas', 'data-interconnectors', 'gb-electricity-ui',
         'globalgrid2050', 'grid-distance-maths', 'gridatlas', 'pipelinenews', 'spiders',
         'ventusltd', 'github.io', 'Ventusltd', 'Vikram', 'Claude', 'codex/', 'atlas/',
         'audit/', 'Deploy', 'GridBot', 'REPD', '.py', '/']
leak = {n: blob.count(n) for n in NAMES if blob.count(n)}
print('payload bytes:', len(blob))
print('source bytes :', len(json.dumps(src)))
print('leaks        :', leak or 'none')
