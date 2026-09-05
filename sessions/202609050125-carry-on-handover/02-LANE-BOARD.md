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
| 02:19 | B | pipelinenews | `e9aef6f` | release `202609050216-pipelinenews`, cartridge `the-pager-belongs-to-the-cut-on-screen`: the shared table pager stops repainting the product's rows under a wider-fleet cut, and stops naming a window size it does not move | see B2 below |
| 02:20 | B | globalgrid2050 | `1b51cf26` | published that release to `pipelinenews_intelligence/202609050216/` — **new directory only; `index.html` not touched** | live 200; served bytes SHA-256 identical to the release; both defects gone on the live URL |
| 02:35 | B | pipelinenews | `6b7890d` | release `202609050233-pipelinenews`, cartridge `every-status-the-register-has`: 2,416 of the 7,680 records were in ten official REPD statuses no control could select | see B3 below |
| 02:35 | B | globalgrid2050 | `347d93fa` | published that release to `pipelinenews_intelligence/202609050233/` — **new directory only; `index.html` not touched** | live 200; served bytes SHA-256 identical; 7,680 of 7,680 now reachable, 0 unreachable |
| 02:49 | B | claude | (this commit) | **TRUNCATION REPORT INVESTIGATED — not reproduced in the app.** `202609031308` and `202609050233` render identically live at 393x852 and at desktop: 100 rows, 13 columns, `7,680 of 7,680 records`, `1-100 of 7,680`, same first and last row, 30 stories, `1-30 of 132`. Served `index.html` is byte-identical across the whole lineage. `app.mjs` grew 83,114 -> 98,813 B; no payload shrank. **The measured truncation tonight is the front page: 111,836 B / 30 Pipeline releases -> 9,359 B / 1** (`a4faffc1`, Lane A, 01:39). Full evidence in `04-LANE-B-truncation-investigation.md`. **Nothing further published; Lane B is holding.** | live, both URLs |
| 03:15 | C | claude | (this commit) | **THE AGENDA AND THE FLAWS — `05-LANE-C-agenda-and-flaws.md`.** 39 repos enumerated from the API (26 active in 7 days), 1,120 commits on default branches, 187 on 53 branches that never merged, 323 of Vikram's own messages read in full across 20 transcripts / 133 MB. Ten located flaws. Three worth acting on first: **F1** the four exact-commit gates crossed a calendar boundary between `5260db10` (green, 04 Sep 22:37Z) and `a4faffc1` (red, 05 Sep 01:39Z) — `major_project_news_v6.py:612` reads `datetime.now()` inside a byte-identity gate, and it decays again on **2026-09-20** and **2026-11-19**; **F2** `Verify published versions are reachable` pins 14 generation stamps and a `v9.99→v9.106` chain in `test_verify_published_versions.py` while live is v9.119, and asserts a homepage block `a4faffc1` deliberately removed — the producer was retired, the consumer check was not; **F3** the sizing double-count is served HTTP 200 at `/solar-bess-topology-v6,-v7/…/gis-sld-v5-calculations.js:147`, byte-identical in five files, beside a correction none of them import. Agenda gap that matters most: **8 of 10 core repos carry no licence file** against *"I am designing this to be open source and public"* (03 Sep 10:20Z). Lane C changed nothing but this row and its report. | all evidence names a commit, a run id or a live URL; `sweep2.py` / `ci.py` / `stamps.py` reproduce it |
| 03:10 | B | pipelinenews | `6e30dc0` | release `202609050309-pipelinenews`, cartridge `the-estate-is-in-the-menu`: the GB price + grid constraint study, engine graph, federation map and spider printer in both navs, plus all 44 engine nodes read from the genome | see B4 below |
| 03:11 | B | globalgrid2050 | `362b679a` | published to `pipelinenews_intelligence/202609050309/` — **new directory only; root `index.html` not touched** | live 200; served bytes SHA-256 identical; 44 nodes load cross-origin on the real globalgrid2050.com origin |

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

### B2 · 202609050219 · the pager belongs to the cut on screen, and stops naming a window it does not move

