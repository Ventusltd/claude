# Codex lane audit — baseline

Auditor: independent Claude session. No write access exercised on `data-grid-gb`,
`gridatlas`, `pipelinenews` or `globalgrid2050`. Every number below was measured
from the artefacts, not read from anyone's summary.

- Baseline taken: 2026-09-03 01:20 UTC
- Audited repo: `C:\Users\vikra\OneDrive\Documents\GitHub\data-grid-gb`
- HEAD: `1c9909d1138704b29235c27fd769436dda8a0b18` (2026-09-01T17:23:51Z)
- All audited work is **uncommitted** in the working tree on top of that commit.

## Verdict at baseline

**ADOPT WITH CHANGES.** The transformer fix, the denominator discipline and the
verifier expansion are sound and independently reproduce. The location-join fix
is right in principle and right in 7 of 16 rejections, but its shore-qualifier
heuristic is **inverted for the dominant UK OSM naming pattern** and has left the
product in a state where an ETYS *offshore* site keeps an onshore coordinate
while the matching ETYS *onshore* site is refused one. That must be fixed before
any of this reaches a public card.

---

## 1. The F2/F3 location-join fix

### Totals — confirmed

| quantity | committed (1c9909d) | working tree | delta |
|---|---:|---:|---:|
| connection points | 886 | 886 | 0 |
| with location | **502** | **489** | −13 |
| exact_name | 461 | 450 | −11 |
| distinctive_tokens | 41 | 39 | −2 |
| ambiguous_exact_name | 25 | 14 | −11 |
| ambiguous_distinctive_tokens | 47 | 31 | −16 |
| ambiguous_authoritative_identity | — | 2 | new |
| rejected_shore_qualifier_conflict | — | 1 | new |
| unlocated | 384 | 397 | +13 |

Per-voltage coverage in the new product: 400 kV 206, 275 kV 198, 132 kV 353.
**This reproduces Vikram's independent measurement exactly** (214→206, 197→198,
358→353).

Site-level diff: **16 lost, 3 gained, 0 changed**. No site silently re-pointed at
a different geometry. Codex's own `verify_phase0_acceptance.py` exports the same
16/3/0 lists; my diff was computed independently and agrees member-for-member.

### Duplicate-coordinate collisions

Distinct coordinates claimed by more than one ETYS site: **19 → 13**. All six
removed collisions are shore/extension pairs. The 13 that remain are TEE / B-station /
GIS pairs (Aberthaw/Aberthaw B, Leven/Leven Tee, Harker/Harker GIS …) which are
arguably genuinely co-located — with one exception, below.

### The 16 rejections, each assessed

**Group 1 — removed a demonstrably wrong duplicate binding. Defensible, high confidence. (7 codes / 6 collisions)**

| code | ETYS name | had been bound to | why the rejection is right |
|---|---|---|---|
| `AREX` | ARECLEOCH EXTENSION | *Arecleoch Wind Farm Substation* (55.08404,−4.84996) | identical coordinate to `AREC` ARECLEOCH, which retains it. One OSM feature cannot be two ETYS sites. |
| `BLEX` | BHLARAIDH EXTENSION | *Bhlaraidh Substation* (57.24429,−4.70336) | identical coordinate to `BHLA`, which retains it. Same reason. |
| `BOSO` | BARROW ONSHORE | *Barrow* (54.12348,−3.22998) | `BOSO` and `BOSW` held the **identical** coordinate from a single unqualified feature. |
| `BOSW` | BARROW OFFSHORE | *Barrow* (same point) | as above. Removing both is over-conservative but unavoidable: the mapped feature carries no qualifier, so neither can be preferred. |
| `GREG` | GREATER GABBARD OFFSHORE | *Greater Gabbard **Onshore** Substation* | shared the coordinate with `GGON` GREATER GABBARD ONSHORE, which retains it. Mapped name is asset-descriptive. Correct. |
| `ORMW` | ORMONDE OFFSHORE | *Ormonde **onshore** substation* | shared with `ORMO` ORMONDE ONSHORE, which retains it. Correct. |
| `MOWE` | MORAY EAST OFFSHORE | *Moray East **Onshore** substation* | shared with `MORO` MORAY EAST ONSHORE, which retains it. **Vikram's exemplar; it is correct.** |

**Group 2 — the shore heuristic fired backwards. NOT defensible. (2 codes)**

| code | ETYS name | had been bound to | the problem |
|---|---|---|---|
| `BBWO` | BURBO BANK EXTENSION **ONSHORE** | *Burbo Bank **Offshore** Wind Farm Substation* (53.24900,−3.46856 — Bodelwyddan, N Wales) | The OSM string "Offshore Wind Farm" names the **project**, not the asset's location. That feature is an onshore substation. A correct binding was removed. |
| `HOWB` | HORNSEA TWO **ONSHORE** | *Hornsea Two **Offshore** Wind Farm Substation* (53.65678,−0.26036 — Killingholme) | Same inversion, and worse: see the finding below. |

