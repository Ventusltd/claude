# Asymmetric ONSHORE/OFFSHORE handling in the ETYS→geometry join

**For whoever implements this in `data-grid-gb/derived/build_connection_points.py`.**

Written by the independent auditor of commit `b91e45b231464c24339f5a58b81e6b1eb4c8b47f`
(`20260903: correct transformer identity and fail-closed joins`, branch
`codex/20260903-phase0-integrity`, unpushed as of 03:00 UTC). Every number below
was measured; each has its reproduction command attached. Nothing here needs to
be taken on trust.

---

## 1. The trade as it stands

`b91e45b` changes located connection points **502 → 489**: sixteen rejections
against three gains, net −13.

```bash
cd data-grid-gb
python - <<'PY'
import json,subprocess
new=json.load(open("derived/connection-points.v3.json"))
old=json.loads(subprocess.run(["git","show","1c9909d:derived/connection-points.v3.json"],
      capture_output=True,text=True).stdout)
O={p["site_code"]:p for p in old["connection_points"]}
N={p["site_code"]:p for p in new["connection_points"]}
lost=[c for c in O if O[c].get("location") and not N[c].get("location")]
gained=[c for c in O if not O[c].get("location") and N[c].get("location")]
moved=[c for c in O if O[c].get("location") and N[c].get("location")
       and O[c]["location"]!=N[c]["location"]]
print(old["counts"]["with_location"],"->",new["counts"]["with_location"])
print("lost",len(lost),sorted(lost)); print("gained",len(gained),sorted(gained))
print("moved",len(moved))
PY
```

The headline reading — "thirteen unsafe bindings removed" — is wrong. Measured
against evidence outside the product, **the change loses eleven true coordinates
to remove five genuine duplicates.**

### The five rejections that are correct

In each case two ETYS sites held one OSM feature and the **more specific sibling
kept the exact point**. Releasing the other is the fix working as designed.

| rejected | sibling that retains the exact coordinate | mapped feature |
|---|---|---|
| `AREX` ARECLEOCH EXTENSION | `AREC` ARECLEOCH | Arecleoch Wind Farm Substation |
| `BLEX` BHLARAIDH EXTENSION | `BHLA` BHLARAIDH WIND FARM | Bhlaraidh Substation |
| `GREG` GREATER GABBARD OFFSHORE | `GGON` GREATER GABBARD ONSHORE | Greater Gabbard Onshore Substation |
| `MOWE` MORAY EAST OFFSHORE | `MORO` MORAY EAST ONSHORE | Moray East Onshore substation |
| `ORMW` ORMONDE OFFSHORE | `ORMO` ORMONDE ONSHORE | Ormonde onshore substation |

```bash
python - <<'PY'
import json,subprocess
new=json.load(open("derived/connection-points.v3.json"))
old=json.loads(subprocess.run(["git","show","1c9909d:derived/connection-points.v3.json"],
      capture_output=True,text=True).stdout)
O={p["site_code"]:p for p in old["connection_points"]}
N={p["site_code"]:p for p in new["connection_points"]}
for rej,keep in (("AREX","AREC"),("BLEX","BHLA"),("GREG","GGON"),
                 ("MOWE","MORO"),("ORMW","ORMO")):
    lo=O[rej]["location"]; ks=N[keep].get("location")
    same = ks and abs(ks["lat"]-lo["lat"])<1e-6 and abs(ks["lon"]-lo["lon"])<1e-6
    print(f"{rej}->{keep}: released={N[rej].get('location') is None}, "
          f"sibling keeps exact point={bool(same)}")
PY
```

**All five are decided by the sibling-claim test, not by the shore words.** None
of them depends on `qualifier_compatible()`. They therefore survive the change
specified in §3 unchanged — **nothing good is lost by holding the merge.** That
is the central point: the correct half of this commit is not hostage to the
incorrect half.

### Two more where the point was abandoned by both claimants

`BOSO` BARROW ONSHORE and `BOSW` BARROW OFFSHORE both held
(54.123477, −3.229975). Both were released and **no ETYS site now claims it**.
Fail-closed is defensible here — the mapped feature is named only `"Barrow"` and
carries no qualifier, so neither claimant can be preferred — but the result is a
mapped, grid-connected substation orphaned. Treat as acceptable-for-now, not as
correct.