| | |
|---|---|
| stamp | `202609050219` (pipelinenews) / `202609050220` (globalgrid2050), `date -u` in the commit command, checked against `git log --format=%ct` |
| commits | `Ventusltd/pipelinenews@e9aef6f` · `Ventusltd/globalgrid2050@1b51cf26` |
| release | `202609050216-pipelinenews`, from `202609050200-pipelinenews` |
| live URL | https://globalgrid2050.com/pipelinenews_intelligence/202609050216/ |
| HTTP | 200; `index.html`, `app.mjs`, `wider-fleet.mjs` all SHA-256 identical served vs release |

**Two defects on one shared control.** The table pager is a single panel used by
the product *and* by any wider-fleet cut on screen, and the spine's handler moves
`windowStart` and calls `renderTable()` **directly**, not through `apply()` — so
the release seam shipped in B1 could not see it. The cartridge's capture-phase
listener did not stop the press either, so both handlers ran on every click.

Measured live on `202609050200`, WIDER FLEET = LANDFILL GAS showing `1–50 of 275`:

| | |
|---|---|
| one press of NEXT | `101–200 of 7,680` |
| what was on screen | 16 solar · 71 battery · 6 onshore · 7 offshore · **0 landfill gas** |
| what the control said | LANDFILL GAS |

And the same two buttons said **PREVIOUS 50 / NEXT 50** while moving the spine's
window of **100** (`1–100` → `101–200`). They also serve the wider cut, whose
page is 50, so no number on those buttons can be true of both cuts.

**The fix.** `event.stopPropagation()` in the cartridge's pager listener once it
has decided the press is its own — which is what its own comment, *"the spine
owns its own paging"*, already claimed. `windowStart` is left untouched while a
cut holds the table and `apply()` zeroes it on return, so nothing is left
half-paged. The number comes off the buttons; the range readout between them is
derived and already states the exact window for whichever cut is showing.
`WIDER_FLEET_CONTRACT.owns_the_pager_while_showing` is invarianted at mount.

**Measurement, on the live URL:**

| | `202609050200` parent | `202609050216` child, live |
|---|---|---|
| button labels | PREVIOUS 50 / NEXT 50, moves 100 | PREVIOUS / NEXT, moves 100 |
| pager under a wider cut | `1–50 of 275` → `101–200 of 7,680`, 0 landfill gas | `1–50` → `51–100` → … → `251–275 of 275`, NEXT disabled at the end, 25 rows on the last page, **0 spine rows leaked** |
| product paging afterwards | — | `1–100 of 7,680` → `101–200 of 7,680` |

Regressions re-run on the child: the six B1 triggers plus a spine technology tab
are **0 of 7**; the wider-fleet deep link still arrives
(`?technology=Landfill+Gas` → `275 of 1,101 records`, 787.87 MW, mount reports
`deep link · Landfill Gas`).

**Also measured, no defect found:**

- **All ten sort modes are correct.** Each was checked for monotonicity across
  the rendered window: `county_asc/desc`, `town_asc/desc`, `postcode_asc/desc`,
  `capacity_desc/asc`, `updated_desc/asc` — no break in any of them.
- **The phone path holds at 393×852.** Measured in a same-origin 393-wide
  iframe, so the media queries actually fire (a resized Chrome window did not
  change `innerWidth` here). No horizontal document overflow: `scrollWidth` 380
  against a 390 viewport; the table scrolls inside its own `overflow-x:auto`
  wrapper (1,680 wide in a 347 box), which is the intended behaviour. Both nav
  variants are `display:none` at that width, but the `RELEASES` opener is 82×44
  at the top right and opens a 360×679 menu of 20 links, every one 44px tall.
  **v9.7's discontinued-v9.6 mobile failure has not recurred here.** One gap:
  the opener never sets `aria-expanded` — noted, not fixed.

### B3 · 202609050235 · every status the register has, not the four the row draws

