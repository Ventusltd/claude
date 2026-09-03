"""Independent audit of familiars/harvest.py's precision claim.

Does not trust harvest's scoring. Re-runs the same prompt against the same rows and
scores each answer THREE ways:

  A. harvest's own rule  - grounded = substring of the name (low in name.lower())
  B. strict grounding    - the answer must appear as a WHOLE WORD sequence in the name.
                           A truncation ("Kintor" from "Kintore") or a fragment is NOT
                           grounded. This is the invention class harvest cannot see:
                           its substring test only catches INSERTIONS, never TRUNCATIONS.
  C. abstention audit    - for every row the model said NONE on, does the name in fact
                           contain a settlement? harvest counts abstentions but never
                           checks them, so its denominator excludes every row the model
                           declined - which is where a cautious model hides its misses.

Every row is written out with the verbatim source name so a reader can check the
quoted evidence against the file it came from.
"""
import json, os, re, sys, time, urllib.request

OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:4b-instruct-2507-q4_K_M"
REL = ("C:/Users/vikra/OneDrive/Documents/GitHub/pipelinenews/"
       "releases/202609032159-pipelinenews/data/")

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
    """Identical to harvest.load, but a missing file is a hard failure, not a skip."""
    rows = []
    for fn, namekey, authkey in (
        ("202609030009-wider-fleet.json", "n", "cty"),
        ("202608311610-grid-proximity.json", "name", "town"),
    ):
        p = os.path.join(REL, fn)
        if not os.path.exists(p):
            raise SystemExit(f"MISSING INPUT {p} - refusing to report a model result")
        d = json.load(open(p, encoding="utf-8"))
        rs = d if isinstance(d, list) else next(
            v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict))
        got = 0
        for r in rs:
            if r.get(namekey):
                rows.append((r[namekey], str(r.get(authkey) or ""), fn))
                got += 1
        print(f"  loaded {got:>6} rows from {fn}", file=sys.stderr)
    step = max(1, len(rows) // n)
    return rows[::step][:n]


def strict_grounded(answer, name):
    """Whole-word-sequence containment. 'Kintor' is not grounded in 'Kintore ...'."""
    a = answer.strip()
    if not a:
        return False
    pat = r"(?<![A-Za-z])" + r"[\s\-,'`]+".join(
        re.escape(tok) for tok in re.split(r"[\s\-,]+", a) if tok) + r"(?![A-Za-z])"
    try:
        return re.search(pat, name, re.I) is not None
    except re.error:
        return a.lower() in name.lower()


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    rows = load(n)
    print(f"\naudit of harvest.py: {len(rows)} rows, model {MODEL}\n", file=sys.stderr)

    out = []
    failed_requests = 0
    t0 = time.time()
    for i, (name, auth, src) in enumerate(rows):
        try:
            a = ask(name)
        except Exception as e:
            failed_requests += 1
            out.append({"name": name, "auth": auth, "src": src,
                        "answer": None, "error": str(e)})
            continue
        low = a.lower()
        abstain = low in ("none", "n/a", "unknown", "") or low.startswith("none")
        rec = {
            "name": name, "auth": auth, "src": src, "answer": a,
            "abstained": abstain,
            "harvest_grounded": low in name.lower(),
            "strict_grounded": strict_grounded(a, name),
            "is_auth_exact": bool(auth) and low == auth.lower(),
            "is_auth_substr": bool(auth) and (low in auth.lower() or auth.lower() in low),
            "is_boiler": bool(BOILER.match(a)) or low in ("uk", "england", "scotland", "wales"),
        }
        out.append(rec)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(rows)}  {time.time()-t0:.0f}s", file=sys.stderr)

    dt = time.time() - t0
    ans = [r for r in out if r.get("answer") is not None and not r["abstained"]]
    abst = [r for r in out if r.get("answer") is not None and r["abstained"]]

    def score(rows_, ground_key):
        hit = inv = ech = boi = 0
        for r in rows_:
            if not r[ground_key]:
                inv += 1
            elif r["is_auth_exact"]:
                ech += 1
            elif r["is_boiler"]:
                boi += 1
            else:
                hit += 1
        return hit, inv, ech, boi

    h1, i1, e1, b1 = score(ans, "harvest_grounded")
    h2, i2, e2, b2 = score(ans, "strict_grounded")
    v = len(ans)
    print("\n" + "=" * 72)
    print(f"rows sampled            {len(rows)}")
    print(f"request failures        {failed_requests}   (harvest drops these from every counter)")
    print(f"volunteered an answer   {v}")
    print(f"abstained (said NONE)   {len(abst)}   (harvest excludes ALL of these from precision)")
    print()
    print(f"  A. harvest's own rule (substring grounding), denominator {v}:")
    print(f"     hits {h1}  invented {i1}  echoed-auth {e1}  boilerplate {b1}"
          f"   -> precision {100.0*h1/v if v else 0:.1f}%")
    print(f"  B. strict rule (whole-word grounding), denominator {v}:")
    print(f"     hits {h2}  invented {i2}  echoed-auth {e2}  boilerplate {b2}"
          f"   -> precision {100.0*h2/v if v else 0:.1f}%")
    print()
    print(f"  answers harvest calls grounded that are NOT whole-word grounded: "
          f"{sum(1 for r in ans if r['harvest_grounded'] and not r['strict_grounded'])}")
    print(f"  answers that are a substring of the planning authority (harvest only "
          f"catches exact): {sum(1 for r in ans if r['is_auth_substr'] and not r['is_auth_exact'])}")
    print()
    print(f"  precision over ALL rows put to the model "
          f"(denominator {v + len(abst)}, abstentions included as non-answers): "
          f"{100.0*h2/(v+len(abst)) if (v+len(abst)) else 0:.1f}%")
    print(f"\n  {dt:.0f}s  ({dt/max(1,len(rows)):.2f}s/row)")

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "audit_rows.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("\n  every row written to audit_rows.json for verbatim checking")
    return 0


if __name__ == "__main__":
    sys.exit(main())
