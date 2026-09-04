#!/usr/bin/env python3
"""Worker 2: read the GridAtlas engine on the GPU and report every layer id it registers.

The deep-link defect is that Pipeline News emits technology buckets the engine has no
layer for. Deciding that by hand across ~3.5 MB of cartridge source is what a local
model is actually good for: many small, bounded reads with one narrow question.

Deterministic extraction stays in Python (regex over addLayer/setLayoutProperty ids).
The model's job is the part regex cannot do: say, for each chunk, which ids are
PROJECT technology layers as opposed to basemap, substation, circuit or decoration
layers, and quote the line it read that from.
"""
import json, os, re, sys, time, threading, urllib.request, pathlib, glob

HERE  = pathlib.Path(__file__).parent
OUT   = HERE / "layerscan.jsonl"
MODEL = os.environ.get("SCAN_MODEL", "qwen3:4b-instruct-2507-q4_K_M")
HOST  = "http://127.0.0.1:11434/api/generate"
ATLAS = pathlib.Path(r"C:\Users\vikra\OneDrive\Documents\GitHub\gridatlas\atlas")

ID_RE = re.compile(r"""["']([a-z0-9_\-]{3,60})["']""")
HINT  = re.compile(r"addLayer|setLayoutProperty|getLayer|layer\s*id|PROJECT_TECHS|TECH_LABEL|layerId|toggleLayer", re.I)

PROMPT = """You are reading one chunk of the GridAtlas map engine. Answer with JSON only.

Question: which of these candidate string ids are PROJECT TECHNOLOGY layers - layers that
light up the renewable-energy projects of one technology (solar, battery, wind, biomass,
hydrogen and so on)? Exclude basemap, label, substation, circuit, transformer, boundary,
route, halo, glow and decoration layers.

Rules:
- Judge ONLY from the chunk below. Never invent an id that is not in the candidate list.
- For every id you return, quote the substring of the chunk you read it from.
- If the chunk does not show what a id is for, leave it out.

Candidate ids: %s

Chunk:
%s

Answer JSON: {"project_technology_layers":[{"id":"...","evidence":"..."}]}"""

lock = threading.Lock()

def ask(prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0, "num_ctx": 8192}}).encode()
    req = urllib.request.Request(HOST, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["response"]

def chunks_of(path, size=6000, overlap=400):
    txt = path.read_text(encoding="utf-8", errors="replace")
    i = 0
    while i < len(txt):
        c = txt[i:i+size]
        if HINT.search(c):
            yield i, c
        i += size - overlap

def worker(name, queue):
    while True:
        with lock:
            if not queue: return
            path, off, chunk = queue.pop(0)
        cands = sorted({m for m in ID_RE.findall(chunk)})[:120]
        if not cands:
            continue
        t0 = time.time()
        try:
            raw = ask(PROMPT % (", ".join(cands), chunk))
            s, e = raw.find("{"), raw.rfind("}")
            got = json.loads(raw[s:e+1]) if s >= 0 else {"project_technology_layers": []}
        except Exception as ex:
            got = {"project_technology_layers": [], "error": str(ex)}
        got.update(worker=name, file=path.name, offset=off, secs=round(time.time()-t0, 1), model=MODEL)
        with lock:
            with OUT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(got) + "\n")
        n = len(got.get("project_technology_layers") or [])
        print("[%s] %s@%d -> %d layer ids (%.1fs)" % (name, path.name, off, n, got["secs"]), flush=True)

def targets():
    """Every cartridge, part and module in the repo - the whole engine corpus.

    The live composition is only four files; the question "which layer ids exist"
    is answered by the whole lineage, because ids are added and dropped across
    generations and the Pipeline buckets were written against an older one.
    """
    seen, paths = set(), []
    for sub in ("cartridges", "parts", "modules"):
        for p in sorted((ATLAS / sub).glob("*.js")):
            if p.stat().st_size > 2000 and p.name not in seen:
                seen.add(p.name)
                paths.append(p)
    return paths

def main():
    queue = []
    for p in targets():
        for off, c in chunks_of(p):
            queue.append((p, off, c))
    print("queued %d chunks from %d files for %s" % (len(queue), len(targets()), MODEL), flush=True)
    ts = [threading.Thread(target=worker, args=("scan%d" % i, queue)) for i in (1, 2)]
    for t in ts: t.start()
    for t in ts: t.join()
    print("scan complete", flush=True)

def loop():
    while True:
        try:
            main()
        except Exception as ex:
            print("cycle error: %s" % ex, flush=True)
        time.sleep(3)

if __name__ == "__main__":
    loop()
