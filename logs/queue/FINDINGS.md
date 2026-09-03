# FINDINGS — Lane A, discovery

Newest first. Every entry was produced by driving two releases through the same
reading in real Chrome, on a stated viewport, and diffing the numbers. A finding
with no numbers in it is not in this file.

Instruments: `claude/sessions/202609040030-ab-discovery/{ab,maphref,probe,pager,timeline,timeline2}.py`,
all built on `claude/familiars/clicker.py`'s `Browser` (own Chrome, own port, own
profile, listeners armed before the page's scripts run, refuses to report a
reading taken while `document.hidden` is true). `document.hidden === false` at
every measurement below. Releases served locally on port 8971 from
`pipelinenews/releases/<generation>-pipelinenews/index.html`.

Downloads were denied at the browser level (`Browser.setDownloadBehavior`) for
every run, so no CSV this lane provoked reached disk. Verified against
`~/Downloads`: newest CSV there is 20:31 UTC, before the first run at 23:19 UTC.

---

### The Atlas deep link shows the identity with no measurement for 9.4 seconds, and that is the architect's screen

severity: defect
seen: live `gridatlas/atlas/` (V9 composed shell), 393x852 coarse-pointer, cold
profile, three network profiles, 2026-09-03 23:28-23:33 UTC
measured: the architect's exact URL
(`?repd_ref=155&project=Markinch+Biomass+CHP+Plant&technology=biomass&capacity_mw=65&latitude=56.20118&longitude=-3.16226&zoom=12`),
sampled every 250 ms from the instant of navigation and reported as state
transitions:

| profile | bare map, no popup | identity popup, **no measurement** | measurement on screen |
|---|---|---|---|
| unthrottled | 0.78 - 4.03 s | not observed at 250 ms resolution | **t = 4.03 s** |
| slow-4G (1.5 Mbps, 150 ms) | 2.84 - 7.96 s | **7.96 - 8.32 s (0.36 s)** | t = 8.32 s |
| slow-3G (400 kbps, 400 ms) | 8.62 - 21.62 s | **21.62 - 30.99 s (9.37 s)** | **t = 30.99 s** |

During the identity-only window the DOM holds exactly ONE popup:
`class="maplibregl-popup maplibregl-popup-anchor-bottom"`, rect `[89, 284, 216, 142]`,
`z-index: auto`, and its text is
`Markinch Biomass CHP Plant | biomass | 65 MW | Markinch, Fife - Fife | REPD 155 ...`
— the architect's screenshot, field for field, with `has_measure: false`.

**Theory 2 is ruled out by measurement.** There are never two popups. At
t = 30.99 s the popup carrying the measurement has the *same* class
`maplibregl-popup-anchor-bottom` and simply re-renders from `[89,284,216,142]`
to `[0,358,393,494]` with `z-index: 400`. One element, content replaced. So this
is not ordering, not z-index, and not an off-screen sheet — it is theory 1, and
the wait is long enough to photograph on any real phone.

evidence: `sessions/202609040030-ab-discovery/t2-slow3g-mobile.json` (9 transitions),
`t2-slow4g-mobile.json` (7), `t2-none-mobile.json` (5); one-second timelines in
`tl-slow4g-mobile.json`, `tl-none-mobile.json`; shots
`sessions/202609040030-ab-discovery/shots/timeline-*.png`. Zero console errors in
every run.
proposed fix: the card must render its measurement slot from the moment the
identity resolves, occupied by a statement that the measurement is being computed
for THIS project — an absence that announces itself. The general fix is in the
deep-link card, not in REPD 155.

---

### `dataset.gridatlasRepdDeepLink === "resolved"` 9.4 seconds before any measurement exists

severity: defect
seen: live Atlas, 393x852, slow-3G, 2026-09-03 23:32 UTC
measured: at t = 21.62 s `document.body.dataset.gridatlasRepdDeepLink` reads
`"resolved"` while `.gridatlas-sheet` does not exist, `.neon-answer` does not
exist, and no popup on the page contains the string `km straight`. It still reads
`"resolved"` at t = 21.88 and t = 30.99. The answer first exists at t = 30.99 s.
evidence: `t2-slow3g-mobile.json`, transitions at t=21.62 and t=30.99 —
`deep: "resolved"`, `sheet: false`, `answer_len: 0`.
proposed fix: `resolved` currently means "the identity was found", and every gate
that reads it as "the reader has an answer" passes in exactly the failing state.
The dataset needs a second value the page sets only once a measurement is
rendered, so a check can tell the two apart.

---