**Group 3 — collateral of the `NOISE` regex change. Over-conservative; removed
probably-correct bindings with no collision and no shore conflict. (7 codes)**

`BEAT` (BEATRICE ONSHORE → *Beatrice Wind Farm Substation*), `EACO` (EAST ANGLIA
THREE ONSHORE → *East Anglia THREE Converter Station*), `LONO` (LONDON ARRAY
ONSHORE → *London Array OWF substation*), `NNGO` (NEART NA GAOITHE ONSHORE),
`SGRX` (SEAGREEN ONE 275KV ONSHORE), `TKNO` (TRITON KNOLL ONSHORE), `WDSO`
(WEST OF DUDDON SANDS ONSHORE).

In every case the mapped name carries **no** shore qualifier, so
`qualifier_compatible()` did not reject them. They were lost because ETYS's
trailing `ONSHORE` is no longer stripped by `NOISE`, so the site's token set is
no longer a subset of the mapped feature's. These are conservative losses, not
corrections of wrong bindings.

`SGRX` is the partial exception: `SGRO` SEAGREEN ONE 220KV ONSHORE also exists and
is unlocated, so one OSM feature was serving two ETYS onshore sites at different
voltages. Rejecting it is defensible on ambiguity grounds — though the build did
not reject it for that reason.

**Tally: 7 defensible, 7 over-conservative-but-safe, 2 wrong.**

### FINDING A (highest severity) — the shore heuristic is inverted, and the product is now backwards at Hornsea

`shore_qualifier()` takes the last ONSHORE/OFFSHORE token in the mapped name and
requires it to equal the ETYS site's. This is correct where OSM describes the
asset (*"Moray East **Onshore** substation"*). It is **wrong** where OSM names the
project — *"X **Offshore Wind Farm** Substation"* — which is the more common UK
convention, and which denotes an **onshore** substation.

Measured consequence in the shipped product:

- `HOWB` **HORNSEA TWO ONSHORE** — location **removed**.
- `HOWW` **HORNSEA OFFSHORE** — location **retained**, at
  (53.65822, −0.26074), *"Hornsea Offshore Wind Farm Substation"*.
- The two candidate coordinates are **163 m apart**, both at North Killingholme,
  on land.

The build now refuses to locate the onshore site and confidently locates the
offshore one, using two features 163 m apart. That is the exact failure mode the
fix was written to prevent, produced by the fix.

**All five ETYS sites named `*OFFSHORE*` that still carry a coordinate are on
land**: `HOWW`, `HUMW` (Humber Gateway), `RAMW` (Rampion), `WERO` and `WERW`
(Westermost Rough). An offshore platform cannot be on land. The heuristic
validated all five because the mapped names say "Offshore".

**Recommended change before adoption:** treat a mapped `ONSHORE` as
asset-descriptive and authoritative; treat a mapped `OFFSHORE` as
project-naming and non-discriminating (i.e. not evidence that the feature is at
sea). That preserves all 7 Group-1 rejections and restores `BBWO`/`HOWB`.

### FINDING B — a same-name collision still ships with a shared coordinate

`WERO` and `WERW` are **both** named `WESTERMOST ROUGH OFFSHORE`, both `OFTO`, and
both carry the identical coordinate (53.80501, 0.13315). They survive
`site_join_context` only because their highest voltages differ (275 vs 150).
Codex's own acceptance evidence lists this pair in
`current_normaliser_all_network_sites.groups` — so it is **detected and
disclosed**, but not failed closed. Same shape as `MORF`/`MORO` (both
`MORAY EAST ONSHORE`, 400 vs 220 kV), where only one is located.

### FINDING C — the 3 gains are genuine improvements

- `WLEE` WHITELEE → *Whitelee Wind Farm Substation* (55.69558,−4.17134)
- `WLEX` WHITELEE EXTENSION → *Whitelee Wind Farm Extension Substation* (55.68039,−4.30358)

Two **distinct** coordinates 8.4 km apart. Previously both were ambiguous because
`EXTENSION` was stripped and the two names collapsed. This is a real,
correctly-resolved gain and the clearest evidence the identity-preservation idea
is right.

- `THAW` THANET WIND ONSHORE → *Thanet Offshore Wind Farm **onshore** substation*.
  Gained because `shore_qualifier` takes the **last** qualifier, which is
  `onshore`. This is the case the "last qualifier" rule was designed for, and it
  works. `THOW` THANET WIND OFFSHORE correctly stays unlocated.

---

## 2. Cowley — CONFIRMED

