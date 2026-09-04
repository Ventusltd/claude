#!/usr/bin/env python3
"""Deterministic triage of arrival records.

The 4B local model was tried on this and failed the only test that matters: on
repd 15169 it returned NO_TECH_LAYER for a record whose own
project_layer_enabled field reads "bess", and said so in the same sentence. A
classifier that contradicts the field it is quoting is worse than no classifier,
because its output looks like evidence. Rules below; the GPU keeps the job it is
actually good at (bounded extraction over engine source, llama_layerscan.py).
"""
import json, pathlib, collections

HERE = pathlib.Path(__file__).parent
IN   = HERE / "journeys.jsonl"
OUT  = HERE / "triage.jsonl"

def classify(r):
    c = []
    fails = r.get("failures") or r.get("fail") or []
    if any("layer control not found" in str(f) for f in fails):
        c.append("NO_TECH_LAYER")
    if r.get("project_layer_enabled") in (None, "", "null") and not c:
        c.append("TECH_LAYER_UNRESOLVED")
    if r.get("links_drawn") == 0:
        c.append("NO_LINKS_DRAWN")
    if r.get("attribReadable") is False:
        c.append("ATTRIBUTION_COVERED")
    if r.get("answerOnFirstScreen") is False:
        c.append("ANSWER_BELOW_FOLD")
    if any("had not rendered its layer controls" in str(f) for f in fails):
        c.append("ARTEFACT_HIDDEN_TAB" if r.get("visibilityState") == "hidden" else "SLOW_LAYER_CONTROLS")
    return c or ["OK"]

def main():
    rows, out = [], []
    for line in IN.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line: continue
        try: rows.append(json.loads(line))
        except Exception: pass
    counts = collections.Counter()
    by_tech = collections.defaultdict(collections.Counter)
    for r in rows:
        cs = classify(r)
        for x in cs:
            counts[x] += 1
            by_tech[r.get("tech")][x] += 1
        out.append({"repd": r.get("repd"), "tech": r.get("tech"),
                    "observer": r.get("observer"), "classes": cs})
    OUT.write_text("\n".join(json.dumps(o) for o in out) + "\n", encoding="utf-8")
    print("records:", len(rows))
    print("totals:", dict(counts))
    for t, c in sorted(by_tech.items(), key=lambda kv: str(kv[0])):
        print("  %-16s %s" % (t, dict(c)))

if __name__ == "__main__":
    main()