### The only "still working" text sits 221 px away from the popup and talks about links, not this project

severity: defect
seen: live Atlas, 393x852, slow-3G, 2026-09-03 23:32 UTC
measured: during the identity-only window the one visible element matching
computing/measuring/resolving/loading is a `DIV` reading
`"Loading the substation data — the links need it."` at rect `[98, 14, 197, 49]`.
The identity popup is at `[89, 284, 216, 142]`. The gap between the label's bottom
(y=63) and the popup's top (y=284) is **221 px**. `in_popup: false`,
`in_sheet: false`. It also appears 0.26 s AFTER the popup (t=21.88 vs t=21.62),
so the first quarter-second offers nothing at all.
evidence: `t2-slow3g-mobile.json`, `working_label` at t=21.88.
proposed fix: the waiting statement belongs inside the card, in the slot the
answer will occupy, and should name the measurement rather than the layer load.

---

### 40 of the 278 mapped 400 kV substations have no name

severity: defect
seen: `gridatlas/atlas/releases/202608300453-atlas-v9/data/grid_substations.geojson`,
5,800 features, read 2026-09-03 23:33 UTC
measured: features whose `properties.voltage` contains `400000`: **278**. Of
those, **238 carry a non-empty `name`; 40 do not — 14.4%.** That is why REPD 155's
card reads `Nearest 400 kV substation: Unnamed substation - 28.82 km straight -
~35.9 km corridor estimate`. Across all 5,800 substation features, 1,340 (23.1%)
are unnamed. (`atlas/world/grid_400kv.geojson` is the circuit layer, a different
set: 4,106 features, 3,553 unnamed — do not quote it for this.)
evidence: counts reproducible with a `voltage` split on `;` over that one file.
proposed fix: for the 40, fall back to a checkable identifier a reader can act on
— operator plus grid reference, or the source id — rather than the word
"Unnamed" beside a measured distance.

---

### The project identity is on screen three times on a deep-link arrival

severity: defect
seen: live Atlas, 393x852, unthrottled and slow-3G, 2026-09-03 23:30-23:33 UTC
measured: `document.body.textContent` contains `"Markinch Biomass CHP Plant"`
**3 times** once the sheet is open (and 2 times during the identity-only window).
The three carriers are the `.search-bar-wrapper` at `[122, 100, 261, 44]` —
holding `Markinch Biomass CHP Plant | Markinch, Fife - Fife | 65 MW - REPD 155 |
Hill Street | 155 metres south west of...` — plus the card's title bar and the
card body. Before the identity resolves the same wrapper is 283x24 at `[95, 149]`
and reads only `GO`.
evidence: `t2-none-mobile.json` and `t2-slow3g-mobile.json`, fields
`identity_repeats` and `search_bar`.
proposed fix: v9.97 removed the results list; the search bar still restates the
answer. One of the three should carry the identity and the other two should not.

---

### REGRESSION — the product is a further 0.6 screens down the page than it was on 29 August

severity: regression
seen: 202608291447 vs 202609032251, 393x852, 2026-09-03 23:26 UTC
measured: distance from the top of the document to each control, same viewport,
at rest:

| | 202608291447 | 202609032251 | change |
|---|---|---|---|
| technology row | 2,676 px / **3.14 screens** | 3,174 px / **3.73 screens** | +498 px |
| record counter | 3,118 px / 3.66 screens | 3,890 px / 4.57 screens | +772 px |
| EXPORT strip | 3,064 px / 3.60 screens | 3,836 px / 4.50 screens | +772 px |
| first project row | 3,408 px / **4.00 screens** | 4,180 px / **4.91 screens** | +772 px |
| whole page | 4.86 screens tall | 5.77 screens tall | +0.91 |

Identical readings on 202609031308, so the growth predates 2159/2251 but has
never been given back. The pain log of 2026-09-03 measured 3.8 / 3.9 / 4.9
screens on 202609031308; the newest release reproduces that within 0.02 screens,
so nothing in the last three generations moved it.
evidence: `r3-mobile-1447-vs-2251.json` (`depth`, `screens_tall`),
`r2-mobile-1308-vs-2251.json` for the unchanged middle.
proposed fix: the first project row is the product. It should be reachable
without four flicks — the three prose blocks and the news feed above it are what
grew.

---

### RECEIPT — the frozen record counter is fixed, and the arcs moved with it

severity: improvement-receipt
seen: 202609031308 vs 202609032251, 393x852 AND 1400x900, 2026-09-03 23:20-23:21 UTC
measured: same journey both sides — click SOLAR, then pick the first wider-fleet
technology (`LANDFILL GAS - 275`). After the switch:

| surface | 202609031308 | 202609032251 |
|---|---|---|
| counter | `3,563 of 7,680 records - 67,013.29 MW - largest 840 MW` | `275 of 1,104 records - 787.87 MW - largest 22.5 MW` |
| `dataset.filteredCount` / `totalCount` | `3563` / `7680` | `275` / `1104` |
| gauge arc g1 (`toDataURL` digest) | `#e7e2f15f` — byte-identical to the SOLAR state | `#56299237` — moved |
| g2 | `#99a891ba` — unchanged | `#bfc71125` — moved |
| g3 | `#6fadd84f` — unchanged | `#22674cb6` — moved |
| gauge numbers v1/v2/v3 | `787.87` / `275` / `22.5` — already correct | same |

So on 1308 the counter and all three arcs kept solar's answer while the three
gauge numbers showed landfill gas: the screen disagreed with itself and nothing
threw. On 2251 all five surfaces agree. Identical result at both viewports.
evidence: `r2-mobile-1308-vs-2251.json`, `r2-desktop-1308-vs-2251.json`, blocks
`after_wider`; shots `shots/{m,d}-*-04-wider.png`.

---

### RECEIPT — the export no longer writes 3,563 solar rows under a landfill-gas heading

severity: improvement-receipt
seen: 202609031308 vs 202609032251, both viewports, 2026-09-03 23:20-23:21 UTC
measured: with `LANDFILL GAS - 275` on screen (50 rows rendered, counter as
above), `#exportInline` clicked once:

- **202609031308** — `#exportMeta` becomes `"3,563 filtered records exported"`,
  `is-declined` false, no `dataset.exportDeclinedColumns`, counter still reading
  `3,563 of 7,680 records`. A 50-column CSV of the spine's **solar** rows under a
  landfill-gas view. (The file was blocked by this lane's download guard; on a
  reader's machine it lands.)
- **202609032251** — declines, `is-declined` true, and states the arithmetic:
  *"It can fill 10 of this CSV's 50 columns ... The other 40 ... are joins onto
  the spine's payload, which this cut does not read. A file carrying them blank
  would still leave here looking official, so no file was written."*
  `dataset.exportDeclinedColumns` lists all 40 by name.

evidence: `r2-mobile-1308-vs-2251.json` / `r2-desktop-1308-vs-2251.json`, key
`export_click`. Zero console errors on either side.

---

### The export strip promises the CSV right up until the click that refuses it

severity: defect
seen: 202609032251 (newest), 1400x900, 2026-09-03 23:25 UTC
measured: with `GEOTHERMAL - 5` selected — a cut the release will not export —
before any click: `#exportMeta` reads `"CSV contains the current filtered rows
only"`, `is-declined` **false**, `dataset.exportDeclinedColumns` **null**, and
`#exportInline` is `"EXPORT FILTERED CSV"`, 155x32, `disabled: false`,
`aria-disabled: null`. Identical string to 202609031308 in the same state — the
screen is unchanged by the fix. Only the click reveals the refusal.
evidence: `probe-2251.json`, `geothermal.strip`; same strip reading in
`r2-*.json` `after_wider`.
proposed fix: the decline is already computed the moment a non-spine cut takes
the table. Say it on the strip then, rather than after a reader has asked for a
file they will not get.

---

### MAP is 1,605 px to the right of the screen's left edge, and has not moved in three generations

severity: defect
seen: 202608291447 vs 202609031308 vs 202609032251, 393x852, 2026-09-03 23:20-23:26 UTC
measured: the ACTIONS cell's MAP link, at rest, `getBoundingClientRect()`:

| | left | table window | table width | overflow | flicks @417 px |
|---|---|---|---|---|---|
| 202608291447 | 1,449 px | 361 px | 1,500 px | 1,139 px | 2.7 |
| 202609031308 | 1,605 px | 371 px | 1,680 px | 1,309 px | 3.1 |
| 202609032251 | **1,605 px** | 371 px | 1,680 px | 1,309 px | **3.1** |

The link itself is 44x44 on mobile (25 px tall at 1400x900) and `target="_blank"`.
MAP is column 13 of 13. The overflow grew 170 px since 29 August and has been
static across the last three generations. This is the pain log's entry about four
sideways flicks, still true, now with the pixel count.
evidence: `r3-mobile-1447-vs-2251.json`, `r2-mobile-1308-vs-2251.json`, keys
`map_cell_rect` and `table_scroll`.
proposed fix: MAP is the action every reader in the pain log was reaching for. It
should be reachable without leaving the project's name behind.

---

### The capacity column mixes MW and MWp, and the headline total adds them up as MW

severity: defect
seen: 202609032251 and 202609031308, 1400x900, 2026-09-03 23:25-23:26 UTC
measured: distinct trailing units in the OFFICIAL CAPACITY column of the rendered
window:

- SOLAR cut: **`["MWp"]`** — every one of 100 rows on page 1 and 100 on page 2.
  Top cell `840 MWp`. The counter for that cut reads `3,563 of 7,680 records -
  67,013.29 MW - largest 840 MW` and gauge `v1` reads `67,013.29`.
- ALL TECH cut: **`["MW", "MWp"]`** in one column. Top cell `4,100 MW`. Counter
  `7,680 of 7,680 records - 356,474.09 MW - largest 4,100 MW`.
- Every MAP href carries the same figure under the parameter name `capacity_mw` —
  e.g. `840 MWp` in the cell, `capacity_mw=840` in the link, on 100 of 100 solar
  rows.

evidence: `pager.py` output for both generations (`units`, `cap`),
`probe-2251.json` `solar.cap_pairs`.
proposed fix: either the totals are MWp-inclusive and must say so, or the column
must convert. One label over two units is the part a reader would quote.

---

### A cut of five records at 0 MW sits under a stated >=1 MW floor on the same screen

severity: defect
seen: 202609032251, 1400x900, 2026-09-03 23:25 UTC
measured: `GEOTHERMAL - 5` — counter `5 of 1,104 records - 0 MW - largest 0 MW`;
all 5 rendered rows read `0 MW` (min 0; 5 of 5 below 1 MW; 5 of 5 exactly zero).
Visible on the same page: `"every qualifying >=1 MW record is loaded"` and the
size control's note `"the register itself starts at 1 MW"`. `UNKNOWN - 1` is also
`0 MW - largest 0 MW`; `FUEL CELL (HYDROGEN) - 2` is `0.11 MW - largest 0.11 MW`.
evidence: `probe-2251.json` `geothermal` (`floor`, `counter`, `cap_pairs`),
`maphref-2251.json` per-cut counters; shot
`shots/probe-202609032251-geothermal.png`.
proposed fix: the wider fleet is not the >=1 MW register and the standing
discipline text does not say so. Either the floor statement is scoped to the
spine, or the wider-fleet cut states its own.

---

### Both pager buttons say 50; the window moves 100

severity: defect
seen: 202609032251, 1400x900, 2026-09-03 23:25 UTC
measured: on the SOLAR cut, `#projectWindowControls` holds two buttons, labelled
`"PREVIOUS 50"` (103x34, disabled on page 1) and `"NEXT 50"` (76x34). Reading
before and after one click of NEXT 50: `1-100 of 3,563` -> `101-200 of 3,563`;
rendered rows 100 -> 100; first row `Botley West ...` -> `Low Horton Farm - Solar
Farm ...`. **Step taken: 100.** Wider-fleet cuts render 50 rows per window with
the same two buttons (`1-50 of 275`).
evidence: `pager.py` output for 202609032251 and 202609031308 (`pager`, `rows`,
`first`).
proposed fix: label the buttons with the step they take, or take the step they
are labelled with — and the spine's 100 and the wider fleet's 50 should not share
one label.

---

### Twenty REPD technology types reach the Atlas as eleven

severity: defect
seen: 202609032251, 1400x900, all 25 technologies walked, 2026-09-03 23:23 UTC
measured: for each cut, the row's TECHNOLOGY cell beside the `technology=`
parameter of that row's MAP href. Collapses:

- `biomass` <- Landfill Gas (275), Anaerobic Digestion (253), Biomass dedicated
  (159), EfW Incineration (122), Sewage Sludge Digestion (12), Biomass co-firing
  (2) — **6 types, 823 projects**
- `hydro` <- Small Hydro (108), Large Hydro (28), Pumped Storage Hydroelectricity
  (15) — 3 types, 151 projects
- `tidal` <- Tidal Stream (14), Shoreline Wave (4)
- `caes` <- Compressed Air Energy Storage (2), Liquid Air Energy Storage (2)
- `geothermal` <- Geothermal (5), Hot Dry Rocks HDR (2)
- `hydrogen` <- Hydrogen (60), Fuel Cell Hydrogen (2)
- `other` <- Unknown (1)

So REPD 8795 shows `Landfill Gas` in the table and hands the Atlas
`technology=biomass`; the architect's own REPD 155 arrived as `technology=biomass`
for a plant the Atlas then labels `biomass`. The spine's own slugs
(`Battery Storage -> bess`, `Onshore Wind -> wind_onshore`) are naming, not
collapse, and are not counted here.
evidence: `maphref-2251.json`, field `shown_vs_link` per cut.
proposed fix: the link already carries `repd_ref`, which is exact. Either the
Atlas vocabulary gains the missing types or the card should show the REPD type
rather than the collapsed one.

---

### 15 of 100 offshore rows carry no MAP link at all

severity: defect
seen: 202609032251, 1400x900, 2026-09-03 23:23 UTC
measured: MAP anchors present in the rendered window, by cut — ALL TECH 86/100
(14 cells read `NO MAP`), OFFSHORE **85/100**, ONSHORE 98/100, SOLAR 100/100,
BATTERY 100/100. Every wider-fleet cut is 100%. Identical counts on 202609031308
and on 202608291447, so this has not moved in three generations.
evidence: `maphref-2251.json` (`rows` vs `with_link`), `r2-*.json` / `r3-*.json`
(`map_cells_total`, `no_map_cells`).
proposed fix: the page already explains that missing geometry is labelled NO MAP.
Offshore losing 15% of its rows to it is the concentration worth naming.

---

### The shipped instrument has been counting zero rows and zero MAP cells on every Pipeline News release

severity: defect
seen: `claude/familiars/clicker.py` against 202608291447 ... 202609032251,
2026-09-03 23:19 UTC
measured: two anchors in `journey_summary` and `journey_maplink` match nothing on
any generation of this product:

- `document.querySelectorAll('#results tbody tr')` — no Pipeline News release has
  ever had an element with `id="results"`. The table body is `id="tbody"`. The
  selector returns **0** where the correct one returns **100**. `rows: 0` is
  indistinguishable from an empty table, so the journey has been reporting an
  empty product as a successful reading.
- `/^MAP$/i.test(e.textContent.trim())` in `journey_maplink` — the ACTIONS cell
  reads **`MAP ^`** (MAP followed by a north-east arrow), so the anchored
  equality matches **0** of **86** MAP links at rest. `map_cells` has been `[]`
  on every run.

`#widerTechnology`, `#resultsMeta`, `#exportInline`, `#v1..v3` and `#g1..g3` all
still resolve, so the journeys ran and looked healthy.
evidence: id inventory of `releases/202609032251-pipelinenews/index.html` (65
ids, no `results`); `r2-mobile-1308-vs-2251.json` shows 100 rows and 86 MAP hrefs
from the corrected selectors in `ab.py`, which carry the reason in comments.
proposed fix: repoint both anchors in `clicker.py`, and prefer a CONTENT
precondition — assert the row count is non-zero before reporting any reading
derived from it — so a drifted selector fails loudly instead of returning 0.

---

## Things checked that turned out NOT to be findings

Recorded so nobody spends the night re-measuring them.

- **Pagination is not malformed.** A first pass read `"501-100 of 7,680"` off
  `document.body.textContent` and it looked like a start greater than an end. It
  is the `"NEXT 50"` button's label running into `"1-100 of 7,680"`. Read off
  `#projectWindowControls` the pager is clean. The regex was the defect.
- **The gauge canvases are not oversized.** `attr 1023x360` against `css 341x120`
  at 393x852 is exactly devicePixelRatio 3. At 1400x900 it is `314x120` against
  `315x120`.
- **The three at-rest arcs being byte-identical is not a fault.** At ALL TECH
  every gauge is at its full value; they diverge the moment SOLAR is picked
  (`#e7e2f15f` / `#99a891ba` / `#6fadd84f`).
- **`Battery Storage -> bess` and `Onshore Wind -> wind_onshore` are slug naming,
  not the collapse above.** A first count called all 732 rows mismatched; 732 is
  not the number.
- **202609031308, 202609032159 and 202609032251 ship a byte-identical
  `index.html`** (sha256 `1e9079e1ebea216b...`). 2159 and 2251 also ship an
  identical `app.mjs` (`a6ff44fd6dcc...`); 2251's only change from 2159 is
  `data/202608311610-grid-proximity.json` (`49aaf5c335a2...` -> `beb5e940d005...`).
  The newest release's `sha256sums.txt` verifies 60 of 60.
- **`depth` cannot be read at 1400x900.** The desktop layout scrolls an inner
  container, so `rect.top + scrollY` goes negative (-216 px) after a filter. Only
  the 393x852 depth figures above are sound.
