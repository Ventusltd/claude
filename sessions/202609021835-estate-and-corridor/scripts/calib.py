"""Is a scalar detour factor on the straight line as good as routing?

Fits a single multiplier k minimising median absolute percentage error against
published cable_km, for (a) straight line and (b) routed distance. Also reports
leave-one-out (honest, no in-sample fitting advantage) and a de-duplicated view
over distinct site pairs, since 95 circuits cover only 59 unique pairs.
"""
import json, os
from common import HERE
from analyze import med, pct


def best_k(vals, pubs, lo=0.5, hi=3.0, steps=2501):
    best = (None, 1e18)
    for i in range(steps):
        k = lo + (hi - lo) * i / (steps - 1)
        e = med([abs(k * v - p) / p * 100.0 for v, p in zip(vals, pubs)])
        if e < best[1]:
            best = (k, e)
    return best


def loo_median_ape(vals, pubs):
    """Leave-one-out: fit k on all but i, score i."""
    out = []
    for i in range(len(vals)):
        v2 = vals[:i] + vals[i + 1:]; p2 = pubs[:i] + pubs[i + 1:]
        k, _ = best_k(v2, p2, steps=601)
        out.append(abs(k * vals[i] - pubs[i]) / pubs[i] * 100.0)
    return med(out), out


def report(rows, tag):
    s = [r["straight_km"] for r in rows]
    t = [r["routed_total_km"] for r in rows]
    p = [r["cable_km"] for r in rows]
    res = {"tag": tag, "n": len(rows)}
    res["raw_median_ape_straight"] = med([abs(a - b) / b * 100 for a, b in zip(s, p)])
    res["raw_median_ape_routed"] = med([abs(a - b) / b * 100 for a, b in zip(t, p)])
    ks, es = best_k(s, p); kt, et = best_k(t, p)
    res["best_k_straight"] = ks; res["calibrated_median_ape_straight"] = es
    res["best_k_routed"] = kt; res["calibrated_median_ape_routed"] = et
    lo_s, _ = loo_median_ape(s, p); lo_t, _ = loo_median_ape(t, p)
    res["loo_median_ape_straight"] = lo_s
    res["loo_median_ape_routed"] = lo_t
    # head-to-head after calibration
    wins = sum(1 for a, b, q in zip(s, t, p)
               if abs(kt * b - q) / q < abs(ks * a - q) / q)
    res["calibrated_routed_beats_calibrated_straight_frac"] = wins / len(rows)
    return res


def main():
    rows = [r for r in json.load(open(os.path.join(HERE, "out_routes.json")))
            if r["status"] == "ok"]
    out = {"all_scored_circuits": report(rows, "81 scored circuits")}

    # de-duplicated: one record per distinct site pair (mean of published lengths)
    byp = {}
    for r in rows:
        k = tuple(sorted((r["site_1"], r["site_2"])))
        byp.setdefault(k, []).append(r)
    ded = []
    for k, g in byp.items():
        r0 = dict(g[0])
        r0["cable_km"] = sum(x["cable_km"] for x in g) / len(g)
        ded.append(r0)
    out["distinct_site_pairs"] = report(ded, "%d distinct site pairs" % len(ded))

    json.dump(out, open(os.path.join(HERE, "out_calib.json"), "w"), indent=1)
    for k, v in out.items():
        print("--", v["tag"])
        print("   raw     : straight %.1f%%   routed %.1f%%"
              % (v["raw_median_ape_straight"], v["raw_median_ape_routed"]))
        print("   calibrat: straight x%.3f -> %.1f%%   routed x%.3f -> %.1f%%"
              % (v["best_k_straight"], v["calibrated_median_ape_straight"],
                 v["best_k_routed"], v["calibrated_median_ape_routed"]))
        print("   LOO     : straight %.1f%%   routed %.1f%%"
              % (v["loo_median_ape_straight"], v["loo_median_ape_routed"]))
        print("   calibrated routed beats calibrated straight: %.1f%%"
              % (100 * v["calibrated_routed_beats_calibrated_straight_frac"]))


if __name__ == "__main__":
    main()
