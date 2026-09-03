"""Measure straight vs routed against published cable_km."""
import json, os, sys
from common import HERE

def pct(xs, q):
    if not xs: return float("nan")
    s = sorted(xs); i = (len(s) - 1) * q
    lo = int(i); hi = min(lo + 1, len(s) - 1); f = i - lo
    return s[lo] * (1 - f) + s[hi] * f

def med(xs): return pct(xs, 0.5)

def summarize(rows, label, candidate_key="routed_total_km", truth_key="cable_km"):
    ok = [r for r in rows if r["status"] == "ok" and r.get(candidate_key) is not None]
    out = {"label": label, "n_total": len(rows), "n_scored": len(ok)}
    ape_s, ape_r, ratio_rs, ratio_rp, ratio_sp = [], [], [], [], []
    wins = 0
    for r in ok:
        pub = r[truth_key]; s = r["straight_km"]; c = r[candidate_key]
        es = abs(s - pub) / pub * 100.0
        er = abs(c - pub) / pub * 100.0
        r["ape_straight"] = es; r["ape_routed"] = er
        r["ratio_routed_straight"] = c / s
        r["ratio_routed_pub"] = c / pub
        r["ratio_straight_pub"] = s / pub
        ape_s.append(es); ape_r.append(er)
        ratio_rs.append(c / s); ratio_rp.append(c / pub); ratio_sp.append(s / pub)
        if er < es: wins += 1
    out["median_ape_straight"] = med(ape_s)
    out["median_ape_routed"] = med(ape_r)
    out["mean_ape_straight"] = sum(ape_s) / len(ape_s) if ape_s else None
    out["mean_ape_routed"] = sum(ape_r) / len(ape_r) if ape_r else None
    out["p25_ape_routed"] = pct(ape_r, .25); out["p75_ape_routed"] = pct(ape_r, .75)
    out["p25_ape_straight"] = pct(ape_s, .25); out["p75_ape_straight"] = pct(ape_s, .75)
    out["routed_beats_straight_n"] = wins
    out["routed_beats_straight_frac"] = wins / len(ok) if ok else 0.0
    out["median_ratio_routed_straight"] = med(ratio_rs)
    out["median_ratio_routed_published"] = med(ratio_rp)
    out["median_ratio_straight_published"] = med(ratio_sp)
    # gate, evaluated over ALL circuits in the validation set (failures count against)
    out["gate_median_ape_lt_15"] = out["median_ape_routed"] < 15.0
    out["gate_beat_frac_ge_80_scored"] = out["routed_beats_straight_frac"] >= 0.80
    out["beat_frac_of_all_95"] = wins / len(rows)
    out["gate_beat_frac_ge_80_all"] = (wins / len(rows)) >= 0.80
    out["gate_passes_scored_only"] = bool(out["gate_median_ape_lt_15"] and out["gate_beat_frac_ge_80_scored"])
    out["gate_passes_all_circuits"] = bool(out["gate_median_ape_lt_15"] and out["gate_beat_frac_ge_80_all"])
    return out, ok

def main(path="out_routes.json"):
    rows = json.load(open(os.path.join(HERE, path)))
    res = {}
    for key in ("routed_total_km", "routed_core_km"):
        s, ok = summarize(rows, key, candidate_key=key)
        res[key] = s

    # ---- invariant checks ----
    viol_site, viol_snap = [], []
    for r in rows:
        if r["status"] != "ok": continue
        if r["routed_total_km"] < r["straight_km"] - 1e-9:
            viol_site.append((r["site_1"], r["site_2"], r["routed_total_km"], r["straight_km"]))
        if r["routed_core_km"] < r["straight_snapped_km"] - 1e-9:
            viol_snap.append((r["site_1"], r["site_2"], r["routed_core_km"], r["straight_snapped_km"]))
    res["invariant_routed_total_ge_straight_site_violations"] = len(viol_site)
    res["invariant_routed_core_ge_straight_snapped_violations"] = len(viol_snap)
    res["invariant_violation_examples"] = viol_site[:5]

    # ---- snap distribution ----
    snaps = [r["snap1_km"] for r in rows] + [r["snap2_km"] for r in rows]
    res["snap_km"] = {"min": min(snaps), "p50": med(snaps), "p75": pct(snaps, .75),
                      "p90": pct(snaps, .90), "max": max(snaps),
                      "over_1km": sum(1 for x in snaps if x > 1.0),
                      "over_5km": sum(1 for x in snaps if x > 5.0),
                      "n": len(snaps)}
    from collections import Counter
    res["status"] = dict(Counter(r["status"] for r in rows))

    # ---- published length context ----
    pubs = [r["cable_km"] for r in rows]
    res["published_cable_km"] = {"min": min(pubs), "p50": med(pubs), "max": max(pubs),
                                 "under_5km": sum(1 for p in pubs if p < 5)}
    sl = [r["straight_km"] for r in rows]
    res["straight_km_dist"] = {"min": min(sl), "p50": med(sl), "max": max(sl)}

    # ---- worst 10 by routed error ----
    ok = [r for r in rows if r["status"] == "ok"]
    ok.sort(key=lambda r: -r["ape_routed"])
    res["worst10"] = [{
        "from": r["name_1"], "to": r["name_2"],
        "pub_cable_km": round(r["cable_km"], 2), "ohl_km": round(r["ohl_km"], 2),
        "straight_km": round(r["straight_km"], 2),
        "routed_total_km": round(r["routed_total_km"], 2),
        "routed_core_km": round(r["routed_core_km"], 2),
        "snap1": round(r["snap1_km"], 2), "snap2": round(r["snap2_km"], 2),
        "ape_routed": round(r["ape_routed"], 1), "ape_straight": round(r["ape_straight"], 1),
        "matched_1": r["matched_1"], "matched_2": r["matched_2"],
    } for r in ok[:10]]

    # circuits where straight line already EXCEEDS published (coordinate/rating problem)
    res["straight_exceeds_published_n"] = sum(1 for r in rows if r["straight_km"] > r["cable_km"])
    res["straight_exceeds_published_frac"] = res["straight_exceeds_published_n"] / len(rows)

    json.dump(res, open(os.path.join(HERE, "out_metrics.json"), "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out_routes.json")