| | |
|---|---|
| stamp | `202609050235` in both repos, `date -u` in the commit command, checked against `git log --format=%ct` |
| commits | `Ventusltd/pipelinenews@6b7890d` · `Ventusltd/globalgrid2050@347d93fa` |
| release | `202609050233-pipelinenews`, from `202609050216-pipelinenews` |
| live URL | https://globalgrid2050.com/pipelinenews_intelligence/202609050233/ |
| HTTP | 200; `index.html` and `app.mjs` SHA-256 identical served vs release |

**The defect.** The status row draws four of the register's **fourteen** official
REPD statuses. Measured by clicking every status control on the live parent and
reading its own filtered count:

| | records |
|---|---|
| reachable by a status control | **5,264** |
| reachable by no control at all | **2,416** — 31.5% of the register |

Application Refused 667 · Revised 531 · Application Withdrawn 420 · Appeal
Refused 295 · Planning Permission Expired 227 · Abandoned 221 · Appeal Withdrawn
39 · Decommissioned 9 · Appeal Lodged 5 · No Application Required 2.

Every one of those rows was loaded, searchable, sortable and in the CSV. None
could be *selected*. `?status=Abandoned` was silently coerced to `All` by a
five-member whitelist — **221 records answered with 7,680, and no word about
why.** Nothing on the surface said the four tabs stop 2,416 records short of the
register, which is precisely what the product's own STATUS DISCIPLINE panel
promises it will not do.

**The fix.** One labelled select in the status row, on the pattern the
technology row already settled on after the same objection from Vikram. Names
and counts read from the payload at boot and never listed in source, so a status
DESNZ adds tomorrow gets an option with its own count and no edit. It reuses the
wider-fleet control's existing classes — no CSS change, same 44px phone floor.
It is **not** a separate cut: it sets the spine's own `status` and calls the
spine's own `apply()`. `releaseWiderStatus()` is the single place the select and
the four tabs are reconciled, and the tabs, CLEAR FILTERS and
`hydrateFiltersFromUrl` all call it — the same discipline as B1, one row up.

**Measurement, on the live URLs:**

| | `202609050216` parent | `202609050233` child |
|---|---|---|
| MORE STATUS control | absent | 10 options + placeholder |
| reachable by a control | 5,264 of 7,680 | **7,680 of 7,680** |
| unreachable | 2,416 | **0** |
| `?status=Abandoned` | 7,680 records | **221 records**, table holds `Abandoned` and nothing else |
| each option's own cut | — | 667 / 531 / 420 / 295 / 227 / 221 / 39 / 9 / 5 / 2, **every one pure** |

**One tightening came with it:** the status test moves from
`item.status.includes(status)` to equality. Substring and equality agree exactly
on the four tab values across all 7,680 records — 2,232 / 282 / 1,910 / 840,
leak zero — so **no answer changes today**. It is tightened because the control
now reaches ten more values, and `Appeal Refused` inside `Application Refused`
is the pair a substring test finds the day one more status is added.

**Regressions, all on the child:** the wider-fleet six-trigger check is 0 of 6
with the new MORE STATUS select added as a trigger; the pager still holds the
wider cut (`1–50` → `51–100 of 275`, 50 Landfill Gas badges) and the product
returns to `1–100 of 7,680`; CLEAR FILTERS resets the select and ALL STATUS;
both wider controls mount. At 393×852 the new select is 44px and the document
does not overflow (`scrollWidth` 379 against a 389 viewport).

---

## Lane B — two corrections against myself

Both are the same root cause, and it is worth carrying.

**1. A CDP timeout is not a stopped script.** A `Runtime.evaluate` that times out
at the transport keeps running in the page. Two probes then drove the same
controls at once and I read the result as a finding: *"selecting ONSHORE and
then changing the sort switches the technology filter to BESS."* It does not.
Re-run in isolation behind a `__running` refusal flag, `wind_onshore` × six sort
modes returns 100 Onshore Wind badges and `2,399 of 7,680` every time.

**2. A background tab throttles `setTimeout` to about once a minute, so any
probe built out of `await sleep(...)` reads the DOM at times it did not choose.**
That produced a second false finding — the ALL news chip appearing to drop from
132 headlines to 100 and back. Re-measured with **no timers at all** (both
`apply()` and `drawNews()` are synchronous, so click and read in the same task),
the sequence is 132 → 77 → 55 → 1 → 132 → 132, stable and repeatable.

