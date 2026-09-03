"""Precompute, for every road edge, how many railway segments it crosses.

Windows-safe multiprocessing: worker lives in a real module with a __main__ guard.
"""
import os, json, array, time, sys
from concurrent.futures import ProcessPoolExecutor
from common import HERE

_G = None
_R = None


def _init(pre):
    global _G, _R
    from router import Graph
    from rail import RailIndex
    _G = Graph(pre)
    _R = RailIndex()


def _chunk(args):
    lo, hi = args
    G = _G; R = _R
    out = []
    for eid in range(lo, hi):
        gm = G.edge_geometry(eid)
        if len(gm) < 4:
            continue
        n = R.count_crossings(gm)
        if n:
            out.append((eid, n))
    return out


def main(pre="roads", workers=10):
    from router import Graph
    G = Graph(pre)
    m = G.meta["edges"]
    del G
    step = (m + workers * 4 - 1) // (workers * 4)
    tasks = [(i, min(i + step, m)) for i in range(0, m, step)]
    t0 = time.time()
    counts = array.array("i", bytes(4 * m))
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init, initargs=(pre,)) as ex:
        done = 0
        for res in ex.map(_chunk, tasks):
            for eid, n in res:
                counts[eid] = n
            done += 1
            print("  chunk %d/%d  %.0fs" % (done, len(tasks), time.time() - t0), flush=True)
    nz = sum(1 for c in counts if c)
    tot = sum(counts)
    print("edges=%d crossing_edges=%d (%.2f%%) total_crossings=%d  %.0fs" %
          (m, nz, 100.0 * nz / m, tot, time.time() - t0))
    with open(os.path.join(HERE, "graph", pre + ".railcnt.bin"), "wb") as fh:
        counts.tofile(fh)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "roads")
