# Codex lane audit — delta

Re-audit trigger: **Codex committed at 01:25 UTC**, five minutes after the
baseline was taken. A commit is the event that matters, so the full re-audit was
run immediately rather than at the three-hour mark.

- Baseline: `1c9909d` + uncommitted tree, 01:20 UTC
- Now: **`b91e45b231464c24339f5a58b81e6b1eb4c8b47f`**, `20260903: correct transformer identity and fail-closed joins`, authored 2026-09-03T02:21:01+01:00
- Branch: **`codex/20260903-phase0-integrity`** — **no upstream configured; NOT pushed.** `origin/main` remains at `1c9909d`.
- Working tree: **clean**.

## What changed between baseline and now

**Nothing in the artefacts.** All nine files are byte-identical to the baseline:

| file | sha256 (unchanged) |
|---|---|
| `derived/connection-points.v3.json` | `8db7171d9476…` |
| `derived/build_connection_points.py` | `a90bbf7ded28…` |
| `derived/verify_connection_points.py` | `da0e83c2f104…` |
| `derived/verify_phase0_acceptance.py` | `b49227eb0496…` |
| `sources/routing-sources-manifest.json` | `7681e7491917…` |
| `docs/routing/LITERATURE_REVIEW.md` | `250e8a23fabe…` |
| `docs/routing/METHOD_AND_LIMITATIONS.md` | `fdf44a5e281c…` |
| `docs/routing/LEGACY_LAYER_AUDIT.md` | `20e8f55ee3ec…` |
| `README.md` | `a78fcc1b23e8…` |

The commit captured exactly the state audited at baseline. Re-run from the
committed tree: `verify_connection_points.py` → **44/44**;
`verify_phase0_acceptance.py` → **22/22, zero failures**; coverage 489/886;
delta `{lost:16, gained:3, changed:0}`. Fully reproducible.

**No overclaim I flagged has been corrected** — the docs are unchanged since I
flagged them (Findings D, E, F stand).

---

## New evidence, and a correction to my own baseline

Codex's acceptance evidence says of the coverage drop:

> *"A lower count is not automatically a regression: fail-closed removal of an
> unsupported join is an epistemic correction. Review every code."*

That is the right invitation, so I reviewed every code against evidence external
to the product. I measured the great-circle distance from each affected
coordinate to the nearest vertex of the GB 400/275/132 kV overhead-line network
(143,689 vertices from `globalgrid2050/grid_{400,275,132}kv.geojson`). A real
onshore transmission substation sits on that network; an offshore platform does
not.

### Result: all sixteen removed coordinates are onshore substations

| code | ETYS name | km to OHL network |
|---|---|---:|
| `BBWO` | BURBO BANK EXTENSION ONSHORE | 0.02 |
| `BOSO` / `BOSW` | BARROW ONSHORE / OFFSHORE | 0.02 |
| `ORMW` | ORMONDE OFFSHORE | 0.02 |
| `SGRX` | SEAGREEN ONE 275KV ONSHORE | 0.02 |
| `AREX` | ARECLEOCH EXTENSION | 0.03 |
| `BLEX` | BHLARAIDH EXTENSION | 0.03 |
| `BEAT` | BEATRICE ONSHORE | 0.04 |
| `MOWE` | MORAY EAST OFFSHORE | 0.04 |
| `TKNO` | TRITON KNOLL ONSHORE | 0.05 |
| `GREG` | GREATER GABBARD OFFSHORE | 0.07 |
| `NNGO` | NEART NA GAOITHE ONSHORE | 0.08 |
| `LONO` | LONDON ARRAY ONSHORE | 0.09 |
| `HOWB` | HORNSEA TWO ONSHORE | 0.11 |
| `WDSO` | WEST OF DUDDON SANDS ONSHORE | 0.11 |
| `EACO` | EAST ANGLIA THREE ONSHORE | 0.12 |

**16 of 16 within 120 m. None is an offshore platform.** The fix did not remove a
single sea-located coordinate, because none of the sixteen was ever at sea.