`COWL` COWLEY: transformers **10 → 5**. Circuits unchanged at 6.

The acceptance oracle independently states
`oracle_physical_record_count: 5`, `product_physical_record_count: 5`, and
`node_end_windings_by_voltage_kv: {"132": 5, "400": 5}` — i.e. five physical
machines presenting five windings at each of two voltages, which is exactly the
distinction that was being conflated.

Fleet-wide effect: sum of per-site transformer counts **2,920 → 1,526**;
**484 sites** changed count; **515** sites carry transformers in the ≥132 kV
rollup, unchanged. Dominant transitions are exact halvings (4→2 ×223, 8→4 ×67,
10→5 ×24), consistent with double-counted node ends rather than an arbitrary
rescale.

---

## 3. The verifiers — SUBSTANTIVE, and the count is 44, not 41

`python derived/verify_connection_points.py` → **44/44 checks passed**
(committed version at `1c9909d` had **31** `check()` call sites; the working tree
has **41**; the script emits 44 assertions because three are parameterised).
Whatever "34 → 41" refers to, the measured pass line reads `44/44 checks passed`.

The 10 new `check()` sites are not restatements. Named additions:

- `the ETYS 2025 model retains 1,472 distinct transformer records`
- `an ambiguous authoritative name/voltage/owner identity fails closed`
- `a mapped onshore/offshore qualifier conflict fails closed`
- `onshore, offshore and extension remain identity-bearing`
- `context keys combine name, voltage and owner and fail closed on duplicates`
- `Thanet onshore does not lend its coordinate to Thanet offshore`
- `Moray East offshore does not inherit Moray East onshore geometry`
- `every site transformer headline counts distinct source rows, not node ends`
- `Cowley is five physical records while both voltage winding counts remain five`
- `the product declares its transformer count semantics`

Each of these would fail if the corresponding defect were reintroduced. They are
regression locks on named, specific defects — real checks, not restatements.

`python derived/verify_phase0_acceptance.py` → **22/22, zero failures**, emitting
a `data-grid-gb.phase0-acceptance-evidence.v1` JSON document. This is the stronger
artefact of the two. It pins its inputs by SHA-256, enumerates the full 16/3/0
location delta, exports frozen cohort membership lists, and refuses to make a
road-router claim at all:

> `"road_router": {"status": "not_reconstructed", "reason": "No immutable road-graph
> bundle and build provenance are present in this repository; road-router accuracy
> claims are not acceptance facts."}`

That refusal is the single most trustworthy line in the whole delivery.

**Caveat:** neither verifier detects Finding A. Both new shore checks are
single-instance fixtures (Thanet, Moray East) chosen from the cases the heuristic
gets right. Nothing asserts that an ETYS `*OFFSHORE*` site is not located on land,
and nothing asserts that a `*ONSHORE*` site whose sibling `*OFFSHORE*` site is
located must itself be located. The tests were written from the fix, not against it.

---

## 4. The civil literature docs

The three self-corrections are present and correctly worded:

- EGL5: *"it does not present a preliminary routed onshore path as a comparison to
  the straight line"* — corrected.
- OS Open Roads: *"unique within a release but … not persistent between versions"* —
  corrected.
- Ramboll: *"study-level average intervals … These inputs are not universal
  frequencies for factual map features"* — corrected.

Every quantitative claim in `METHOD_AND_LIMITATIONS.md` §P2 reproduces **exactly**
against the machine oracle:

| doc claim | oracle |
|---|---|
| corrected cohort, k=1.245: 8.58% median, 68/95 | 8.58224%, 68/95 ✓ |
| corrected pair-weighted: 9.39%, 40/60 | 9.38712%, 40/60 ✓ |
| historical: 8.45%, 69/95 | 8.45403%, 69/95 ✓ |
| historical pair-weighted: 9.30%, 40/59 | 9.30066%, 40/59 ✓ |

`LEGACY_LAYER_AUDIT.md`'s road measurements also reproduce exactly on independent
recount of the source GeoJSON: motorways 17,713 / 133,642; trunk 130,228 / 848,251;
primary 163,790 / 1,104,914; combined **311,731 / 2,086,807**. Every digit matches.

### Residual overclaims

**FINDING D — the most specific civil parameters rest on unpinned sources.**
The manifest's own `integrity_policy` says a sha256 is present *"only where the
exact referenced file was independently downloaded and hashed"*. Only **2 of 12**
sources are hashed: the NG undergrounding PDF and the DESNZ/Ramboll PDF. `null`
elsewhere.

But the literature review's sharpest numbers come from the **unhashed** documents:

> *"A curved HDD of about 850 m combines an A-road, railway and river crossing.
> The scheme records eighteen ditch/watercourse crossings, a working corridor
> around 65 m, open-cut formation up to 23 m"* — Glaslyn ES, `sha256: null`.

