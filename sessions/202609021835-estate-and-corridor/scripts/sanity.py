"""Sanity checks demanded by the study brief."""
import random, math, json, time, os
from common import haversine, spherical_law_of_cosines, vincenty_sphere, HERE
from router import Graph

random.seed(20260903)
res = {}

# ---- 1. haversine vs two independent formulas ----
worst_slc = 0.0; worst_vin = 0.0
for _ in range(200000):
    la1 = random.uniform(49.0, 61.0); lo1 = random.uniform(-8.0, 2.0)
    la2 = random.uniform(49.0, 61.0); lo2 = random.uniform(-8.0, 2.0)
    h = haversine(la1, lo1, la2, lo2)
    if h < 1e-6:
        continue
    worst_slc = max(worst_slc, abs(h - spherical_law_of_cosines(la1, lo1, la2, lo2)) / h)
    worst_vin = max(worst_vin, abs(h - vincenty_sphere(la1, lo1, la2, lo2)) / h)
# short distances too (where law-of-cosines is known to lose precision)
worst_short = 0.0
for _ in range(50000):
    la1 = random.uniform(49.0, 61.0); lo1 = random.uniform(-8.0, 2.0)
    la2 = la1 + random.uniform(-0.002, 0.002); lo2 = lo1 + random.uniform(-0.002, 0.002)
    h = haversine(la1, lo1, la2, lo2)
    if h < 1e-9:
        continue
    worst_short = max(worst_short, abs(h - vincenty_sphere(la1, lo1, la2, lo2)) / h)
res["haversine_vs_law_of_cosines_max_rel"] = worst_slc
res["haversine_vs_vincenty_max_rel"] = worst_vin
res["haversine_vs_vincenty_max_rel_short_links"] = worst_short
res["formula_agreement_1e-9"] = bool(worst_vin < 1e-9 and worst_short < 1e-9)

# ---- load graph ----
t0 = time.time()
G = Graph("roads")
ncells = G.build_snap_index()
res["graph_load_seconds"] = round(time.time() - t0, 2)
res["snap_cells"] = ncells
res["nodes"] = G.n
res["giant_frac"] = G.meta["giant_frac"]

# ---- 2. edge weight equals the sum of its own geometry legs (EXHAUSTIVE) ----
w_by_eid = {}
for p_ in range(len(G.eids)):
    w_by_eid[G.eids[p_]] = G.weights[p_]
worst_edge = 0.0; checked = 0; mism = 0; worst_abs = 0.0
for eid in range(G.meta["edges"]):
    gm = G.edge_geometry(eid); npts = len(gm) // 2
    if npts < 2: continue
    s_ = 0.0
    for i in range(npts - 1):
        s_ += haversine(gm[2*i+1], gm[2*i], gm[2*i+3], gm[2*i+2])
    if s_ <= 0: continue
    w = w_by_eid[eid]; checked += 1
    r = abs(w - s_) / s_
    if r > 1e-9:
        mism += 1; worst_abs = max(worst_abs, abs(w - s_))
    worst_edge = max(worst_edge, r)
res["edge_weight_vs_geometry_max_rel"] = worst_edge
res["edge_weight_vs_geometry_max_abs_km"] = worst_abs
res["edge_weight_checks"] = checked
res["edge_weight_mismatches_over_1e-9"] = mism

# ---- 3. zero-length route between identical points ----
nd, _ = G.snap(52.5, -1.9)
c, p = G.astar(nd, nd)
res["identical_point_route_km"] = c
res["identical_point_route_is_zero"] = (c == 0.0)

# ---- 4. route length equals the sum of its own leg lengths ----
worst_leg = 0.0; tested = 0; failed = 0
for _ in range(25):
    a, _ = G.snap(random.uniform(51.0, 55.0), random.uniform(-3.0, 0.5))
    b, _ = G.snap(random.uniform(51.0, 55.0), random.uniform(-3.0, 0.5))
    c, path = G.astar(a, b)
    if c is None:
        failed += 1; continue
    legs = G.path_legs(path)
    s = sum(w for w, _e in legs)
    tested += 1
    if c > 0:
        worst_leg = max(worst_leg, abs(c - s) / c)
res["route_vs_legsum_max_rel"] = worst_leg
res["route_legsum_routes_tested"] = tested
res["route_legsum_routes_failed"] = failed

print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(HERE, "out_sanity.json"), "w"), indent=1)
