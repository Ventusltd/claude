"""Verify every audited row against the SOURCE FILE it claims to come from.

Not against a re-parse of my own loader - against the raw bytes of the release JSON.
A row is only confirmed if:
  - the project name occurs verbatim, as a JSON string, in the file named in `src`
  - the model's answer occurs verbatim inside that project name
"""
import json, os, sys

REL = ("C:/Users/vikra/OneDrive/Documents/GitHub/pipelinenews/"
       "releases/202609032159-pipelinenews/data/")
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "audit_rows.json"), encoding="utf-8"))

raw = {}
for fn in ("202609030009-wider-fleet.json", "202608311610-grid-proximity.json"):
    with open(os.path.join(REL, fn), "rb") as fh:
        raw[fn] = fh.read()
    print(f"  {fn}: {len(raw[fn])} bytes read")

name_ok = name_bad = ans_ok = ans_bad = 0
answered = [r for r in rows if r.get("answer") is not None and not r.get("abstained")]
for r in answered:
    blob = raw[r["src"]]
    # the name must be present as a JSON string value in the raw bytes
    needle = json.dumps(r["name"], ensure_ascii=False).encode("utf-8")
    if needle in blob:
        name_ok += 1
    else:
        name_bad += 1
        print(f"  NAME NOT IN SOURCE: {r['name'][:70]!r}  ({r['src']})")
    if r["answer"].lower() in r["name"].lower():
        ans_ok += 1
    else:
        ans_bad += 1
        print(f"  ANSWER NOT IN NAME: {r['answer']!r} <- {r['name'][:70]!r}")

print(f"\n  answered rows checked          {len(answered)}")
print(f"  project name verbatim in source {name_ok} confirmed / {name_bad} absent")
print(f"  answer verbatim inside the name {ans_ok} confirmed / {ans_bad} absent")

print("\n  --- 10 sampled rows, verbatim ---")
for r in answered[:10]:
    print(f"    {r['answer']:<20} <- {r['name'][:62]}")
    print(f"       auth={r['auth']!r} strict={r['strict_grounded']} "
          f"auth_substr={r['is_auth_substr']} src={r['src']}")

sus = [r for r in answered if r["is_auth_substr"] and not r["is_auth_exact"]]
if sus:
    print("\n  --- answers that are a SUBSTRING of the planning authority ---")
    for r in sus:
        print(f"    answer={r['answer']!r} auth={r['auth']!r} name={r['name'][:60]!r}")
        print(f"       harvest scores this a HIT (it only compares exact equality)")

errs = [r for r in rows if r.get("answer") is None]
print(f"\n  --- {len(errs)} request failures harvest would have dropped silently ---")
for r in errs[:4]:
    print(f"    {r['error'][:100]}")