---

## 2. The nine ONSHORE sites released with no rival claim

These are the loss. Every one is the **onshore grid connection point of an
offshore wind farm** — the land-based substation where the export cable makes
landfall and meets the transmission network.

| code | ETYS name | released coordinate's mapped feature | km to OHL network |
|---|---|---|---:|
| `BBWO` | BURBO BANK EXTENSION ONSHORE | Burbo Bank Offshore Wind Farm Substation | 0.02 |
| `SGRX` | SEAGREEN ONE 275KV ONSHORE | Seagreen Wind Farm Substation | 0.02 |
| `BEAT` | BEATRICE ONSHORE | Beatrice Wind Farm Substation | 0.04 |
| `TKNO` | TRITON KNOLL ONSHORE | Triton Knoll Wind Farm Substation | 0.05 |
| `NNGO` | NEART NA GAOITHE ONSHORE | Neart na Gaoithe Wind Farm Substation | 0.08 |
| `LONO` | LONDON ARRAY ONSHORE | London Array OWF substation | 0.09 |
| `HOWB` | HORNSEA TWO ONSHORE | Hornsea Two Offshore Wind Farm Substation | 0.11 |
| `WDSO` | WEST OF DUDDON SANDS ONSHORE | West of Duddon Sands Wind Farm Substation | 0.11 |
| `EACO` | EAST ANGLIA THREE ONSHORE | East Anglia THREE Converter Station | 0.12 |

For each, I checked every sibling ETYS site of the same project: `BBWW`, `SGRO`,
`BEIW`, `TKNE`/`TKNW`, `NNGW`, `LOAW`/`LOYW`, `HOWA`/`HOWC`/`HOWD`, `WDSW`,
`EAAW`/`EABO`/`EANO`/`EANW` are **all unlocated**. Nothing took the released
coordinate. Nine mapped substation features are now bound to nothing.

**Why this is the wrong direction.** An offshore platform may legitimately have
no land coordinate — it is at sea, often unmapped, and refusing to locate it is
correct conservatism. An **onshore** connection point is the opposite case: it is
definitionally on land, it is a large fenced compound sitting directly on the
transmission network, and it is among the most reliably locatable assets in the
whole model. The measurement confirms this — **all sixteen released coordinates
lie within 120 m of the GB 400/275/132 kV overhead-line network**, so every one
was a real onshore substation and not one was an offshore platform:

```bash
cd data-grid-gb && python - <<'PY'
import json,math,os,subprocess
base=r"C:\Users\vikra\OneDrive\Documents\GitHub\globalgrid2050"
pts=[]
for n in ("grid_400kv.geojson","grid_275kv.geojson","grid_132kv.geojson"):
    for f in json.load(open(os.path.join(base,n),encoding="utf-8"))["features"]:
        g=f.get("geometry") or {}
        if g.get("type")=="LineString": pts.extend(g["coordinates"])
        elif g.get("type")=="MultiLineString":
            for p in g["coordinates"]: pts.extend(p)
R=6371008.8
def hav(a,b,c,d):
    p1,p2=math.radians(a),math.radians(c)
    h=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(math.radians(d-b)/2)**2
    return 2*R*math.asin(math.sqrt(h))/1000
old=json.loads(subprocess.run(["git","show","1c9909d:derived/connection-points.v3.json"],
      capture_output=True,text=True).stdout)
O={p["site_code"]:p for p in old["connection_points"]}
for c in ["AREX","BBWO","BEAT","BLEX","BOSO","BOSW","EACO","GREG","HOWB",
          "LONO","MOWE","NNGO","ORMW","SGRX","TKNO","WDSO"]:
    l=O[c]["location"]
    print(f"{c:<6} {min(hav(l['lat'],l['lon'],y,x) for x,y in pts
          if abs(y-l['lat'])<0.6 and abs(x-l['lon'])<1.0):7.2f} km")
PY
```

Refusing a location to the most locatable class of asset in the model, in order
to avoid mislocating the least locatable class, is a trade in the wrong
direction. The three gains (`WLEE`/`WLEX` at two distinct coordinates 8.4 km
apart, `THAW`) show the underlying idea is sound; the implementation over-applies
it.

