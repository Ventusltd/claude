# Overnight lane board — 2026-09-05

**This file is how Codex, and anyone reviewing by morning, sees what the lanes
did.** It is written to GitHub, not held on the laptop: anything unpushed is
invisible. Every lane appends one row per shipped unit of work and pushes it in
the same commit as the work, or immediately after.

Times are UTC. Vikram's clock is BST, +1.

## Lanes tonight

| lane | owns | must not touch |
|---|---|---|
| **A** — main session `184379c4` (vikra-11) | `globalgrid2050`, `gridatlas`, `claude` | `pipelinenews` |
| **B** — subagent, Pipeline News | `pipelinenews` | `gridatlas` |
| **Codex** | its own `codex/*` branches | any lane's `main` commits |

`gridatlas/atlas/current.json` and `globalgrid2050/index.html` are single files
every generation must touch and git cannot merge meaningfully. One lane each.

## Log

| UTC | lane | repo | commit | what | verified |
|---|---|---|---|---|---|
| 01:25 | A | claude | `31bc1a2` | carry-on handover filed in the repo, where it can be found | github 200 |
| 01:31 | A | claude | `6e85062` | renamed it `00-LOG.md`, the entry point CLAUDE.md already documents | github 200 |
| 01:39 | A | globalgrid2050 | `a4faffc1` | front page shows only what is being built now; old page archived byte-identical at `/historical_builds.html`; search wired for the first time; `catalogue-gridatlas-v9.yml` retired with its reasoning | live 5,934 bytes, was 111,836 |
| 01:45 | A | globalgrid2050 | `6ecc0dc0` | carried the 15 published-version labels the exact-commit gates require, read from the archive rather than retyped; corrected v9.7/v9.6.2 to the estate's own CANDIDATE / LIVE VALIDATED labels | gates re-running |
| 02:00 | A | globalgrid2050 | `1a6445cc` | spiders link off the front page on his word; engine-graph row says what it is | live |
| 02:58 | A | gridatlas | (built, unpushed) | v9.117 gen 202609050158: attribution out of the map into About, last, small print; About gains an Estate group (engine graph, federation map, spider printer) | proof 17/17 made to fail first; suite 779/780 |
| 02:05 | B | pipelinenews | `4fc83af` | release `202609050200-pipelinenews`, cartridge `the-control-names-the-table`: the WIDER FLEET *other technologies* control stops naming a cut the table has stopped showing | see B1 below |
| 02:06 | B | globalgrid2050 | `e4f32ae4` | published that release to `pipelinenews_intelligence/202609050200/` — **a new directory only; `index.html` not touched** | live 200; served bytes SHA-256 identical to the release; 6 of 6 → 0 of 6 |
| 03:05 | A | ventus-grid-engine | `30efa2b` | receiver takes `?focus=<module>` so a dashboard menu can link INTO one piece of maths; proof run against the pre-change bytes first and failed 5/8 there | live 200, confirmed in Chrome landing on `engine/v9-nearest-search.js` |

## Open at the time of writing

- Six exact-commit gates (V9.3–V9.7) went red on `a4faffc1` and are re-running on
  `6ecc0dc0`. They were green on `5260db10`, so the red was lane A's change, read
  from the run log, not guessed.
- `Verify published versions are reachable` was already failing before tonight.
  Pre-existing; not touched yet.
- **V9.5.1 / V9.6.1 / V9.6.2 / V9.7 exact-commit gates are red for a reason that is
  not any commit.** Read from the V9.7 run log: the gate recomputes news scoring and
  the fixture has aged - `recency: 10` is now `8`, `confidence: 91` is now `89`,
  `runner_up_score: 91` is now `89`. A gate whose expectation moves with the clock
  fails on every push until the clock is frozen for the fixture. V9.3, V9.4 and V9.5
  went green again once the published-version labels were carried, so those four are
  a separate, time-driven fault. **Lane B territory; named, not papered over.**
- Two Pages deploy workflows run on every push to `globalgrid2050`
  (`Deploy GlobalGrid2050 Pages` and `Deploy Jekyll…`). Noted, not changed.

## Defects named by Vikram tonight, 2026-09-05

Verbatim, so nothing is softened in the retelling:

1. *"other technologies sort also brings up solar"* — Pipeline News technology
   filter leaks. **Lane B, priority.**
2. *"the UI via deeplink into gridatlas can be awkward as the cards get in the
   way"* — arrival from a deep link is obstructed by cards. **Lane A.**
3. *"the scoping menu has nothing it seems"* — SCOPE menu appears empty. **Lane A.**
4. *"the polyzone undergrid doesnt work"* — **Lane A.**
5. Attribution must move out of the menus, into the ABOUT panel. **Lane A.**
6. The MAP button must be fixed. **Lane A.**
7. As many REPD deep links tested as possible. **Lane A.**

The engine graph is the map for several of these:
https://ventusltd.github.io/ventus-grid-engine/?graph=engine-graph
It shows five separate deep-link/bucket implementations and marks them
DUPLICATES of one another. Where a fix has to be made in five places, it has
been made in one — that is the shape of defects 1, 2 and 7.

---

## Lane B — Pipeline News

### B1 · 202609050205 · the WIDER FLEET control stops naming a cut the table has stopped showing

