# Routing table — finding → owning module → proof

The modularisation test, stated once: **a finding that routes to one file is a cut; a finding
that cannot be routed to one file is a decision.** Every row below names the single file that
owns the change, the class of change, what is measured to be true right now, and the gate that
proves it. A row with no owning file is flagged as a decision, not left vague.

State as of 2026-09-03 03:05 UTC. Statuses are measured, not reported.

## Oven-ready: the next stamp is v9.84, and it is one module

| | |
|---|---|
| **finding** | F8 — the cartridge proof reads `data-grid-gb` from an unpinned sibling path; absent on the runner; eight real-data checks skip silently; `run-current` halts at the first failing proof |
| **owning file** | `gridatlas/tools/proofs/202609030137-substation-intelligence.proof.mjs:302-311` + `.github/workflows/202608312212-cartridge-proof.yml` |
| **change class** | proof + workflow. No cartridge logic changes. |
| **measured** | CI red on **v9.79, v9.80, v9.81, v9.82, v9.83** (runs 33702626898, 33703003486, 33703210221, 33703780359, 33704447774). Local 667/667 at 4a17fa3. Runner-shape reproduction: 59/60, one failure, **675 of 735 checks never execute**. v9.78 was the last green (run 33702004076). |
| **invariant to assert** | proof-input commit == `atlas/modules/202609030137-pinned-products.js` commit, by digest. A null product FAILS the eight checks, loudly. |
| **gate** | the runner's conclusion for the pushed commit, polled from the Actions API — not the local run |
| **status** | in flight, agent instructed 02:58 UTC |

## The table

