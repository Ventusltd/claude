"""Railway crossing counting: spatial index over mainline railway segments."""
import json, os, array, math, time, gc
from common import haversine, HERE
from build_graph import read_blob

CELL = 0.01  # ~1.1 km lat


def load_rail_segments():
    """Flat arrays of segment endpoints (lon1,lat1,lon2,lat2)."""
    raw = read_blob("uk_mainline_railways.geojson")
    gj = json.loads(raw); del raw
    seg = array.array("d")
    nl = 0
    for f in gj["features"]:
        g = f.get("geometry")
        if not g: continue
        gt = g.get("type")
        if gt == "LineString": lines = [g["coordinates"]]
        elif gt == "MultiLineString": lines = g["coordinates"]
        else: continue
        for ln in lines:
            if len(ln) < 2: continue
            nl += 1
            for i in range(len(ln) - 1):
                seg.append(ln[i][0]); seg.append(ln[i][1])
                seg.append(ln[i + 1][0]); seg.append(ln[i + 1][1])
    del gj; gc.collect()
    return seg, nl


def build_index(seg, cell=CELL):
    """Grid hash: cell -> list of segment indices."""
    idx = {}
    n = len(seg) // 4
    for s in range(n):
        x1 = seg[4 * s]; y1 = seg[4 * s + 1]
        x2 = seg[4 * s + 2]; y2 = seg[4 * s + 3]
        i1 = int(math.floor(y1 / cell)); j1 = int(math.floor(x1 / cell))
        i2 = int(math.floor(y2 / cell)); j2 = int(math.floor(x2 / cell))
        for i in range(min(i1, i2), max(i1, i2) + 1):
            for j in range(min(j1, j2), max(j1, j2) + 1):
                b = idx.get((i, j))
                if b is None: idx[(i, j)] = [s]
                else: b.append(s)
    return idx


def _orient(ax, ay, bx, by, cx, cy):
    v = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    if v > 1e-14: return 1
    if v < -1e-14: return -1
    return 0


def seg_intersect(ax, ay, bx, by, cx, cy, dx, dy):
    """Proper segment intersection in lon/lat plane (fine at GB scale)."""
    d1 = _orient(cx, cy, dx, dy, ax, ay)
    d2 = _orient(cx, cy, dx, dy, bx, by)
    d3 = _orient(ax, ay, bx, by, cx, cy)
    d4 = _orient(ax, ay, bx, by, dx, dy)
    return d1 != d2 and d3 != d4 and d1 != 0 and d2 != 0 and d3 != 0 and d4 != 0


class RailIndex:
    def __init__(self, cell=CELL):
        t0 = time.time()
        self.seg, self.nlines = load_rail_segments()
        self.nseg = len(self.seg) // 4
        self.idx = build_index(self.seg, cell)
        self.cell = cell
        self.build_seconds = time.time() - t0

    def count_crossings(self, poly, dedup=True):
        """poly: flat [lon,lat,...]. Returns number of railway segments crossed."""
        seg = self.seg; idx = self.idx; cell = self.cell
        hits = set()
        npts = len(poly) // 2
        for k in range(npts - 1):
            ax = poly[2 * k]; ay = poly[2 * k + 1]
            bx = poly[2 * k + 2]; by = poly[2 * k + 3]
            i1 = int(math.floor(ay / cell)); j1 = int(math.floor(ax / cell))
            i2 = int(math.floor(by / cell)); j2 = int(math.floor(bx / cell))
            cand = set()
            for i in range(min(i1, i2), max(i1, i2) + 1):
                for j in range(min(j1, j2), max(j1, j2) + 1):
                    b = idx.get((i, j))
                    if b: cand.update(b)
            for s in cand:
                if seg_intersect(ax, ay, bx, by,
                                 seg[4 * s], seg[4 * s + 1],
                                 seg[4 * s + 2], seg[4 * s + 3]):
                    hits.add(s if dedup else (k, s))
        return len(hits)


if __name__ == "__main__":
    R = RailIndex()
    print("rail lines=%d segments=%d cells=%d build=%.1fs" %
          (R.nlines, R.nseg, len(R.idx), R.build_seconds))
