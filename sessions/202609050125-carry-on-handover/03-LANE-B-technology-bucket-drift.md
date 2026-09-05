# Every technology-bucket implementation in `globalgrid2050` + `pipelinenews`

Lane B, 2026-09-05. Read-only survey; nothing here was changed. The Lane B brief
named `sld-sandbox-technology-buckets.js LAYER_ID_FOR_BUCKET` as one suspect of
five. **It is in neither of these two repos.** It lives in
`gridatlas/atlas/parts/202609041234-sld-sandbox-technology-buckets.js:266` and
`ventus-grid-engine/deeplink/contract.js:74` — Lane A's territory, listed here
only so the next reader does not hunt for it in the wrong repo.

What these two repos *do* hold is **seven families** of technology mapping, and
they do not agree. This is the record; the fix is a decision for Vikram, because
collapsing them changes what several published surfaces show.

## The drift, in one table

| axis | distinct variants found |
|---|---|
| accepted key set | 4-member · 5-member with `all` · 14-member · unrestricted · 2-member |
| bucket naming | `solar/bess/wind_onshore/wind_offshore` · `solar/bess/wind` · `solar/solar_roof/wind/bess/…` · `SOLAR/BESS/SOLAR + BESS` · `BATTERY/SOLAR/WIND_ONSHORE/WIND_OFFSHORE` · `Solar Photovoltaics/Battery/Wind Onshore/Wind Offshore` |
| fallback for unknown | `"solar"` · `"bess"` · `""` · `null` · `"other"` · `true` · empty URL · pass-through |
| wind handling | split two ways · collapsed to `wind` · recovered from `raw_tech` · **dropped silently** |
| case of the BESS test | `"bess"` · `"BESS"` · `.toLowerCase()==="bess"` · `.includes("BESS")` |

## A — the canonical four (the family that agrees)

`{solar, bess, wind_onshore, wind_offshore}`, and `Solar Photovoltaics /
Battery / Wind Onshore / Wind Offshore` as the REPD names that map onto them.
Agrees byte for byte across ~30 files: `scripts/data/build_v9_1_spine.py:16`
in each of `uk_renewables_pipeline/{v9,v9.4,v9.5,v9.5.1,v9.6,v9.6.1,v9.6.2,v9.7}`,
`scripts/core/project-filter-v9-2.js:1` in the same eight, the `projects-v9-*.js`
plugins, `pipelinenews/ui/javascript/202608261640-filters.js:1`, and the
`SPINE_TECHNOLOGIES` set in every wider-fleet cartridge copy.

**The data agrees with it.** Cross-tab over all 7,680 records of
`uk_renewables_pipeline/v9.7/data/v9.1/projects/part-*.json`:

| `technology` | `repd_technology` | rows |
|---|---|---|
| solar | Solar Photovoltaics | 3,563 |
| bess | Battery | 1,609 |
| wind_onshore | Wind Onshore | 2,399 |
| wind_offshore | Wind Offshore | 109 |

Four cells, no leakage. **The v9.7 project technology filter is exact** and was
measured so in the browser: each tab returns only its own badge, and the four
tabs sum to 7,680.

## B — the 14-token deep-link emitter, against a 4-token receiver

`pipelinenews/tools/intelligence/cartridges/map-corpus-contract/assets/{GEN}-atlas-pointer-deep-link.mjs:16`
accepts `act, bess, biomass, caes, flywheel, geothermal, hydro, hydrogen, other,
solar, solar_roof, tidal, wind_offshore, wind_onshore`.

The receiver, `globalgrid2050/repd_grid_atlasv8/ventus-corev8engine.js:805`,
accepts four: `solar, bess, wind_onshore, wind_offshore`.

**Ten of the fourteen emit links the receiver rejects.** The repo already knows:
`pipelinenews/tools/intelligence/202609030132-verify-wider-fleet-deep-link.mjs:22`
narrates it, and observes that the wider fleet emits *only* technologies outside
the receiver's set, by construction.

## C — a third emitter with no whitelist at all

`cartridges/{atlas-live-handoff,project-intelligence}/assets/{GEN}-atlas-pointer-deep-link.mjs:169`
sets `technology` from the project with no membership test — any string passes.
~68 identical copies live in `pipelinenews/releases/*/assets/202608311343-…` and
their `globalgrid2050/pipelinenews_intelligence/*` mirrors.

