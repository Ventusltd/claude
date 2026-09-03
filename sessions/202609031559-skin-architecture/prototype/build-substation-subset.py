import json, math, sys, os

SRC = r"C:\Users\vikra\OneDrive\Documents\GitHub\gridatlas\atlas\releases\202608300453-atlas-v9\data\grid_substations.geojson"
DST = r"C:\Users\vikra\OneDrive\Documents\GitHub\claude\sessions\202609031559-skin-architecture\prototype\substations.json"

R = 6378.137
D = math.pi / 180.0

def dk(a, b, c, d):
    dla = (d - b) * D
    dlo = (c - a) * D
    x = math.sin(dla / 2) ** 2 + math.cos(b * D) * math.cos(d * D) * math.sin(dlo / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))

def rep(g):
    if not g:
        return None
    t = g.get("type")
    c = g.get("coordinates")
    if t == "Point":
        return c
    ring = None
    if t == "Polygon":
        ring = c[0]
    elif t == "MultiPolygon":
        ring = c[0][0]
    if not ring:
        return None
    return [sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)]

with open(SRC, "r", encoding="utf-8") as fh:
    gj = json.load(fh)

B = (-1.3489728, 51.8132088)   # Botley West Solar Project
O = (0.15, 53.88)              # Ossian, offshore
K = (-2.30, 56.15)             # a Firth of Forth point, so the set covers a
                               # northern drag target for the move-the-project demo.
                               # NOT asserted to be any named project location.

seen = set()
rows = []
for f in gj["features"]:
    p = f.get("properties") or {}
    at = rep(f.get("geometry"))
    if not at:
        continue
    v = str(p.get("voltage") or "")
    kvs = []
    for s in v.split(";"):
        try:
            n = round(float(s) / 1000)
        except Exception:
            continue
        if n > 0 and n not in kvs:
            kvs.append(n)
    if not kvs:
        continue
    kvs.sort(reverse=True)
    db = dk(B[0], B[1], at[0], at[1])
    do = dk(O[0], O[1], at[0], at[1])
    dbb = dk(K[0], K[1], at[0], at[1])
    keep = (db <= 45) or (kvs[0] >= 400 and db <= 90) or (kvs[0] >= 275 and do <= 220) or (kvs[0] >= 275 and dbb <= 220)
    if not keep:
        continue
    key = (round(at[0], 5), round(at[1], 5))
    if key in seen:
        continue
    seen.add(key)
    rows.append([p.get("name") or None, kvs, round(at[0], 6), round(at[1], 6)])

payload = {
    "schema": "gridatlas.substations.subset/1",
    "source": "gridatlas/atlas/releases/202608300453-atlas-v9/data/grid_substations.geojson",
    "source_features": len(gj["features"]),
    "note": "A geographic subset, taken so this prototype loads in milliseconds. "
            "Rows are [name, [kV...], lon, lat]. Representative point is the mean of "
            "the outer ring, exactly as modules/202609011950-geodesy.js does it.",
    "anchors": {"botley_west": list(B), "ossian": list(O), "firth_of_forth_point": list(K)},
    "rows": rows,
}
os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(payload, fh, separators=(",", ":"))

print("features", len(gj["features"]), "kept", len(rows), "bytes", os.path.getsize(DST))
n400 = [r for r in rows if r[1][0] >= 400]
n400.sort(key=lambda r: dk(B[0], B[1], r[2], r[3]))
print("nearest 400kV to Botley:", n400[0][0], round(dk(B[0], B[1], n400[0][2], n400[0][3]), 3))
n400.sort(key=lambda r: dk(O[0], O[1], r[2], r[3]))
print("nearest 400kV to Ossian:", n400[0][0], round(dk(O[0], O[1], n400[0][2], n400[0][3]), 3))
n400.sort(key=lambda r: dk(K[0], K[1], r[2], r[3]))
print("nearest 400kV to Forth point:", n400[0][0], round(dk(K[0], K[1], n400[0][2], n400[0][3]), 3))