| # | finding | owning file | class | measured now | gate |
|---|---|---|---|---|---|
| F1 | PipelineNews deploy frozen | `pipelinenews/atman/202608262014-build-pages.py` — three gates, third is `ATLAS_V9_SOURCE_PARENT = 693ccda8` | **DECISION, not a cut.** 1,796 diverging paths all `A`; allowance covers ≤42; authorisation freeze working as designed. **No route exists for an owner to authorise a wider closure.** | 27 consecutive reds; last success 30 Aug 11:13. `globalgrid2050.com/pipelinenews_intelligence/` is a separate surface and current. | owner decision at 10:00 |
| F2 | substation name collisions | producer `data-grid-gb/derived/build_connection_points.py` (Codex `b91e45b`, **unmerged**) · consumer `gridatlas/atlas/parts/202609012350-substation-intelligence-body.js:51` `normalise()` | data + consumer | **HELD.** Fix as written trades 11 true coordinates (all `*ONSHORE*`) for 5 correct rejections. `HOWB HORNSEA TWO ONSHORE` loses a pin while `HOWW HORNSEA OFFSHORE` keeps one 162 m away. Needs asymmetric ONSHORE/OFFSHORE. | `verify_connection_points.py` 44/44 + proposed invariant: no ETYS `*OFFSHORE*` site on the onshore network |
| F3 | transformer double-count | `gridatlas/atlas/parts/…sld-sandbox-body.js` + `…substation-intelligence-body.js` (v9.79) · upstream `b91e45b` | consumer fixed; upstream pending | **shipped v9.79**, Cowley 5 not 10, 2,944 landings → 1,550 units, 484 of 525 sites. **Never verified by CI** — see F8. | the eight guarded checks, once F8 makes them run |
| F4 | "Nearest" over 57% coverage | `gridatlas` substation-intelligence cartridge — compute per-voltage located/published **from the fetched payload**, never literal text | cartridge | **not cut.** Coverage will move 502→489 when `b91e45b` merges; hardcoded numbers would go stale with no cut between. | proof asserts the rendered count equals the payload count |
| F5 | runtime fetch from mutable `main` | `gridatlas/atlas/modules/202609030137-pinned-products.js` | module | **FIXED v9.83.** Three products pinned by 40-char commit + SHA-256 + byte length. Zero mutable runtime edges in gridatlas. **2 remain estate-wide:** `globalgrid2050 → gridatlas@main atlas/current.json` (`scripts/verify_published_versions.py:54`), `pipelinenews → globalgrid2050@main dist/major_project_news_v9_5_1.json` (`index/202608261927-compile-index.mjs:128`). `current.json:292` carries a stale `"reads"` descriptor. | pinned-products proof (lands in v9.84) |
| F6 | four Pages roots answer 404 | `companies`, `data-gb-electricity`, `data-interconnectors`, `pipelinenews` | observation | open; may be intended | — |
| F7 | standing red CI | spider `01-drift.md` | observation | `data-gridatlas` hourly watchdog red ~2 days at `5484218`; `cvaa` self-test red since 31 Aug (`b725155`) — **the immune system's own CI is red**, know this before adopting it into 32 repos | spider, per pass |
| Reg1 | HIDE LAYERS blanks the map | `gridatlas` v9.80 `e9491b6` | part | shipped; CI red via F8 | — |
| Reg2 | deep link without `repd_ref` | `gridatlas/atlas/cartridges/…place-global-search` v9.81 `f1f430d` | cartridge | shipped; parallel session proved arrival RESOLVED, camera moves; CI red via F8 | — |
| Reg3 | technology whitelist | `gridatlas` v9.82 `52ebabc` — "an unknown technology costs one layer, not the arrival" | cartridge | shipped; **re-diagnosed (C3)**: Pipeline News never emits `Landfill Gas`, it emits `row.t` e.g. `biomass`; all 1,104 wider-fleet links lost their *layer*, not their arrival | pipelinenews harness `b4c446a` 9/11 |
| — | corridor scalar k=1.245 | `gridatlas` substation-intelligence card, additive line beside the straight line | cartridge | **not cut.** 8.45% median error, 73% within 15%, 59 distinct pairs. Never apply to OHL (1.13). | `routestudy/` scripts, pinned inputs required before it counts as evidence |
| — | 44 px `Explore route corridors ▸` | `gridatlas` UI, `contextmenu` + long-press unbound | part | not cut | — |
| — | ledger digests name CRLF bytes never served | `pipelinenews` `78fbd42` guards the next release | tooling | shipped; **10 entries across 6 immutable releases wrong, not amended** | `--check` proven both ways |
| — | wider-fleet duplicate rows | `pipelinenews` harness | data | 3 duplicate rows, 47.30 MW double-counted; explain 2 of 13 unresolved | harness 9/11 |

## What the dependency graph says — from `sessions/202609030120-cicd-spider/crosslink.json`

524 edges, evidence-tiered. **Read `evidenceTier=shipped` only** for runtime truth — `record` and
`doc` edges are prose in `claude`, `gemini`, `codex-chatgpt` citing URLs, and they inflate 2 real
mutable edges to 17. The map predates v9.83 and shows three gridatlas edges as mutable that are
now pinned; the spider is regenerating.

| repo | in-degree (runtime + contract) | note |
|---|---|---|
| **pipelinenews** | **99** | most load-bearing repo in the estate — and the one with the frozen deploy |
| globalgrid2050 | 39 | |
| data-grid-gb | 23 | the pin target |
| gridatlas | 14 | |
| data-gb-electricity | 6 | |

## The queue after v9.84, in order, one module each

1. **F4** — coverage from payload. Robust to `b91e45b` merging.
2. **corridor scalar** — one additive line on the card, k=1.245 with its spread stated.
3. **44 px sheet** — one part, one gesture slot.
4. **F2 consumer side** — only after Codex resolves the asymmetric join upstream; do not fix in
   the consumer what the producer is about to fix.

## Two environmental facts a fresh session will hit

- A Windows clone of `gridatlas` needs `-c core.longpaths=true`, and **12 files under
  `nightly/…/runs/` are still left absent while git reports success**. Measure a fresh clone here
  and you measure an incomplete tree.
- `python3` is a broken Store stub. `python`.