---

## 3. The rule, stated so it can be implemented without judgement

**The whole cause is that the two qualifiers are treated identically.** They
carry opposite evidential weight and must be handled asymmetrically.

> **`OFFSHORE` on the ETYS side means the site may legitimately have no land
> coordinate. Be strict: require positive evidence before binding, and prefer to
> leave it unlocated.**
>
> **`ONSHORE` on the ETYS side means the site is definitely on land. A nearby
> onshore feature is therefore a better match, not a reason to reject.**

Concretely, in `build_connection_points.py`:

1. **A mapped `ONSHORE` token is asset-descriptive and stays discriminating.**
   `"Moray East Onshore substation"` genuinely describes an onshore asset. Keep
   the current behaviour: it may reject an ETYS `*OFFSHORE*` site. This is what
   makes `MOWE`, `ORMW` and `GREG` correct, and it must not be weakened.

2. **A mapped `OFFSHORE` token appearing inside a project name is NOT evidence
   the feature is at sea, and must never reject an ETYS `ONSHORE` site.**
   Detect the project-naming form — `OFFSHORE` immediately followed by
   `WIND FARM` / `WINDFARM` / `OWF`, or any `OFFSHORE` token with no
   `ONSHORE` token later in the string — and treat it as non-discriminating.
   This alone restores `BBWO` and `HOWB`.

3. **When the mapped name carries no shore token at all, fall back to the
   ETYS-qualifier-stripped token set.** Seven of the nine losses have mapped
   names with no shore word whatsoever (`Beatrice Wind Farm Substation`,
   `Triton Knoll Wind Farm Substation`, …); `qualifier_compatible()` never
   rejected them. They were lost purely because removing `ONSHORE` and
   `EXTENSION` from `NOISE` left ETYS's trailing `ONSHORE` in the site's token
   set, so `site_tokens <= candidate_tokens` stopped holding. Strip the ETYS
   shore qualifier for the *subset test* while keeping it for *identity*.

4. **Keep the sibling-claim test as the arbiter.** Where two ETYS sites resolve
   to one feature, the more specific name wins and the other fails closed. This
   is what produces the five correct rejections and it is independent of 1–3.

`EXTENSION` needs the same treatment as a separate axis: preserving it as
identity-bearing is what produced the `WLEE`/`WLEX` gain and must be kept, but it
should not block a subset match when the mapped side has no extension feature at
all (which is what cost `AREX` and `BLEX` — though those two are correct anyway
via the sibling-claim test).

---

## 4. The two the shore heuristic gets backwards

`shore_qualifier()` takes the **last** `ONSHORE`/`OFFSHORE` token in a name and
`qualifier_compatible()` requires equality:

```python
def shore_qualifier(name):
    words = re.findall(r"[A-Z0-9]+", str(name or "").upper())
    qualifiers = [w for w in words if w in {"ONSHORE", "OFFSHORE"}]
    return qualifiers[-1] if qualifiers else None
```

This assumes the qualifier describes the **mapped asset's location**. In the
dominant UK OSM convention it names the **project**:

> `BBWO` **BURBO BANK EXTENSION ONSHORE** was bound to
> *"Burbo Bank **Offshore Wind Farm** Substation"*.

There, `OFFSHORE` is part of the wind farm's name. The substation itself is
onshore — 0.02 km from the 132 kV network. The rule read a project name as a
location and rejected a correct binding. Same for `HOWB` **HORNSEA TWO ONSHORE** →
*"Hornsea Two **Offshore Wind Farm** Substation"*, 0.11 km from the network.

The "last qualifier" trick was written for the mixed form
*"Thanet **Offshore** Wind Farm **onshore** substation"*, where it works and
correctly gains `THAW`. It has no defence against the far more common form where
only the project word is present.

---

## 5. The inconsistency that proves it

Within one project, the corrected product now refuses the onshore site a location
and grants the offshore site a land coordinate **162 m away**:

| site | ETYS name | outcome | coordinate | km to OHL network |
|---|---|---|---|---:|
| `HOWB` | HORNSEA TWO **ONSHORE** | **released** | 53.656775, −0.260361 | 0.11 |
| `HOWW` | HORNSEA **OFFSHORE** | **retained** | 53.658217, −0.260744 | 0.22 |

