#!/usr/bin/env python3
"""Two local qwen3 workers triage GridAtlas deep-link arrival records.

Input : journeys.jsonl  (one arrival record per line, written by the Chrome pilot)
Output: triage.jsonl    (one classification per record)

The pilot measures; the workers only classify what was measured. A worker that
cannot answer from the record writes {"class":"UNCLASSIFIED"} rather than guessing.
"""
import json, os, sys, time, threading, urllib.request, pathlib

HERE = pathlib.Path(__file__).parent
IN   = HERE / "journeys.jsonl"
OUT  = HERE / "triage.jsonl"
MODEL = os.environ.get("TRIAGE_MODEL", "qwen3:4b-instruct-2507-q4_K_M")
HOST  = "http://127.0.0.1:11434/api/generate"

CLASSES = [
 "OK",                    # card + links + no failures
 "NO_TECH_LAYER",         # failures mention 'layer control not found'
 "NO_LINKS_DRAWN",        # links_drawn == 0
 "NO_CARD",               # card text missing the project
 "DEAD_MAP",              # map found false / centre is the default UK view
 "ATTRIBUTION_COVERED",   # attribution.isAttrib false
 "ZOOM_IGNORED",          # url zoom != map zoom
 "UNCLASSIFIED",
]

PROMPT = """You classify one GridAtlas deep-link arrival record. Answer with JSON only.

Allowed classes: %s

Rules:
- Use ONLY the fields present in the record. Never invent a field.
- More than one class may apply; list every one that the record supports.
- If the record does not let you decide, answer ["UNCLASSIFIED"].

Record:
%s

Answer JSON: {"classes":[...],"why":"<one short sentence quoting a field>"}"""

lock = threading.Lock()

def ask(rec):
    body = json.dumps({
        "model": MODEL,
        "prompt": PROMPT % (", ".join(CLASSES), json.dumps(rec, sort_keys=True)),
        "stream": False,
        "options": {"temperature": 0, "num_ctx": 4096},
    }).encode()
    req = urllib.request.Request(HOST, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["response"]

def worker(name, queue):
    while True:
        with lock:
            if not queue: return
            rec = queue.pop(0)
        t0 = time.time()
        try:
            raw = ask(rec)
            s, e = raw.find("{"), raw.rfind("}")
            got = json.loads(raw[s:e+1]) if s >= 0 else {"classes": ["UNCLASSIFIED"]}
        except Exception as ex:
            got = {"classes": ["UNCLASSIFIED"], "why": "worker error: %s" % ex}
        got.update(worker=name, repd=rec.get("repd"), secs=round(time.time()-t0, 1), model=MODEL)
        with lock:
            with OUT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(got) + "\n")
        print("[%s] %s -> %s (%.1fs)" % (name, rec.get("repd"), got.get("classes"), got["secs"]), flush=True)

def main():
    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            try: done.add(json.loads(line)["repd"])
            except Exception: pass
    if not IN.exists():
        print("no journeys.jsonl yet"); return
    queue = []
    for line in IN.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line: continue
        try: rec = json.loads(line)
        except Exception: continue
        if rec.get("repd") in done: continue
        queue.append(rec)
    print("queued %d records for %s" % (len(queue), MODEL), flush=True)
    ts = [threading.Thread(target=worker, args=("w%d" % i, queue), daemon=False) for i in (1, 2)]
    for t in ts: t.start()
    for t in ts: t.join()
    print("done", flush=True)

def loop():
    while True:
        try:
            main()
        except Exception as ex:
            print("cycle error: %s" % ex, flush=True)
        time.sleep(5)

if __name__ == "__main__":
    loop()
