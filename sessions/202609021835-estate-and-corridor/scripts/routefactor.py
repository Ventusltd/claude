"""Measure the GB transmission route factor from published data.

Every ETYS circuit publishes its real built length (ohl_km + cable_km) and
connects two named nodes whose sites have coordinates. So the ratio between
"straight line between the two sites" and "length actually built" can be
measured, not assumed. That ratio is what turns a crow-flies distance on a
project card into a defensible statement about a route.
"""
import json, subprocess, math, statistics, collections

def sh(*a):
    return subprocess.run(a, capture_output=True).stdout

net = json.loads(sh('git', '-C', 'data-grid-gb', 'show',
                    'gh/main:derived/gb-transmission-network.v1.json'))
cps = json.loads(sh('git', '-C', 'data-grid-gb', 'show',
                    'gh/main:derived/connection-points.v3.json'))['connection_points']

loc = {}
for p in cps:
    L = p.get('location')
    if L:
        lat = L.get('latitude', L.get('lat'))
        lon = L.get('longitude', L.get('lon', L.get('lng')))
        if lat is not None and lon is not None:
            loc[p['site_code']] = (float(lat), float(lon))

node_site = {n['node']: n['site_code'] for n in net['nodes']}
node_kv   = {n['node']: n.get('voltage_kv') for n in net['nodes']}

R = 6371.0088
def gc(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(min(1, math.sqrt(h)))

rows = []
skip = collections.Counter()
for c in net['circuits']:
    s1, s2 = node_site.get(c['node_1']), node_site.get(c['node_2'])
    if not s1 or not s2:
        skip['node has no site'] += 1; continue
    if s1 == s2:
        skip['both ends same site'] += 1; continue
    if s1 not in loc or s2 not in loc:
        skip['site has no coordinates'] += 1; continue
    built = (c.get('ohl_km') or 0) + (c.get('cable_km') or 0)
    if built <= 0:
        skip['no published length'] += 1; continue
    d = gc(loc[s1], loc[s2])
    if d < 1.0:
        skip['ends under 1 km apart'] += 1; continue
    kv = node_kv.get(c['node_1']) or node_kv.get(c['node_2'])
    rows.append({'ratio': built / d, 'straight': d, 'built': built, 'kv': kv,
                 'type': c.get('circuit_type'), 'cable': c.get('cable_km') or 0})

print('circuits published        : %6d' % len(net['circuits']))
print('usable for measurement    : %6d' % len(rows))
for k, v in skip.most_common():
    print('  skipped, %-24s %5d' % (k, v))

rs = sorted(r['ratio'] for r in rows)
def q(p): return rs[int(p * (len(rs) - 1))]
print()
print('ROUTE FACTOR  (built length / straight-line between site coordinates)')
print('  p10 %.2f   p25 %.2f   median %.2f   p75 %.2f   p90 %.2f' %
      (q(.10), q(.25), q(.50), q(.75), q(.90)))
print('  mean %.2f   n=%d' % (statistics.mean(rs), len(rs)))

print()
print('by voltage class:')
byk = collections.defaultdict(list)
for r in rows:
    if r['kv']:
        byk[r['kv']].append(r['ratio'])
for kv in sorted(byk, reverse=True):
    v = sorted(byk[kv])
    if len(v) >= 12:
        print('  %4s kV  n=%4d   median %.2f   p25 %.2f   p75 %.2f' %
              (kv, len(v), v[len(v)//2], v[len(v)//4], v[3*len(v)//4]))

print()
print('by circuit type:')
byt = collections.defaultdict(list)
for r in rows:
    byt[r['type'] or '?'].append(r['ratio'])
for t in sorted(byt, key=lambda k: -len(byt[k])):
    v = sorted(byt[t])
    if len(v) >= 10:
        print('  %-12s n=%4d   median %.2f' % (t, len(v), v[len(v)//2]))

sane = [r for r in rows if r['ratio'] < 5]
print()
print('sanity: %d circuits have built length > 5x straight line' % (len(rows) - len(sane)))
worst = sorted(rows, key=lambda r: -r['ratio'])[:5]
for w in worst:
    print('   ratio %6.1f  straight %6.2f km  built %7.2f km  %s' %
          (w['ratio'], w['straight'], w['built'], w['type']))
json.dump({'n': len(rs), 'median': q(.50), 'p25': q(.25), 'p75': q(.75),
           'p10': q(.10), 'p90': q(.90)}, open('routefactor.json', 'w'), indent=1)