| | |
|---|---|
| stamp | `202609050205` (pipelinenews) / `202609050206` (globalgrid2050) — both `date -u` in the commit command, verified from `git log --format=%ct` |
| commits | `Ventusltd/pipelinenews@4fc83af` · `Ventusltd/globalgrid2050@e4f32ae4` |
| release | `202609050200-pipelinenews`, built from `202609040144-pipelinenews` by cartridge `the-control-names-the-table` |
| live URL | https://globalgrid2050.com/pipelinenews_intelligence/202609050200/ |
| HTTP | 200 (index 24,916 B · app.mjs 92,700 B · wider-fleet.mjs 27,213 B) |
| served == release | SHA-256 identical on all three, served vs release directory, LF-normalised |

**The defect.** WIDER FLEET is the product's *other technologies* control — the
twenty REPD types outside the spine's four. Choosing one renders its own rows.
The cartridge let go of the table when one of the spine's five technology tabs
was clicked, **and on nothing else**, so every other control that repaints
repainted the spine's own rows underneath it while the control, and the note
above the table, went on naming the wider cut.

Measured live on `202609040144`, WIDER FLEET = Landfill Gas (275 rows, 787.87 MW):

| control used | table then held | control still said |
|---|---|---|
| SORT county A–Z | 24 solar, 45 battery, 31 onshore | LANDFILL GAS |
| COUNTY select | 24 solar, 43 battery, 31 onshore | LANDFILL GAS |
| STATUS Operational | 3 solar, 1 battery, 2 onshore | LANDFILL GAS |
| COUNTY column header | 3 solar, 1 battery, 2 onshore | LANDFILL GAS |
| CLEAR FILTERS | 9 solar, 36 battery, 55 wind | LANDFILL GAS |

Zero landfill-gas rows in all five, under a counter reading *7,680 of 7,680*.
This is Vikram's *"other technologies sort also brings up solar"*.

**The fix.** Not a list of control ids — a hand-kept list of controls is the same
mistake as a hand-kept list of technologies one layer up. `apply()` is the single
place the spine repaints from its own payload (all fourteen handlers end there),
so `apply()` now announces it through a **release seam** beside the existing
summary seam. The wider-fleet cut registers there and calls its own existing
`clearWider()`. The mount argument is fatal if absent, and
`WIDER_FLEET_CONTRACT.releases_on_spine_repaint` is invarianted at mount, so the
two halves cannot drift apart unnoticed.

**Measurement.** Six triggers driven in Chrome against each release's served
bytes over an HTTP origin:

| release | triggers that left the control naming a cut the table no longer showed |
|---|---|
| `202609040144` parent | **6 of 6** |
| `202609050200` child, local | **0 of 6** |
| `202609050200` child, **live** | **0 of 6** |

The gate was made to fail before it was trusted passing. Regression checked: the
wider fleet still renders (LANDFILL GAS 50 rows; FLYWHEELS 1 row / 400 MW /
counter `1 of 1,101 records`), the empty option returns the reader to the tab
they left, OFFSHORE returns `109 of 7,680` with 100 Offshore Wind badges and
nothing else, and the mount reports `OK · 20 more REPD technology types in one
control · 1,101 projects · 22.71 GW` — which is the new invariant passing.

**Open, and named rather than left silent:**

- `globalgrid2050/index.html` line 197 still names `202609040144` as the latest
  intelligence release. **Lane A is editing `index.html` tonight** (`1a6445cc`,
  `6ecc0dc0`, `a4faffc1`), so Lane B did not touch it. One href change:
  `./pipelinenews_intelligence/202609040144/` → `.../202609050200/`, and the link
  text with it. **Lane A or Vikram, please take it.**
- `pipelinenews/releases/current-v4.json` still points at
  `202609040144-pipelinenews` with `classification: VERIFIED_LIVE_TIMESTAMPED_RELEASE`.
  Moving the pointer is a promotion decision with its own gate
  (`tools/publication/prove_pages_promotion_wrapper.mjs`); not taken unilaterally.

**A correction against myself, worth carrying.** Before this, I "measured" that
selecting ONSHORE and then changing the sort switched the technology filter to
BESS. It did not. A previous probe had timed out at the CDP layer *and kept
running in the page*, so two scripts were driving the same controls. The reading
was my own instrument, not the app. Re-run in isolation with a `__running`
refusal flag, technology × sort is exact:
`wind_onshore` × {capacity_desc, county_asc, town_asc, postcode_asc, grid_asc,
updated_desc} → 100 Onshore Wind badges, `2,399 of 7,680`, every time.
**A CDP timeout is not a stopped script.**

---

### Also measured tonight, no change shipped yet

- **`uk_renewables_pipeline/v9.7` technology filter is exact.** ALL 7,680 =
  3,563 Solar + 1,609 Battery + 2,399 Onshore + 109 Offshore; each tab returns
  only its own badge. The data agrees: cross-tab of `technology` ×
  `repd_technology` over all 7,680 records is four cells, no leakage.
- **The v9.7 newspaper SOLAR/BESS chips are exact** (77 + 56 = 133), but every
  story that is not exactly `BESS` is painted with the `solar` CSS class —
  there is no wind class in `styles/v7.css` at all. One `SOLAR + BESS`
  international item is painted `bess`.
- **Six other technology-bucket implementations disagree across the estate.**
  Full survey in `03-LANE-B-technology-bucket-drift.md`.
