"""Route the 95 cable circuits and measure routed vs straight vs published.

Definitions (kept explicit because the snap distance must never be hidden):
  straight_km      great-circle between the two SITE coordinates          [baseline]
  snap1/snap2      site -> nearest routable road junction                 [reported]
  routed_core_km   A* road distance between the two SNAPPED junctions
  routed_total_km  snap1 + routed_core_km + snap2                         [candidate]
  published_km     NESO cable_km for the circuit                          [truth]
"""
import json, os, sys, time
from common import haversine, HERE
from router import Graph

MAX_SNAP_KM = 5.0


def run(pre="roads", out="out_routes.json"):
    G = Graph(pre)
    G.build_snap_index()
    V = json.load(open(os.path.join(HERE, "data", "validation_set.json")))
    rows = []
    t0 = time.time()
    for c in V:
        r = dict(c)
        a, da = G.snap(c["lat1"], c["lon1"])
        b, db = G.snap(c["lat2"], c["lon2"])
        r["snap1_km"] = da; r["snap2_km"] = db
        r["snap_node_1"] = a; r["snap_node_2"] = b
        r["snap_max_km"] = max(da, db)
        # straight line between the SNAPPED nodes -- the correct invariant target
        r["straight_snapped_km"] = haversine(G.nlat[a], G.nlon[a], G.nlat[b], G.nlon[b])
        if da > MAX_SNAP_KM or db > MAX_SNAP_KM:
            r["status"] = "snap_too_far"
            r["routed_core_km"] = None; r["routed_total_km"] = None
            rows.append(r); continue
        if a == b:
            r["status"] = "same_snap_node"
            r["routed_core_km"] = 0.0
            r["routed_total_km"] = da + db
            r["path_hops"] = 1
            rows.append(r); continue
        d, path = G.astar(a, b)
        if d is None:
            r["status"] = "no_path"
            r["routed_core_km"] = None; r["routed_total_km"] = None
            rows.append(r); continue
        r["status"] = "ok"
        r["routed_core_km"] = d
        r["routed_total_km"] = da + d + db
        r["path_hops"] = len(path)
        r["path"] = path
        rows.append(r)
    print("routed %d circuits in %.1fs" % (len(rows), time.time() - t0))
    json.dump(rows, open(os.path.join(HERE, out), "w"))
    return rows


if __name__ == "__main__":
    pre = sys.argv[1] if len(sys.argv) > 1 else "roads"
    out = sys.argv[2] if len(sys.argv) > 2 else "out_routes.json"
    rows = run(pre, out)
    from collections import Counter
    print(Counter(r["status"] for r in rows))
    snaps = sorted([r["snap1_km"] for r in rows] + [r["snap2_km"] for r in rows])
    print("snap distance km: min=%.2f p50=%.2f p90=%.2f max=%.2f" %
          (snaps[0], snaps[len(snaps) // 2], snaps[int(len(snaps) * .9)], snaps[-1]))
