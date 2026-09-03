"""Build a routable road graph from OSM primary + trunk roads.

Strategy (memory-conscious, pure Python -- numpy is not installed):
  1. Parse each GeoJSON once, flatten every LineString into a flat array('d')
     of lon/lat pairs plus an array('l') of way start offsets. Drop properties
     and the parsed JSON immediately.
  2. Count how many times each rounded vertex (1e-6 deg, OSM native precision)
     is referenced. A vertex is a JUNCTION if referenced by >= 2 way-positions
     or if it is a way endpoint.
  3. Contract each way into edges between consecutive junctions, carrying the
     true geodesic length (haversine, R = 6371.0088 km) summed over every
     intermediate shape point.
  4. Emit CSR adjacency + node coordinate arrays to a binary file.
"""
import json, os, sys, time, array, gc
from collections import defaultdict
from common import haversine, HERE

CLONES = r"C:\Users\vikra\AppData\Local\Temp\claude\C--Users-vikra\5b94bee7-197b-4cfd-944b-d4cf3aa02d18\scratchpad\clones"
GG = os.path.join(CLONES, "globalgrid2050")
OUT = os.path.join(HERE, "graph")
SCALE = 1_000_000  # 1e-6 degree rounding


def read_blob(path):
    import subprocess
    p = subprocess.run(["git", "-C", GG, "show", "gh/main:" + path],
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:500])
    return p.stdout