> *"burial is at least 1.5 m below the bed and maintained for at least 5 m beyond
> both banks"* — EA FRA3, `sha256: null`.

> *"Preliminary rating studies indicated that eighteen transmission cables were
> likely to be required"* — River Ouse, `sha256: null`.

The gap: these are asserted at section-level precision against copies whose
integrity is not pinned and whose retrieval is not receipted. The README then
describes the review as recording *"exact page/section locators"* — "exact" is
stronger than `sha256: null` supports. **I could not verify any of these numbers
against the source documents** (no network retrieval performed). Not an assertion
that they are wrong; an assertion that nothing in the repository lets a reader
check them.

**FINDING E — an undated source cited for current dimensions.**
*"a typical trench is about 1.5 m wide and 1.2 m deep … a 400 kV double-circuit
construction swathe can be about 40-65 m"* is sourced to the NG undergrounding
paper, whose manifest entry carries `"published": null`. That document is
long-standing, not current. The review presents its dimensions without a date.
A dimension on a public card needs its vintage attached.

**FINDING F — an unverifiable citation.**
Versleijen et al., DOI `10.1007/s12667-026-00827-x`, cited as *"peer-reviewed"* and
*"compares least-cost routing with human reference routes across five real cases"*.
`sha256: null`, no retrieval receipt. I could not confirm the DOI resolves or the
five-case count. The doc's own guard is good (*"Using it as an independent test
oracle is a proposal here, not a sourced validation"*), so the risk is low, but
"peer-reviewed" is currently an unverified attribute.

Everything else in the review is guarded. The Glaslyn 50/50 open-cut/HDD split
would be a serious overclaim if generalised, and the doc explicitly forbids that:
*"Use this project as a geometry-and-event regression fixture, not as a universal
parameter table."* Accepted.

---

## 5. Denominator hygiene — PASS, and better than asked

Codex's `verify_phase0_acceptance.py` publishes an explicit terminology block that
keeps all five quantities apart:

```
1472 : global physical/source transformer records
1526 : transformer-to-site incidences in the >=132 kV rollup only
1550 : global transformer-to-site incidences
2920 : node-end/winding landings in the >=132 kV rollup
2944 : global node-end/winding landings
```

plus `global_sites_with_transformers: 525`, `rollup_sites_with_transformers: 515`,
`global_sites_inflated_by_endpoint_count: 484`.

Against Vikram's four figures:

| Vikram | Codex artefact | verdict |
|---|---|---|
| 1,472 physical transformer records | `1472_global_transformer_records: true` | ✓ |
| 525 sites with transformers | `global_sites_with_transformers: 525` | ✓ |
| 484 sites affected | `global_sites_inflated_by_endpoint_count: 484`; my own diff finds 484 | ✓ |
| 95 cable records, 59 distinct endpoint pairs | `historical_95_records_are_only_59_site_pairs: true` | ✓ |

**Nowhere is 1,526 quoted as a physical record count** — it is labelled an
incidence count everywhere it appears. **Nowhere is 95 quoted as a sample size** —
`METHOD_AND_LIMITATIONS.md` states *"Those 95 circuit rows represented only 59
endpoint pairs … parallel rows are not independent route geometries."*

One clarification worth recording, because it resolves an apparent conflict:
**515 vs 525 is not a discrepancy.** 525 is over all network sites; 515 is over the
≥132 kV published subset. Codex names both separately. Similarly 1,526 = 1,472 + 54
transformer rows whose two ends land at *different* sites and are therefore counted
at each.

Codex also goes further than asked: the corrected `> 1 km` cable cohort *coincidentally*
also contains 95 rows, but now over **60** pairs with different members, and the doc
says so explicitly — *"The coincident row count does not make the two cohorts
equivalent"* — and freezes membership by SHA-256 rather than by count. That is the
correct instinct and I would not have caught the coincidence without it.

**Residual QA signal Codex surfaces on itself:** `straight_exceeds_published_cable_km_records: 5`
— five circuit records where the straight-line endpoint separation exceeds the
published cable length, which is geometrically impossible and indicates five
remaining bad joins or length-semantics mismatches. Correctly labelled a signal,
not a diagnosis.

---

## What I could not verify

- The content of any external civil source (no network fetch performed). Findings D,
  E and F are gaps in the repository's own auditability, not claims that the numbers
  are wrong.
- Whether the OSM features behind the 489 retained joins are correctly placed at all;
  I checked internal consistency (collisions, shore logic, land/sea plausibility),
  not ground truth.
- Codex's reported "34 → 41" verifier count. Measured values are 31 committed
  `check()` sites → 41 working-tree sites, printing 44/44.