## D — the only place a bucket becomes a layer id, and it falls back to solar

`globalgrid2050/repd_grid_atlasv8/ventus-corev8engine.js:824`

    const technology = p.technology === 'bess' ? 'bess'
      : (p.technology.startsWith('wind_') ? 'wind' : 'solar');

Three buckets, and **anything not `bess` and not `wind_*` becomes `solar`**. It
exists because the atlas layer ids have no onshore/offshore split.

## E — the REPD string classifier that has no wind split to give

`globalgrid2050/scripts/repd_updater.py:197` (`classify_tech`) emits
`solar / solar_roof / wind / bess / … / other`. **It has no `wind_onshore` or
`wind_offshore` output at all** — the root of D's collapse. The split is
recovered downstream by re-reading `raw_tech`, in `tests/check_v9_1.mjs:35` of
all eight pipeline versions and in the MapLibre filters at
`repd_grid_atlasv8/index.html:253`.

## F — headline text → technology, wind absent

`uk_renewables_pipeline/v9.7/scripts/news/rules/technology-v9-7.mjs:1` yields
`SOLAR | BESS | "SOLAR + BESS" | ""`. There is no wind branch. Measured on the
served payload `dist/major_project_news_v9_5_1.json` (133 items): 77 SOLAR,
56 BESS, and the v9.7 SOLAR/BESS chips return exactly those counts — **the
newspaper technology chips are not leaking.**

One outlier, `pipelinenews/archive/…/discoveryv1/modules/matcher-bridge.mjs:6`,
holds **two disagreeing classifiers in the same file** and compares them against
each other at line 37: one requires the bigrams "offshore wind"/"onshore wind",
the other accepts bare "offshore"/"wind".

## G — the CSS class, five predicates, one silent loss

There are only two technology classes in the whole estate: `.story.solar` and
`.story.bess` (`uk_renewables_pipeline/v9.7/styles/v7.css`,
`pipelinenews/ui/styles/202608261740-v7-foundation.css`). **There is no wind
class.** Every predicate has the same shape and the same fallback:

| predicate | where |
|---|---|
| `item.technology === "bess" ? "bess" : "solar"` | `newspaper.js:52` × 10 versions |
| `String(item.technology\|\|"").toLowerCase() === "bess" ? …` | `newspaper-v9-2.js:93`, `newspaper-v9-5.js:87` |
| `technology === "BESS" ? …` | `newspaper-v9-5-1.js:88` × 5 versions |
| `classification.technology.includes("BESS") ? …` | `newspaper-v9-6-2.js:35` |
| `technologyValue.includes("BESS") ? …` | `newspaper-v9-7.js:35` and ~40 release copies of `app.mjs` |

**So anything that is not exactly BESS is painted as solar.** Measured on the
live v9.7 INTERNATIONAL chip: 19 stories, kickers read 13 BESS / 5 SOLAR /
1 `SOLAR + BESS`, but the CSS classes are 14 bess / 5 solar — the `SOLAR + BESS`
item is painted bess by the substring test.

## H — two-bucket code still shipping

- `uk_renewables_pipeline/*/scripts/plugins/canonical-project-controls.js:52`
  seeds its counter `{ solar: 0, bess: 0 }` and returns three options. No wind.
- `uk_renewables_pipeline/*/scripts/data/build_v7_2_spine.py:229` —
  `"solar" if record["technology"] == "Solar Photovoltaics" else "bess"`:
  **everything non-solar becomes bess.**
- `pipelinenews/discovery/javascript/202608270844-live-news-runner.mjs:353`
  declares `excluded_technologies: ['wind_onshore','wind_offshore']`.

## What this means for the defect Vikram reported

The complaint — *"other technologies sort also brings up solar"* — was **not**
any of these. It was the WIDER FLEET control keeping its label while the spine
repainted the table underneath it (see `02-LANE-BOARD.md`, B1). But families D
and G are both live, both silently substitute solar for something else, and both
would produce a sentence with those same words on a different surface. They are
named here rather than fixed: G changes the appearance of a published newspaper
and D changes what the Atlas draws, and neither is Lane B's to decide alone.