Separation **162.32 m** (IUGG mean radius 6371008.8 m; 162.50 m on WGS84
semi-major — the choice is immaterial at this scale):

```bash
python - <<'PY'
import math
R=6371008.8; a=(53.656775,-0.260361); b=(53.658217,-0.260744)
p1,p2=math.radians(a[0]),math.radians(b[0])
h=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(math.radians(b[1]-a[1])/2)**2
print(f"{2*R*math.asin(math.sqrt(h)):.2f} m")
PY
```

An onshore substation and an offshore platform for the same project cannot be
162 m apart. At least one binding is wrong, and the build kept the wrong one.

`HOWW` is not alone. Of the five ETYS `*OFFSHORE*` sites that still carry a
coordinate, **two sit on the onshore network and should be re-examined**; the
other three are genuinely at sea and are correct:

| code | km to OHL network | verdict |
|---|---:|---|
| `HUMW` HUMBER GATEWAY OFFSHORE | 0.00 | **wrong binding retained** |
| `HOWW` HORNSEA OFFSHORE | 0.22 | **wrong binding retained** |
| `WERO` WESTERMOST ROUGH OFFSHORE | 14.56 | correct |
| `WERW` WESTERMOST ROUGH OFFSHORE | 14.56 | correct |
| `RAMW` RAMPION OFFSHORE | 15.83 | correct |

(`WERO`/`WERW` share one coordinate, but it is a real platform 14.6 km out; two
ETYS rows at 275 kV and 150 kV landing on one physical platform is plausible.
Note it, do not "fix" it blindly.)

---

## 6. The invariant the verifier is missing

Add this check. It is cheap, it is decisive, and it would have caught `HUMW` and
`HOWW` on the first run:

> **No ETYS site whose name contains `OFFSHORE` may be located within 1 km of the
> GB onshore overhead-line network.** An offshore platform is not on the onshore
> network. Fail the build if one is.

A useful companion: **if an ETYS `*OFFSHORE*` site is located and its sibling
`*ONSHORE*` site is not, fail** — that ordering is almost always inverted.

**Why the existing checks passed.** `verify_connection_points.py` has two shore
assertions:

- `Thanet onshore does not lend its coordinate to Thanet offshore`
- `Moray East offshore does not inherit Moray East onshore geometry`

Both are fixtures drawn from cases the heuristic already gets right. They were
written *from* the implementation rather than *against* it. **A check built only
from passing cases cannot fail**, which is why 44/44 and 22/22 are both green
over a product containing two demonstrably wrong bindings and nine unnecessary
losses. The new invariant is different in kind: it tests a physical property of
the world, not a remembered example.

---

## 7. What I could not verify

- **Ground truth for the 489 retained joins.** I tested internal consistency —
  duplicate coordinates, shore logic, and distance to the onshore network. I did
  not confirm that any retained OSM feature is the correct substation for its
  ETYS identity. The 489 may contain further errors of the `HUMW`/`HOWW` kind
  that the network-distance test cannot see because both candidates are onshore.
- **Any external civil source.** No network fetch was performed at any point in
  this audit. The separate finding that the sharpest civil parameters in
  `docs/routing/LITERATURE_REVIEW.md` cite sources carrying `sha256: null` is a
  statement about the repository's auditability, not a claim those numbers are
  wrong.
- **The completeness of the OHL layers** used for the land/sea test. A substation
  genuinely at sea also reads as far from them, which is why the test is used
  only to separate "on the onshore network" (≤0.25 km) from "far from it"
  (≥14.5 km). The gap between those two clusters is three orders of magnitude,
  so the separation is not sensitive to layer completeness.

---

## Summary for the implementer

Merging `b91e45b` as-is costs eleven true onshore coordinates and keeps two wrong
offshore ones. The five correct rejections in it do not depend on the faulty
heuristic and survive the fix in §3 untouched. Implement the asymmetry, add the
§6 invariant, then rebuild and confirm: expected outcome is the five correct
rejections retained, the three gains retained, `BBWO` and `HOWB` restored by rule
2, the seven no-shore-token losses restored by rule 3, and `HUMW`/`HOWW`
re-examined under the new invariant.
