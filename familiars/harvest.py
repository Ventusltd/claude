"""harvest.py - measure whether the local model is worth harvesting, on a real estate defect.

WHY THIS EXISTS

The estate carries a known defect: the spine field called `town` is the PLANNING AUTHORITY,
not the settlement. "Aberdeenshire" is not where a project is; it is who decides it. Any card
that prints that field as a location is telling the reader something false.

The settlement is usually present, but only as free text inside the project name:

    "The Kintore Hydrogen Project, Kintore - Hydrogen Plant"   -> Kintore
    "Ewe Hill Wind Farm Extension II"                          -> (none; no settlement stated)

That is fuzzy extraction over messy human strings, which is the one shape of work a small
local model can plausibly do better than a regex - and the one shape where it is easy to
fool yourself into believing it did. So this does not ask the model to do the job. It asks
whether the model CAN do the job, and prints a number.

THE SCORING RULE

A model answer is only counted correct if it survives three checks that need no gazetteer:

  1. GROUNDED  - the answer appears verbatim in the source name. A locality the model
                 invented is the failure mode that matters, and it is invisible unless
                 tested for explicitly.
  2. NOT THE AUTHORITY - the answer is not just the planning authority echoed back. That is
                 the defect we are trying to fix; reproducing it is not a fix.
  3. NOT BOILERPLATE - the answer is not a technology or project word ("Solar Farm",
                 "Hydrogen Plant", "Extension"). A model that returns the tech word scores
                 well on grounding while being useless.

ABSTENTION IS CORRECT. Many names contain no settlement at all. A model that says NONE on
those is right, and a model that invents something is worse than useless - it would write a
false locality into a shipping product. So abstention is scored separately from accuracy,
and a high invention rate fails the harvest regardless of how good the hits look.

WHAT THE NUMBER MEANS

Precision here is: of the answers the model volunteered, how many were real, grounded,
non-authority localities. Ship the model into the pipeline only if precision is high AND
invention is near zero. A model that is right 70% of the time is not usable for a field a
reader will trust - it is a machine for generating plausible wrong towns.

Usage:
    python familiars/harvest.py            # 40 rows
    python familiars/harvest.py 120        # more
"""
import json, os, re, sys, time, urllib.request, collections

OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:4b-instruct-2507-q4_K_M"
REL = ("/c/Users/vikra/OneDrive/Documents/GitHub/pipelinenews/"
       "releases/202609032159-pipelinenews/data/")
REL = os.environ.get("PN_DATA", REL.replace("/c/", "C:/"))

BOILER = re.compile(
    r"^(the|a|an)?\s*(solar|wind|hydro|hydrogen|biomass|tidal|geothermal|battery|bess|"
    r"energy|power|farm|park|plant|project|station|storage|extension|scheme|site|ltd|"
    r"limited|repowering|onshore|offshore|anaerobic|digestion|landfill|gas|efw|"
    r"incineration|sewage|sludge|pumped|small|large|stream|wave|advanced|conversion)"
    r"[\s\-]*", re.I)


def ask(name, timeout=90):
    body = json.dumps({
        "model": MODEL,
        "prompt": (
            "Extract the SETTLEMENT (town, village or hamlet) from this UK energy project "
            "name. Reply with the settlement only, nothing else. If the name states no "
            "settlement, reply exactly: NONE\n\n"
            f"Name: {name}\nSettlement:"),
        "stream": False,
        "options": {"num_ctx": 16384, "temperature": 0, "num_predict": 16},
    }).encode()
    req = urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)["response"].strip().strip('."').split("\n")[0]


def load(n):
    rows = []
    for fn, namekey, authkey in (
        ("202609030009-wider-fleet.json", "n", "cty"),
        ("202608311610-grid-proximity.json", "name", "town"),
    ):
        p = os.path.join(REL, fn)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        rs = d if isinstance(d, list) else next(
            v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict))
        for r in rs:
            if r.get(namekey):
                rows.append((r[namekey], str(r.get(authkey) or ""), fn.split("-")[-1][:-5]))
    # deterministic spread across both files rather than the first N of one
    step = max(1, len(rows) // n)
    return rows[::step][:n]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    rows = load(n)
    print(f"harvest test: {len(rows)} project names, model {MODEL}\n")

    volunteered = hit = invented = echoed = boiler = 0
    abstained = 0
    examples, misses = [], []
    t0 = time.time()

    for name, auth, src in rows:
        try:
            a = ask(name)
        except Exception as e:
            print("  request failed:", e)
            continue
        low = a.lower()
        if low in ("none", "n/a", "unknown", "") or low.startswith("none"):
            abstained += 1
            continue
        volunteered += 1
        grounded = low in name.lower()
        is_auth = auth and low == auth.lower()
        is_boiler = bool(BOILER.match(a)) or low in ("uk", "england", "scotland", "wales")
        if not grounded:
            invented += 1
            misses.append((name, a, "INVENTED - not in the name"))
        elif is_auth:
            echoed += 1
            misses.append((name, a, "echoed the planning authority"))
        elif is_boiler:
            boiler += 1
            misses.append((name, a, "boilerplate/tech word"))
        else:
            hit += 1
            if len(examples) < 6:
                examples.append((name, a))

    dt = time.time() - t0
    print(f"  answered      {volunteered:>4}   abstained (said NONE) {abstained}")
    print(f"  usable hits   {hit:>4}")
    print(f"  INVENTED      {invented:>4}   <- not present in the source name")
    print(f"  echoed auth   {echoed:>4}")
    print(f"  boilerplate   {boiler:>4}")
    prec = 100.0 * hit / volunteered if volunteered else 0.0
    invrate = 100.0 * invented / volunteered if volunteered else 0.0
    print(f"\n  precision  {prec:5.1f}%   invention {invrate:5.1f}%   {dt:.0f}s "
          f"({dt/max(1,len(rows)):.2f}s/row)")

    if examples:
        print("\n  hits:")
        for nm, a in examples:
            print(f"    {a:<22} <- {nm[:70]}")
    if misses:
        print("\n  failures:")
        for nm, a, why in misses[:6]:
            print(f"    {a:<22} <- {nm[:56]}  [{why}]")

    print()
    if volunteered == 0:
        print("  VERDICT: model abstained on everything. Nothing to harvest.")
    elif prec >= 90 and invrate <= 2:
        print("  VERDICT: HARVEST. Precision high and invention near zero.")
    elif invrate > 10:
        print(f"  VERDICT: DISCARD. {invrate:.0f}% invention would write false localities "
              "into a shipping field.")
    else:
        print(f"  VERDICT: NOT YET. {prec:.0f}% precision is not good enough for a field a "
              "reader trusts. Usable only behind human review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
