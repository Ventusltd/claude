"""Shared geodesy + IO for the road-routing feasibility study."""
import json, math, os

R_KM = 6371.0088
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def haversine(lat1, lon1, lat2, lon2):
    p1 = math.radians(lat1); p2 = math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return 2.0 * R_KM * math.asin(math.sqrt(a))


def spherical_law_of_cosines(lat1, lon1, lat2, lon2):
    """Independent formula for cross-checking haversine."""
    p1 = math.radians(lat1); p2 = math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    x = max(-1.0, min(1.0, x))
    return R_KM * math.acos(x)


def vincenty_sphere(lat1, lon1, lat2, lon2):
    """Second independent formula (special case of Vincenty on a sphere)."""
    p1 = math.radians(lat1); p2 = math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    num = math.sqrt((math.cos(p2) * math.sin(dl)) ** 2 +
                    (math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)) ** 2)
    den = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return R_KM * math.atan2(num, den)


def load_sites_with_coords():
    cp = json.load(open(os.path.join(DATA, "cp.json"), encoding="utf-8"))
    out = {}
    for p in cp["connection_points"]:
        loc = p.get("location")
        if loc and loc.get("lat") is not None and loc.get("lon") is not None:
            out[p["site_code"]] = (float(loc["lat"]), float(loc["lon"]),
                                   p.get("name"), loc.get("matched_by"))
    return out


def load_validation_set(min_sep_km=1.0):
    net = json.load(open(os.path.join(DATA, "network.json"), encoding="utf-8"))
    node2site = {n["node"]: n["site_code"] for n in net["nodes"]}
    coords = load_sites_with_coords()

    stats = {"cable_circuits": 0, "no_node_map": 0, "no_coords": 0,
             "zero_len": 0, "too_close": 0, "kept": 0}
    kept = []
    for c in net["circuits"]:
        if c.get("circuit_type") != "Cable":
            continue
        stats["cable_circuits"] += 1
        s1 = node2site.get(c["node_1"]); s2 = node2site.get(c["node_2"])
        if not s1 or not s2:
            stats["no_node_map"] += 1; continue
        if s1 not in coords or s2 not in coords:
            stats["no_coords"] += 1; continue
        pub = (c.get("cable_km") or 0.0) + (c.get("ohl_km") or 0.0)
        cab = c.get("cable_km") or 0.0
        if cab <= 0:
            stats["zero_len"] += 1; continue
        a = coords[s1]; b = coords[s2]
        sl = haversine(a[0], a[1], b[0], b[1])
        if sl <= min_sep_km:
            stats["too_close"] += 1; continue
        stats["kept"] += 1
        kept.append({
            "node_1": c["node_1"], "node_2": c["node_2"],
            "site_1": s1, "site_2": s2,
            "name_1": a[2], "name_2": b[2],
            "matched_1": a[3], "matched_2": b[3],
            "lat1": a[0], "lon1": a[1], "lat2": b[0], "lon2": b[1],
            "cable_km": cab, "ohl_km": c.get("ohl_km") or 0.0,
            "published_km": pub,
            "straight_km": sl,
            "owner": c.get("transmission_owner"),
            "winter_mva": c.get("winter_mva"),
        })
    return kept, stats


if __name__ == "__main__":
    kept, stats = load_validation_set()
    print(json.dumps(stats, indent=1))
    # dedupe view: how many distinct site pairs
    pairs = set()
    for k in kept:
        pairs.add(tuple(sorted((k["site_1"], k["site_2"]))))
    print("distinct site pairs:", len(pairs))
    json.dump(kept, open(os.path.join(DATA, "validation_set.json"), "w"), indent=1)
    print("wrote", len(kept), "circuits")