**The rule that follows:** when the code under test is synchronous, *never* put a
timer in the instrument. Where a timer is unavoidable, guard re-entry and make
the probe refuse rather than overlap. Both B1 and B2 were re-confirmed against
this standard before shipping.

### B4 · 202609050310 · the estate is in this product's own menu, and the engine list is read not retyped

| | |
|---|---|
| commits | `Ventusltd/pipelinenews@6e30dc0` · `Ventusltd/globalgrid2050@362b679a` |
| release | `202609050309-pipelinenews`, from `202609050233-pipelinenews` |
| live URL | https://globalgrid2050.com/pipelinenews_intelligence/202609050309/ |
| HTTP | 200; `index.html`, `app.mjs`, `orientation.css` all SHA-256 identical served vs release |

Answers two of Vikram's asks: *"add this to the appropriate menuw on gridatlas
and pipeline news"* and *"why are the drop down engines here NOT in the menus of
gridatlas and pipelinenews"*.

**Where.** Both navs — the desktop sidebar and the RELEASES popover a phone opens
— get the same five rows after MAP ATLAS, as the same markup twice with no ids.
All four URLs **probed 200 before being written into the menu**: the study
(32,345 B), the engine graph, the federation map, the spider printer. The study
is **also** linked beside the product's own OPEN GB ELECTRICITY CONTEXT button,
which is where a reader of this product already goes for price.

**The 44 nodes are not listed in source.** They are read from
`ventus-grid-engine/genome/engine-graph.json`, so a node added there appears
here with no edit — which is the whole subject of that graph. Each row links to
`?graph=engine-graph&focus=<label>`; the receiver matches the node's own label.

**Cross-origin, checked rather than assumed.** The page is on
`globalgrid2050.com`, the genome on `ventusltd.github.io`. GitHub Pages answers
with `Access-Control-Allow-Origin: *` — verified against the live URL with a
real `Origin: https://globalgrid2050.com` header **before** the code was
written, then verified again by loading the list on the real origin.

**It is not allowed to fail quietly.** Fetched only when the reader opens the
list; failure prints its own reason where the list would have been, in amber,
and says the ENGINE GRAPH link still works; the promise is cleared so the next
tap is a real retry; the button shows no count until it has one.

| measured | result |
|---|---|
| live, on `globalgrid2050.com` | 44 nodes · CANONICAL 11 / EXTRACT 1 / REFERENCE 1 / FRAGMENT 31 · **0 of 44** links missing `focus=` |
| **fail-first** — genome fetch broken in a fresh document before the first tap | state `failed`, **0** node links, amber `rgb(255,204,0)`, *"ENGINE NODES UNAVAILABLE · Failed to fetch · the ENGINE GRAPH link above still opens the graph itself. Tap again to retry."*, button still `ENGINE NODES` with **no invented count** |
| retry, fetch restored, same document | ready, 44 nodes |
| end-to-end | `?focus=engine/v9-nearest-search.js` lands the receiver on that node — select reads `engine/v9-nearest-search.js`, card is that module, `1 dependencies · 4 dependents` |
| 393×852 | menu 360×681, scrollable 1,116 over 679, every link **44px**, every node row **44px**, no horizontal overflow |

**A defect of my own, found and fixed before shipping.** The first build measured
the ENGINE NODES toggle at **37px** on a phone against the 44px every link beside
it meets — it is the one row in that menu that is a `<button>`, so it did not
inherit the floor. `min-height` and a flex centre; re-measured at 44px. **That
build was discarded, not published.**

No MutationObserver and no DOM observation of any kind: the toggle writes into
one container it owns, on a click.

**Said plainly:** `index.html` in `pipelinenews_intelligence/` is no longer
byte-identical across the lineage — 24,916 B up to `202609050233`, 26,831 B
here. That byte identity was the evidence used in the truncation investigation,
so: it holds for every release up to and including `202609050233`, and this
release adds menu rows on purpose.
