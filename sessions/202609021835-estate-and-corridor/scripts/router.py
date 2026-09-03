"""Graph loading, spatial snapping and A* routing over the OSM road graph."""
import array, os, math, json
from heapq import heappush, heappop
from common import haversine, HERE

GRAPH = os.path.join(HERE, "graph")


def _load(pre, name, typecode):
    a = array.array(typecode)
    path = os.path.join(GRAPH, pre + "." + name + ".bin")
    n = os.path.getsize(path) // a.itemsize
    with open(path, "rb") as fh:
        a.fromfile(fh, n)
    return a


class Graph:
    def __init__(self, pre="roads"):
        self.pre = pre
        self.nlat = _load(pre, "nlat", "d")
        self.nlon = _load(pre, "nlon", "d")
        self.indptr = _load(pre, "indptr", "q")
        self.indices = _load(pre, "indices", "q")
        self.weights = _load(pre, "weights", "d")
        self.eids = _load(pre, "eids", "q")
        self.comp = _load(pre, "comp", "q")
        self.gptr = _load(pre, "gptr", "q")
        self.gxy = _load(pre, "gxy", "d")
        self.meta = json.load(open(os.path.join(GRAPH, pre + ".meta.json")))
        self.n = len(self.nlat)
        # dominant component id
        counts = {}
        for c in self.comp:
            counts[c] = counts.get(c, 0) + 1
        self.giant_id = max(counts, key=counts.get)
        self._grid = None

    # ---------- spatial snap index ----------
    def build_snap_index(self, cell=0.02, giant_only=True):
        g = {}
        lat = self.nlat; lon = self.nlon; comp = self.comp; gid = self.giant_id
        for i in range(self.n):
            if giant_only and comp[i] != gid:
                continue
            k = (int(lat[i] / cell), int(lon[i] / cell))
            b = g.get(k)
            if b is None:
                g[k] = [i]
            else:
                b.append(i)
        self._grid = g
        self._cell = cell
        return len(g)

    def snap(self, la, lo, max_rings=60):
        """Nearest indexed node. Returns (node_id, distance_km)."""
        cell = self._cell; g = self._grid
        ci = int(la / cell); cj = int(lo / cell)
        best = -1; bestd = float("inf")
        r = 0
        while r <= max_rings:
            found_any = False
            for i in range(ci - r, ci + r + 1):
                for j in range(cj - r, cj + r + 1):
                    # only the ring perimeter after r=0
                    if r > 0 and abs(i - ci) != r and abs(j - cj) != r:
                        continue
                    b = g.get((i, j))
                    if not b:
                        continue
                    found_any = True
                    for nd in b:
                        d = haversine(la, lo, self.nlat[nd], self.nlon[nd])
                        if d < bestd:
                            bestd = d; best = nd
            # once something is found, expand two more rings to be safe,
            # because cell distance is not the same as great-circle distance
            if best >= 0 and r >= 2 and bestd < (r - 1) * cell * 111.0:
                break
            r += 1
            if best < 0 and r > max_rings:
                break
        return best, bestd

    # ---------- routing ----------
    def astar(self, src, dst, extra_cost=None):
        """A* with admissible great-circle heuristic.

        extra_cost: optional dict/list mapping edge id -> additional km-equivalent
                    penalty. Penalties are >= 0 so the heuristic stays admissible.
        Returns (cost_km, node_path) or (None, None).
        """
        if src == dst:
            return 0.0, [src]
        nlat = self.nlat; nlon = self.nlon
        indptr = self.indptr; indices = self.indices
        weights = self.weights; eids = self.eids
        tlat = nlat[dst]; tlon = nlon[dst]

        g = {src: 0.0}
        parent = {src: -1}
        closed = set()
        h0 = haversine(nlat[src], nlon[src], tlat, tlon)
        pq = [(h0, 0.0, src)]
        pops = 0
        while pq:
            f, gu, u = heappop(pq)
            if u in closed:
                continue
            closed.add(u)
            pops += 1
            if u == dst:
                path = []
                while u != -1:
                    path.append(u); u = parent[u]
                path.reverse()
                return gu, path
            for p in range(indptr[u], indptr[u + 1]):
                v = indices[p]
                if v in closed:
                    continue
                w = weights[p]
                if extra_cost is not None:
                    w += extra_cost[eids[p]]
                ng = gu + w
                if ng < g.get(v, float("inf")):
                    g[v] = ng
                    parent[v] = u
                    heappush(pq, (ng + haversine(nlat[v], nlon[v], tlat, tlon), ng, v))
        return None, None

    # ---------- helpers ----------
    def edge_between(self, u, v):
        """Return (weight, eid) for the edge u-v, or None."""
        for p in range(self.indptr[u], self.indptr[u + 1]):
            if self.indices[p] == v:
                return self.weights[p], self.eids[p]
        return None

    def path_legs(self, path):
        """Per-leg (weight, eid). Used for the leg-sum sanity check."""
        out = []
        for a, b in zip(path, path[1:]):
            e = self.edge_between(a, b)
            if e is None:
                raise RuntimeError("path uses a non-existent edge %d-%d" % (a, b))
            out.append(e)
        return out

    def edge_geometry(self, eid):
        """Flat [lon,lat,...] for one edge."""
        a = self.gptr[eid]; b = self.gptr[eid + 1]
        return self.gxy[2 * a:2 * b]

    def path_geometry(self, path):
        """Flat [lon,lat,...] for the whole routed path, orientation-corrected."""
        out = array.array("d")
        for a, b in zip(path, path[1:]):
            e = self.edge_between(a, b)
            gm = self.edge_geometry(e[1])
            pts = [(gm[2 * i], gm[2 * i + 1]) for i in range(len(gm) // 2)]
            # orient so the polyline starts at node a
            d_start = haversine(self.nlat[a], self.nlon[a], pts[0][1], pts[0][0])
            d_end = haversine(self.nlat[a], self.nlon[a], pts[-1][1], pts[-1][0])
            if d_end < d_start:
                pts.reverse()
            for (lo, la) in pts:
                out.append(lo); out.append(la)
        return out
