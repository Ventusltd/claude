"""Independently recompute every figure the Botley West card states about COWLEY,
straight from gb-transmission-network.v1.json. Nothing here reads the cartridge,
so an agreement is a real agreement and a divergence is a real divergence.
"""
import json, subprocess, collections

net = json.loads(subprocess.run(
    ['git', '-C', 'data-grid-gb', 'show', 'gh/main:derived/gb-transmission-network.v1.json'],
    capture_output=True).stdout)

SITE = 'COWL'
site = next(s for s in net['sites'] if s['code'] == SITE)
nodes = [n for n in net['nodes'] if n['site_code'] == SITE]
nset = {n['node'] for n in nodes}
kv_of = {n['node']: n.get('voltage_kv') for n in nodes}

def card(label, claimed, computed):
    ok = 'OK  ' if str(claimed) == str(computed) else 'DIFF'
    print('  [%s] %-42s card: %-26s computed: %s' % (ok, label, claimed, computed))

print('SITE %s  %s   TO %s   declared voltages %s' %
      (SITE, site['name'], site.get('transmission_owner'), site.get('voltages_kv')))
print('nodes at site: %d  ->  %s' % (len(nodes), ', '.join(sorted(nset))))
print()

# ---- circuits ----
circ = [c for c in net['circuits'] if c['node_1'] in nset or c['node_2'] in nset]
c_by_kv = collections.Counter()
for c in circ:
    end = c['node_1'] if c['node_1'] in nset else c['node_2']
    c_by_kv[kv_of.get(end)] += 1
card('circuits, site-wide', 6, len(circ))
card('circuits at 400 kV', 6, c_by_kv.get(400.0, 0) + c_by_kv.get(400, 0))
card('circuits at 132 kV', 0, c_by_kv.get(132.0, 0) + c_by_kv.get(132, 0))

w = [c['winter_mva'] for c in circ if c.get('winter_mva')]
s = [c['summer_mva'] for c in circ if c.get('summer_mva')]
card('winter rating range MVA', '1180-2779', '%g-%g' % (min(w), max(w)))
card('summer rating range MVA', '877-2219', '%g-%g' % (min(s), max(s)))

# ---- transformers ----
tx = [t for t in net['transformers'] if t['node_1'] in nset or t['node_2'] in nset]
both = [t for t in tx if t['node_1'] in nset and t['node_2'] in nset]
t_by_kv = collections.Counter()
for t in tx:
    for e in (t['node_1'], t['node_2']):
        if e in nset:
            t_by_kv[kv_of.get(e)] += 1
print()
card('transformers, site-wide', 10, len(tx))
card('transformers at 400 kV', 5, t_by_kv.get(400.0, 0) + t_by_kv.get(400, 0))
card('transformers at 132 kV', 5, t_by_kv.get(132.0, 0) + t_by_kv.get(132, 0))
print('       transformers with BOTH ends inside this site: %d' % len(both))
print('       -> physical units at the site: %d ; winding-ends counted: %d'
      % (len(tx), sum(t_by_kv.values())))

# ---- reactive compensation ----
rc = [r for r in net['reactive_compensation'] if r['node'] in nset or r.get('site_code') == SITE]
print()
card('reactive compensation units', 5, len(rc))

# ---- planned changes ----
pc = [p for p in net['planned_changes'] if p['node_1'] in nset or p['node_2'] in nset]
yrs = collections.Counter(p['year'] for p in pc)
print()
card('planned changes total', 14, len(pc))
card('planned change years', '2026, 2028, 2030', ', '.join(sorted(yrs)))
for y in sorted(yrs):
    st = collections.Counter(p['status'] for p in pc if p['year'] == y)
    print('       %s: %s' % (y, '  '.join('%s %s' % (v, k) for k, v in sorted(st.items()))))

# ---- fault current ----
fc = [f for f in net['fault_current_scenarios'] if f.get('site_code') == SITE]
brk = [f['three_phase_rms_break_current_ka'] for f in fc
       if f.get('three_phase_rms_break_current_ka') is not None]
buses = {f['location'] for f in fc}
years = {f['winter'] for f in fc}
print()
card('fault-current rows', 15, len(fc))
card('distinct buses', 3, len(buses))
card('3ph RMS break current kA', '12.4-49.4', '%g-%g' % (min(brk), max(brk)))
card('year span', '2025/26 to 2033/34', '%s to %s' % (min(years), max(years)))
print('       buses: %s' % ', '.join(sorted(buses)))
print('       demand cases: %s' % ', '.join(sorted({f['demand_case'] for f in fc})))

# ---- neighbours ----
adj = collections.defaultdict(set)
nsite = {n['node']: n['site_code'] for n in net['nodes']}
for c in net['circuits']:
    a, b = nsite.get(c['node_1']), nsite.get(c['node_2'])
    if a and b and a != b:
        adj[a].add(b); adj[b].add(a)
one = adj[SITE]
two = {x for h in one for x in adj[h]} - one - {SITE}
name = {s['code']: s['name'] for s in net['sites']}
print()
card('sites one circuit away', 6, len(one))
card('more sites at two hops', 9, len(two))
print('       reach: %s' % ', '.join(sorted(name.get(c, c) for c in one)))