### I was wrong at baseline about the retained offshore sites

My baseline said *"all five ETYS `*OFFSHORE*` sites that still carry a coordinate
are on land."* **That is incorrect.** Measured:

| code | km to OHL network | verdict |
|---|---:|---|
| `HUMW` HUMBER GATEWAY OFFSHORE | 0.00 | on the onshore network — **wrong binding retained** |
| `HOWW` HORNSEA OFFSHORE | 0.22 | on the onshore network — **wrong binding retained** |
| `WERO` WESTERMOST ROUGH OFFSHORE | 14.56 | genuinely offshore — correct |
| `WERW` WESTERMOST ROUGH OFFSHORE | 14.56 | genuinely offshore — correct |
| `RAMW` RAMPION OFFSHORE | 15.83 | genuinely offshore — correct |

Two, not five. Correcting the record.

**Finding B softens accordingly:** `WERO`/`WERW` share a coordinate that is a
genuine offshore platform 14.6 km out. Two ETYS rows (275 kV and 150 kV) landing
on one physical platform is plausible, not obviously an error. It remains an
undisclosed-in-product identity collision, but not a land/sea fault.

**Finding A stands and is now measured, not inferred:** `HOWW` (ETYS *offshore*)
retains a coordinate 0.22 km from the onshore network, while `HOWB` (ETYS
*onshore*) was refused one 0.11 km from it, 163 m away. The build kept the
offshore-named site on the onshore network and discarded the onshore-named one.

---

## Revised scorecard for the sixteen rejections

The relevant question is not "was the coordinate onshore" — all sixteen were —
but **"did another ETYS site have a better claim to it?"**

**(a) Correct duplicate resolution — the sibling kept the point. 5 codes.**

`AREX`→`AREC`, `BLEX`→`BHLA`, `GREG`→`GGON`, `MOWE`→`MORO`, `ORMW`→`ORMO`.
In each case two ETYS sites held one OSM feature; the more specific site retained
it and the other was released. These are the fix working as designed, and
`MOWE` is exactly the case Vikram named. **Defensible.**

**(b) Point abandoned by both claimants. 2 codes.**

`BOSO` BARROW ONSHORE and `BOSW` BARROW OFFSHORE both held (54.12348, −3.22998),
a substation 20 m from the 132 kV network. Both were released and **no ETYS site
now claims it.** Defensible as fail-closed (the mapped feature *"Barrow"* carries
no qualifier, so neither can be preferred) but it is a real loss: a mapped,
grid-connected substation is now orphaned.

**(c) A correct coordinate removed with no competing claimant. 9 codes.**

`BBWO`, `BEAT`, `EACO`, `HOWB`, `LONO`, `NNGO`, `SGRX`, `TKNO`, `WDSO`.
Every one is 20–120 m from the transmission network. In every case I checked the
sibling ETYS sites and **no other site took the coordinate** — `BBWW`, `BEIW`,
`HOWA/C/D`, `LOAW/LOYW`, `NNGW`, `SGRO`, `TKNE/TKNW`, `WDSW` are all unlocated.
Two mechanisms produced these:

- **`BBWO`, `HOWB`** — the shore heuristic fired backwards. `shore_qualifier()`
  reads the last ONSHORE/OFFSHORE token of the mapped name and requires equality.
  It is right where OSM describes the asset (*"Moray East **Onshore** substation"*)
  and wrong where OSM names the project (*"Burbo Bank **Offshore Wind Farm**
  Substation"*), which denotes an onshore substation. **Not defensible.**
- **The other 7** — collateral of removing `ONSHORE`/`EXTENSION` from `NOISE`.
  The mapped names carry no shore token at all, so `qualifier_compatible()` never
  rejected them; they simply stopped matching because ETYS's trailing `ONSHORE`
  is no longer stripped. **Safe but over-conservative.**

### Net effect

**5 of 16 removals are supported by the evidence. 11 removed a true onshore
substation location, 10 of which are now claimed by nothing.** Coverage did not
drop by 13 because 13 bindings were wrong; it dropped because 3 were newly
resolved and 11 true locations were released alongside 5 genuine duplicates.

This does not make the change wrong to have made — preserving `ONSHORE`,
`OFFSHORE` and `EXTENSION` as identity-bearing is correct, and the `WLEE`/`WLEX`
gain (two distinct coordinates 8.4 km apart, previously collapsed) proves it. It
means the current implementation trades 11 true positives for 5 true negatives,
and the recovery is available without giving up any of the 5.

### The change that recovers them

Treat the two mapped qualifiers asymmetrically:

- a mapped **`ONSHORE`** is asset-descriptive → keep it discriminating;
- a mapped **`OFFSHORE`** inside a project name (*"… Offshore Wind Farm …"*) is
  not evidence the feature is at sea → do not let it reject an ETYS `ONSHORE`
  site;
- fall back to the ETYS-qualifier-stripped token set when the mapped name carries
  no shore token, so the 7 Group-(c) collateral losses rebind.

All 5 supported rejections survive that change: they are decided by the
*sibling-claim* test, not by the shore words. `HUMW` and `HOWW` should
additionally be re-examined — they are the two retained bindings the evidence
contradicts.

---

## Everything else: unchanged and confirmed

- **Cowley 10 → 5** — confirmed, with the oracle reporting five physical records
  and five windings at each of 132 kV and 400 kV.
- **Denominator hygiene — pass.** 1,472 / 525 / 484 / 95-over-59 all reproduce.
  1,526 is labelled an incidence count everywhere; 95 is never quoted as a sample
  size. Codex additionally catches that the corrected cohort coincidentally also
  has 95 rows but 60 pairs, and freezes membership by SHA-256 rather than count.
- **Verifiers — substantive.** 31 → 41 `check()` sites, printing 44/44. The ten
  additions are named regression locks on specific defects, not restatements.
  Neither verifier would catch Finding A: both shore checks (Thanet, Moray East)
  are fixtures drawn from cases the heuristic gets right. **A check that an ETYS
  `*OFFSHORE*` site is not located on the onshore OHL network would have caught
  `HUMW` and `HOWW` immediately.**
- **Docs — numerically faithful.** All six §P2 cable figures reproduce to five
  decimal places against the oracle; all twelve `LEGACY_LAYER_AUDIT.md` road
  counts reproduce exactly (311,731 features / 2,086,807 segments).
- **Findings D, E, F stand uncorrected** — the sharpest civil parameters
  (Glaslyn 850 m HDD / 18 crossings / 65 m corridor; EA FRA3 1.5 m and 5 m; River
  Ouse eighteen cables) cite sources carrying `sha256: null`, while the README
  calls the locators *"exact"*; the NG undergrounding paper supplies trench and
  swathe dimensions with `published: null`; the Versleijen DOI is called
  *"peer-reviewed"* unverified.

## Verdict

**ADOPT WITH CHANGES**, unchanged from baseline but now better evidenced.

Take now: the transformer identity fix, the denominator terminology block, both
verifiers, and all three routing documents (with the source-integrity caveats
attached to any civil number that reaches a card).

Hold: the location join. It is directionally right and 5 of its 16 rejections are
correct, but as it stands it releases 11 true onshore substation locations and
retains 2 demonstrably wrong offshore bindings. Do not ship the 489 as an
improvement on the 502 without the asymmetric-qualifier change; ship it as what
it is — a different, not yet better, trade.

## What I could not verify

- External civil sources: no network retrieval performed. Findings D/E/F are gaps
  in the repository's auditability, not claims the numbers are wrong.
- Whether the OHL layers used for the land/sea test are themselves complete; a
  substation genuinely at sea would also read as far from them, which is why the
  test is only used to separate "on the onshore network" from "far from it", and
  the three offshore results (14.6–15.8 km) are consistent with real platforms.
- Codex's reported "34 → 41" verifier count. Measured: 31 committed → 41
  working-tree `check()` sites, printing 44/44.
