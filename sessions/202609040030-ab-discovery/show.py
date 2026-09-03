"""Print one A/B reading as a diff, not as two dumps.

A finding is a difference. Printing both sides in full and asking a reader to
spot it is how a regression survives a review, so this prints only the keys
where A and B disagree, plus the keys a reader always wants regardless.
"""
import json
import sys

ALWAYS = ('counter', 'counter_dataset', 'v1', 'v2', 'v3', 'g1', 'g2', 'g3',
          'exportMeta', 'export_dataset', 'row_count', 'pagination',
          'map_cells_total', 'map_hrefs', 'map_cell_rect', 'table_scroll',
          'wider_selected', 'widerFleetMeta', 'screens_tall', 'depth',
          'gauge_canvas', 'errs', 'log', 'no_map_cells')

r = json.load(open(sys.argv[1], encoding='utf-8'))
buf = []


def p(*a):
    buf.append(' '.join(str(x) for x in a))


p('#', sys.argv[1], r['viewport'], r['utc'])
A, B = r['A'], r['B']
p('A =', A['generation'], ' B =', B['generation'])
p('picks: spine', A.get('spine_pick'), '| wider', A.get('wider_pick'))
for st in ('at_rest', 'after_spine', 'after_wider'):
    p('')
    p('== %s ==' % st)
    a, b = A.get(st) or {}, B.get(st) or {}
    for k in ALWAYS:
        va, vb = json.dumps(a.get(k)), json.dumps(b.get(k))
        mark = '  ' if va == vb else '!!'
        if va == vb:
            p('%s %-16s %s' % (mark, k, va[:300]))
        else:
            p('%s %-16s A: %s' % (mark, k, va[:300]))
            p('%s %-16s B: %s' % (mark, '', vb[:300]))
p('')
p('== share at table ==')
p('A', json.dumps(A.get('share_at_table')))
p('B', json.dumps(B.get('share_at_table')))
p('== export click (after a wider-fleet cut owns the table) ==')
p('A', json.dumps(A.get('export_click')))
p('B', json.dumps(B.get('export_click')))
p('== columns ==')
p(json.dumps((A.get('at_rest') or {}).get('columns')))
p('== first rows after wider ==')
p('A', json.dumps((A.get('after_wider') or {}).get('first_rows'))[:400])
p('B', json.dumps((B.get('after_wider') or {}).get('first_rows'))[:400])
p('== download guard ==', json.dumps(r.get('download_guard')))
sys.stdout.buffer.write('\n'.join(buf).encode('utf-8', 'replace'))
