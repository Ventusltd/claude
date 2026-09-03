"""Sweep a railway-crossing penalty (km-equivalent) added to edge weight.

The penalty is added to the SEARCH cost only; the REPORTED length of the chosen
route is always its true geodesic length, so the comparison against published
cable_km stays honest.
"""
import json, os, array, sys
from common import haversine, HERE
from router import Graph
from analyze import med, pct

MAX_SNAP_KM = 5.0


def true_length(G, path):
    s = 0.0
    for a, b in zip(path, path[1:]):
        e = G.edge_between(a, b)
        s += e[0]
    return s


def main(pre="roads", penalties=(0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 20.0)):
    G = Graph(pre); G.build_snap_index()
    m = G.meta["edges"]
    cnt = array.array("i")
    with open(os.path.join(HERE, "graph", pre + ".railcnt.bin"), "rb") as fh:
        cnt.fromfile(fh, m)
    V = json.load(open(os.path.join(HERE, "data", "validation_set.json")))

    # pre-snap once
    jobs = []
    for c in V:
        a, da = G.snap(c["lat1"], c["lon1"])
        b, db = G.snap(c["lat2"], c["lon2"])
        if da > MAX_SNAP_KM or db > MAX_SNAP_KM:
            continue
        jobs.append((c, a, b, da, db))

    results = []
    for pen in penalties:
        extra = [cnt[i] * pen for i in range(m)] if pen > 0 else None
        apes, wins, n = [], 0, 0
        for (c, a, b, da, db) in jobs:
            if a == b:
                L = 0.0
            else:
                d, path = G.astar(a, b, extra_cost=extra)
                if d is None:
                    continue
                L = true_length(G, path)   # TRUE length, penalty excluded
            tot = da + L + db
            pub = c["cable_km"]
            er = abs(tot - pub) / pub * 100.0
            es = abs(c["straight_km"] - pub) / pub * 100.0
            apes.append(er); n += 1
            if er < es: wins += 1
        results.append({
            "penalty_km_per_crossing": pen,
            "n_scored": n,
            "median_ape_routed": med(apes),
            "mean_ape_routed": sum(apes) / len(apes),
            "p75_ape_routed": pct(apes, .75),
            "beats_straight_frac_scored": wins / n,
            "beats_straight_frac_all95": wins / len(V),
        })
        print("pen=%5.1f km  n=%d  medAPE=%6.2f%%  meanAPE=%7.2f%%  beat=%.1f%% (scored) %.1f%% (all 95)"
              % (pen, n, results[-1]["median_ape_routed"], results[-1]["mean_ape_routed"],
                 100 * results[-1]["beats_straight_frac_scored"],
                 100 * results[-1]["beats_straight_frac_all95"]), flush=True)

    best = min(results, key=lambda r: r["median_ape_routed"])
    print("\nbest by median APE: penalty=%.1f km  medAPE=%.2f%%"
          % (best["penalty_km_per_crossing"], best["median_ape_routed"]))
    json.dump({"results": results, "best": best},
              open(os.path.join(HERE, "out_sweep.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "roads")
