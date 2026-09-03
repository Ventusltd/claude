"""Count railway crossings on each routed path and test correlation with error."""
import json, os, math
from common import HERE
from router import Graph
from rail import RailIndex
from analyze import med, pct


def pearson(xs, ys):
    n = len(xs)
    if n < 3: return float("nan")
    mx = sum(xs) / n; my = sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs); syy = sum((b - my) ** 2 for b in ys)
    if sxx <= 0 or syy <= 0: return float("nan")
    return sxy / math.sqrt(sxx * syy)


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]: j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1): r[order[k]] = avg
            i = j + 1
        return r
    return pearson(rank(xs), rank(ys))


def main():
    G = Graph("roads"); G.build_snap_index()
    R = RailIndex()
    rows = json.load(open(os.path.join(HERE, "out_routes.json")))
    out = []
    for r in rows:
        if r["status"] != "ok" or "path" not in r:
            continue
        poly = G.path_geometry(r["path"])
        nx = R.count_crossings(poly)
        pub = r["cable_km"]
        rec = {"from": r["name_1"], "to": r["name_2"], "crossings": nx,
               "routed_total_km": r["routed_total_km"], "cable_km": pub,
               "straight_km": r["straight_km"],
               "ape_routed": abs(r["routed_total_km"] - pub) / pub * 100.0,
               "detour_ratio": r["routed_total_km"] / r["straight_km"],
               "crossings_per_km": nx / r["routed_total_km"]}
        out.append(rec)
    xs = [r["crossings"] for r in out]
    ys = [r["ape_routed"] for r in out]
    res = {
        "n": len(out),
        "crossings": {"min": min(xs), "p25": pct(xs, .25), "p50": med(xs),
                      "p75": pct(xs, .75), "p90": pct(xs, .90), "max": max(xs),
                      "mean": sum(xs) / len(xs), "zero_crossing_routes": xs.count(0)},
        "crossings_per_km_median": med([r["crossings_per_km"] for r in out]),
        "pearson_crossings_vs_ape": pearson(xs, ys),
        "spearman_crossings_vs_ape": spearman(xs, ys),
        "pearson_crossings_vs_detour": pearson(xs, [r["detour_ratio"] for r in out]),
        "spearman_crossings_vs_detour": spearman(xs, [r["detour_ratio"] for r in out]),
        "pearson_crossings_vs_routedkm": pearson(xs, [r["routed_total_km"] for r in out]),
    }
    json.dump({"summary": res, "rows": out},
              open(os.path.join(HERE, "out_crossings.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    hist = {}
    for x in xs: hist[x] = hist.get(x, 0) + 1
    print("crossing histogram:", dict(sorted(hist.items())))


if __name__ == "__main__":
    main()