def flatten_geojson(paths):
    """Return (coords array('d') of lon,lat pairs, way_start array('l'))."""
    coords = array.array("d")
    starts = array.array("q")
    nfeat = 0
    for path in paths:
        t0 = time.time()
        raw = read_blob(path)
        gj = json.loads(raw)
        del raw
        feats = gj["features"]
        for f in feats:
            g = f.get("geometry")
            if not g:
                continue
            gt = g.get("type")
            if gt == "LineString":
                lines = [g["coordinates"]]
            elif gt == "MultiLineString":
                lines = g["coordinates"]
            else:
                continue
            for ln in lines:
                if len(ln) < 2:
                    continue
                starts.append(len(coords) // 2)
                for pt in ln:
                    coords.append(pt[0]); coords.append(pt[1])
                nfeat += 1
        del gj, feats
        gc.collect()
        print("  parsed %-32s ways=%d pts=%d  %.1fs" %
              (path, nfeat, len(coords) // 2, time.time() - t0), flush=True)
    starts.append(len(coords) // 2)  # sentinel
    return coords, starts


def key_of(lon, lat):
    return (int(round(lat * SCALE)) + 90_000_000) * 400_000_000 + \
           (int(round(lon * SCALE)) + 180_000_000)


def build(paths, out_prefix):
    t_all = time.time()
    print("[1/4] parsing geojson", flush=True)
    coords, starts = flatten_geojson(paths)
    nways = len(starts) - 1
    npts = len(coords) // 2
    print("  ways=%d shape-points=%d" % (nways, npts), flush=True)

    print("[2/4] counting vertex references", flush=True)
    t0 = time.time()
    cnt = defaultdict(int)
    keys = array.array("q", bytes(8 * npts))  # cache key per shape point
    for w in range(nways):
        a = starts[w]; b = starts[w + 1]
        for i in range(a, b):
            k = key_of(coords[2 * i], coords[2 * i + 1])
            keys[i] = k
            cnt[k] += 1
        # way endpoints are always junctions
        cnt[keys[a]] += 2
        cnt[keys[b - 1]] += 2
    print("  unique vertices=%d  %.1fs" % (len(cnt), time.time() - t0), flush=True)

    print("[3/4] assigning junction ids + contracting ways", flush=True)
    t0 = time.time()
    nid = {}
    nlat = array.array("d"); nlon = array.array("d")
    edges = {}   # (u,v) u<v -> min length km
    geoms = {}   # (u,v) -> array('d') of lon,lat pairs INCLUDING both junctions

    def get_id(k, lon, lat):
        j = nid.get(k)
        if j is None:
            j = len(nlat)
            nid[k] = j
            nlon.append(lon); nlat.append(lat)
        return j

    for w in range(nways):
        a = starts[w]; b = starts[w + 1]
        prev_j = None
        acc = 0.0
        seg = array.array("d")
        plon = coords[2 * a]; plat = coords[2 * a + 1]
        for i in range(a, b):
            lon = coords[2 * i]; lat = coords[2 * i + 1]
            if i > a:
                acc += haversine(plat, plon, lat, lon)
            plat = lat; plon = lon
            if prev_j is not None:
                seg.append(lon); seg.append(lat)
            k = keys[i]
            if cnt[k] >= 2:  # junction
                j = get_id(k, lon, lat)
                if prev_j is not None and j != prev_j and acc > 0.0:
                    e = (prev_j, j) if prev_j < j else (j, prev_j)
                    old = edges.get(e)
                    if old is None or acc < old:
                        edges[e] = acc
                        g = array.array("d", [nlon[prev_j], nlat[prev_j]])
                        g.extend(seg)
                        geoms[e] = g
                prev_j = j
                acc = 0.0
                seg = array.array("d")
    del cnt, keys, coords, starts
    gc.collect()
    nnodes = len(nlat)
    print("  nodes=%d edges=%d  %.1fs" % (nnodes, len(edges), time.time() - t0), flush=True)

    print("[4/4] building CSR + connected components", flush=True)
    t0 = time.time()
    deg = array.array("q", bytes(8 * (nnodes + 1)))
    for (u, v) in edges:
        deg[u + 1] += 1; deg[v + 1] += 1
    for i in range(nnodes):
        deg[i + 1] += deg[i]
    indptr = array.array("q", deg)
    fill = array.array("q", deg[:nnodes])
    m = len(edges)
    indices = array.array("q", bytes(8 * 2 * m))
    weights = array.array("d", bytes(8 * 2 * m))
    eids = array.array("q", bytes(8 * 2 * m))
    gptr = array.array("q", [0])
    gxy = array.array("d")
    for eid, ((u, v), wgt) in enumerate(edges.items()):
        p = fill[u]; indices[p] = v; weights[p] = wgt; eids[p] = eid; fill[u] = p + 1
        p = fill[v]; indices[p] = u; weights[p] = wgt; eids[p] = eid; fill[v] = p + 1
        gxy.extend(geoms[(u, v)])
        gptr.append(len(gxy) // 2)
    del edges, geoms, fill, deg
    gc.collect()

    # connected components (iterative BFS)
    comp = array.array("q", [-1]) * nnodes
    sizes = []
    for s in range(nnodes):
        if comp[s] != -1:
            continue
        cid = len(sizes)
        comp[s] = cid
        stack = [s]; n = 0
        while stack:
            u = stack.pop(); n += 1
            for p in range(indptr[u], indptr[u + 1]):
                v = indices[p]
                if comp[v] == -1:
                    comp[v] = cid; stack.append(v)
        sizes.append(n)
    giant = max(sizes)
    print("  components=%d giant=%d (%.2f%% of nodes)  %.1fs" %
          (len(sizes), giant, 100.0 * giant / nnodes, time.time() - t0), flush=True)

    os.makedirs(OUT, exist_ok=True)
    pre = os.path.join(OUT, out_prefix)
    for name, arr in (("nlat", nlat), ("nlon", nlon), ("indptr", indptr),
                      ("indices", indices), ("weights", weights), ("comp", comp),
                      ("eids", eids), ("gptr", gptr), ("gxy", gxy)):
        with open(pre + "." + name + ".bin", "wb") as fh:
            arr.tofile(fh)
    meta = {"nodes": nnodes, "edges": m, "components": len(sizes),
            "giant": giant, "giant_frac": giant / nnodes,
            "shape_points": npts, "ways": nways,
            "build_seconds": round(time.time() - t_all, 1),
            "sources": paths,
            "total_edge_km": round(sum(weights) / 2.0, 1)}
    json.dump(meta, open(pre + ".meta.json", "w"), indent=1)
    print(json.dumps(meta, indent=1))
    return meta


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "roads"
    if which == "roads":
        build(["uk_primary_roads.geojson", "uk_trunk_roads.geojson"], "roads")
    elif which == "roads_mw":
        build(["uk_primary_roads.geojson", "uk_trunk_roads.geojson",
               "uk_motorways.geojson"], "roads_mw")
