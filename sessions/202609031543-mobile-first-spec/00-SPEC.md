# GridAtlas Atlas — mobile-first design specification and staged plan

Generation of this document: 202609031543
Composition measured: GridAtlas `atlas/current.json` generation **202609031316**, version ledger newest **v9.89** (`9593f0a`)
Live route measured: `https://ventusltd.github.io/gridatlas/atlas/`

This is a specification and a plan. Nothing in the Atlas was changed to produce it.

---

## 0. How this was measured, and what could not be

### 0.1 `resize_window` is still broken on this machine — confirmed, not assumed

```
resize_window(tabId, 402, 874)
  -> "Successfully resized window containing tab ... to 402x874 pixels"
  -> window.innerWidth  1707   (unchanged)
  -> window.innerHeight  842   (unchanged)
  -> matchMedia('(max-width: 480px)').matches  false
```

The tool reports success and the viewport does not move. Every mobile number below therefore comes from a different method.

### 0.2 The method that did work: a same-origin frame at a fixed CSS width

The Atlas is served from `ventusltd.github.io`. Loading `https://ventusltd.github.io/gridatlas/` and injecting an `<iframe>` of a declared CSS size, whose `src` is the Atlas deep link, gives a **genuine** narrow viewport: inside the frame `window.innerWidth` is 390 (or 402, or 430), media queries evaluate at that width, `100dvh` resolves to the frame height, and MapLibre lays out against it. Same origin, so `contentDocument` is readable and every box is measurable with `getBoundingClientRect()`.

Measured this way at **390 × 664** (iPhone-class content box), **402 × 874**, **430 × 780**, **360 × 640**, and **1400 × 900** for the desktop baseline.

### 0.3 What this method cannot see, and where I fall back to the architect's screenshots

| Not observable in the frame | Consequence | Fallback |
|---|---|---|
| `pointer: coarse` — the frame reports a fine pointer | The `@media (pointer:coarse)` block in `sld-sandbox` (`min-height:44px` on `.map-ctrl-btn`, `.search-btn`, `.search-input`) did **not** apply. My raw 23 px for the search field is therefore an artifact. | Architect screenshots; treated as *unverified* below, not asserted. |
| Fullscreen API inside a frame | `enterFullscreen()` sets the classes but `requestFullscreen()` cannot succeed | The class-driven layout is what matters and it did apply (`#map-container.map-container.is-fullscreen`). |
| Browser chrome (URL bar, home indicator) | The frame is pure content | Derived from the screenshots: 1320 × 2868 device px at dpr 3 = **440 × 956 CSS**, of which ≈ **817 CSS px** is web content. |
| The topology checkbox list | It never populated in the frame (`.scada-keys` measured 5 px, 0 checkboxes) | Measured off screenshot `10a550cc`. Row pitch ≈ 30 CSS px, checkbox ≈ 22 CSS px. |

Everything stated as a number below was measured unless the sentence says "derived from the screenshot" or "unverified".

---

## 1. The measured current state

### 1.1 The viewport budget — where the phone screen actually goes

**State A — plain arrival, no deep link (screenshot `10a550cc`).** Measured at 390 × 664:

| Band | Box | Share of a 664 px viewport |
|---|---|---|
| `.hud-header` (SYSTEM TIME / VENTUS / 2050 TARGET) | `4,4 382×68` | 10.2 % + 8 px padding |
| `#map-container` | `4,76 382×458` | **69 %** |
| `.scada-wrapper` (legend, disclaimer, layer list) | `4,538 382×122` | 18.4 % |

That 69 % is the *best* case: the layer list was empty in my frame. `.scada-wrapper` is capped at `max-height:38vh` (`ventusv8.css:12`), which is 252 px at 664. On the architect's device, with the list populated, the same bands measure (derived from screenshot `10a550cc`, ±5 %):

| Band | CSS height | Share of ≈817 px of web content |
|---|---|---|
| header | ≈ 70 | 8.6 % |
| **map** | **≈ 362** | **44 %** |
| legend + topology list + disclaimer | ≈ 348 | 43 % |

**The map gets 44 % of the phone screen on the architect's device.** The other 56 % is a clock, a brand mark, a countdown, a four-dot legend, a checkbox list and a disclaimer paragraph in 9 px type.

There is no page scroll to recover any of it: `html` and `body` both compute `overflow: hidden`, and `.dashboard` is `height:100dvh`. Anything that does not fit is not reachable — it is gone.

**State B — deep-link arrival, fullscreen (screenshot `851f6587`).** Measured at 390 × 664:

| Element | Box | z-index |
|---|---|---|
| `#map-container.is-fullscreen` | `0,0 390×664` | 500 |
| `.custom-map-attrib` | `10,44 359×38` | 10 |
| `.search-bar-wrapper` | `99,100 282×23` | **20** |
| `#search-results` | `39,136 301×91` | **21** |
| `.maplibregl-popup` (the project card) | **`-89,116 340×621`** | **auto** |
| `.map-controls` (TOOLS/GRID/SUBS/SCOPE/CLEAR + GB PRICES + VERSIONS) | `10,511 362×123` | **20** |
| `#gridatlas-dash-toggle` (HIDE LAYERS) | `293,608 86×44` | 9999 |
| `.podcast-shoutout` | `56,631 322×18` | 10 |

Full-bleed is achieved — and the whole screen is then covered by the card.

### 1.2 The overlap defect has three separate causes, not one

The card carries **no z-index** (`z-index: auto`, i.e. 0 in the map's stacking context; it only becomes `z-index:12` after a drag, via `.maplibregl-popup.gridatlas-free`). Every floating control has `z-index: 20` or higher. On a phone the card is 340 × 621 — **53 % of the screen** — so every control that was designed to float over *the map* now floats over *the card*.

Measured coverage at 390 × 664: of the card's visible area (251 × 548 = 137,548 px², after left-edge clipping — see below), roughly **50,000 px² ≈ 36 % is painted over by other UI**:

| Overlay | Area over the card | Cause | Conditional? |
|---|---|---|---|
| `#search-results` | ≈ 19,300 px² | The deep-link path calls `selectResult(exact)` (`place-global-search:512`) and sets `input.value = repdRef` (`:517`) but **never dismisses the results list**. It stays open at `z-index:21` for the life of the session. | **No.** Present in both architect screenshots and in every frame load I did. |
| `.map-controls` | ≈ 29,600 px² | Geometry. `ventusv8.css:49` — `position:absolute; bottom:30px; left:10px; z-index:20`. Correct against a map; wrong against a card that fills the map. | **No.** Installed whenever `pointer:coarse` or `innerWidth ≤ 700` (`sld-sandbox:5487`). |
| `.search-bar-wrapper` + GO | ≈ 1,100 px² | Geometry. `ventusv8.css:37` — `top:72px; right:10px` (`top:100px` under `body.fs-active`), width 282. A 340 px card plus a 282 px search bar is 622 px of demand on a 390–430 px screen. | **No.** |

**The single cheapest fix in this whole document is the first row.** It is not a z-index architecture problem; it is a dropdown that is never closed. It is five lines in one cartridge and it removes the most visible defect in the architect's screenshots.

**Desktop does not have this problem, and the arithmetic says why.** At 1400 × 900 the card sits at `587,-145 340×666` and the search bar at `1104,148 282×23`: card right edge 927, search left edge 1104 — 177 px of clearance. `340 + 282 = 622` fits in 1400 and does not fit in 430. The overlap is a *width* consequence, and it is unconditional below ≈ 640 px.

### 1.3 The card is sized for a desktop popup and clips on a phone

```
.maplibregl-popup        width 340px   max-width 340px      (fixed; MapLibre default skin)
.maplibregl-popup-content  max-height var(--gridatlas-card-max, 60vh)   (sld-sandbox:3746)
```

Measured at 390 × 664 on a fresh load: the card's left edge is at **x = −89**. It is anchored to the project marker (`maplibregl-popup-anchor-right`), and at 390 px there is not enough room to the left of a centred marker for a 340 px box. **89 px — 26 % of every line of card text — is off the left edge of the screen and cannot be scrolled to.**

The vertical dimension has the mirror problem. `--gridatlas-card-max` is derived from the map rect, not from the space below the anchor:

| Viewport | map height | card `max-height` | card top | card bottom | clipped |
|---|---|---|---|---|---|
| 390 × 664 | 664 | 604 px | 116 | 737 | **73 px** |
| 402 × 874 | 874 | 814 px | 116 | 947 | **73 px** |

The internal scroller believes it has 620 px of visible height; 73 px of that is below the screen edge. The last 73 px of card content is unreachable at *any* scroll position.

**This is the sequencing fact that matters for the plan:** the card's height is derived from the map's height. Making the map full-bleed makes the card *taller* (621 px against a 664 map, versus ~330 px against a 458 map) and therefore makes the overlap *worse*. De-overlap must ship before full-bleed, not after.

### 1.4 Where the answer sits

The card's scrollable content is **1,810 px tall** in a 620 px window — 2.9 screens.

Content order as rendered, with the y at which each line lands on a 390 × 664 phone:

| y | Content |
|---|---|
| 140 | Project name (in the card bar) |
| **188** | **Project name again** — rendered twice, ≈ 48 px spent on a duplicate |
| 230 | `solar` |
| 250 | `840 MW` |
| 272 | Address · postcode · county |
| 293 | `REPD 12588 · application submitted` |
| 334–512 | Substation intelligence: Cowley Substation, site-wide published envelope, 6 circuits / 10 transformer winding connections, the Appendix D note — **≈ 270 px of secondary detail** |
| **601** | **`Nearest 400 kV substation`** |
| **602** | **`Cowley Substation · 15.76 km straight · 19.6 km corridor estimate`** |
| 642 | `Indicative highway-corridor screening only. Not a connection offer…` |
| **745** | The scope sentence — `nearest of the 278 mapped substations at 400 kV or above that this search could see…` |
| 827+ | ETYS topology, the name join, declared voltages |

**The headline measurement lands at y = 601 on a 664 px screen — 90 % of the way down.** The scope sentence that makes the superlative honest lands at **y = 745, which is 81 px below the bottom of the screen and inside the 73 px unreachable band.**

Desktop, same content, 1400 × 900: the measurement lands at **y = 327 — 36 % down**. The product is not badly ordered for a desktop reader. It is badly ordered for a phone, and only for a phone.

### 1.5 Touch targets

Measured in a fine-pointer frame, so the `@media (pointer:coarse)` rules in `sld-sandbox:3782` did not apply. Splitting honestly:

**Already ≥ 44 px unconditionally (verified in the frame):**
`#gridatlas-mobile-tray` chips — Tools 68×44, ⚡ Grid 71×44, ◉ Subs 65×44, ◎ Scope 71×44, ✕ Clear 71×44 (tray CSS, `sld-sandbox:5507`); card bar − and × 44×44 (`sld-sandbox:3760`); `#gridatlas-dash-toggle` 44 min (`sld-sandbox:2783`).

**Covered by a `pointer:coarse` rule, so presumed 44 px on a real phone — unverified here:**
`.search-input`, `.search-btn` (GO), `.map-ctrl-btn`, SLD panel controls. *(Note: the architect's screenshot `851f6587` appears to show the search field at ≈ 34 CSS px, not 44. My display-pixel estimate carries ±10 %, so this is a flag to check on device, not a claim.)*

**Under 44 px and covered by no rule at all — these are the real defects:**

| Control | Measured | Owner |
|---|---|---|
| `#btn-fullscreen` (⛶, enter) | **28 × 22** | shell `ventusv8.css:115` |
| `#btn-fullscreen-exit` (✕ Exit) | **65 × 25** | shell `ventusv8.css:116` |
| `#fs-curtain-tab` (⬇ LAYERS) | **84 × 22** | shell `ventusv8.css:126` |
| `.maplibregl-popup-close-button` | **20 × 18** | MapLibre default skin |
| `GB prices · historic ▸` | **362 × 30** | `sld-sandbox:5644` |
| `Versions · v9.89 ▸` | **362 × 30** | `sld-sandbox:5254` |
| `Explore route corridors ›` | **304 × 44**, but two sibling actions below it are **304 × 31** | `sld-sandbox:2396`, card body |
| `.key-item` topology rows | ≈ **30** high, ≈ 22 px checkbox (derived from screenshot) | shell `ventusv8.css:20` |

Eight controls. All fixable with one injected CSS block in one file.

### 1.6 What the phone downloads before it can answer

Measured with `PerformanceResourceTiming` on a cold-ish arrival at the Botley West deep link:

| Resource | Host | Decoded bytes | Fetch starts |
|---|---|---|---|
| `maplibre-gl.js` | cdn.jsdelivr.net | 762,783 | 367 ms |
| `202609031316-sld-sandbox-v9-8.js` | ventusltd.github.io | 362,061 | 317 ms |
| `202609031316-substation-intelligence-v9-63.js` | ventusltd.github.io | 238,945 | 269 ms |
| `current.json` | ventusltd.github.io | 46,315 | 73 ms |
| **`grid_substations.geojson`** | ventusltd.github.io | **1,193,190** | 445 ms |
| **`connection-points.v3.json`** | **raw.githubusercontent.com** | **2,896,561** *(pin-declared; cross-origin, so opaque to timing)* | **391 ms — on the arrival path** |
| `gb-transmission-network.v1.json` | raw.githubusercontent.com | 10,069,966 *(pin-declared)* | **not fetched at arrival** |

**Correction to the concurrent audit's framing, in the audit's favour but with a different number.** The ~12.7 MB figure is right as a *session* total (2,896,561 + 10,069,966 + 6,873 = 12,973,400 bytes, `atlas/modules/202609030137-pinned-products.js`). But the 10.07 MB ETYS network is **already lazy** — ledger v9.68 records "the 10 MB ETYS node/branch product is fetched on first click, never at load", and the resource timing confirms it is absent from the arrival. The honest cold-arrival figure is:

> **≈ 4.09 MiB of application data** (`grid_substations.geojson` 1.14 MiB + `connection-points.v3.json` 2.76 MiB), plus **≈ 1.35 MiB of code**, downloaded before the reader can be told that Cowley is 15.76 km away.

The architect's constraint is nonetheless violated exactly as stated. The phone downloads all 886 published connection points, and 5,800-odd mapped substations, in order to re-derive on the handset a single nearest-substation answer that an engine could compute once and publish as one row. `connection-points.v3.json` is on the critical path from 391 ms; it is the arrival's long pole and the first thing to move.

### 1.7 Two states nobody has designed, and the layout must not assume away

**Out of drawing range.** `sld-sandbox:2135` — `const MAX_LINK_KM = 40; // beyond this, silence is more honest`, enforced at `:3637` and `:3672`. Berwick Bank's nearest 400 kV is 78.96 km and Hornsea 3's is 103.79 km, so both draw **zero** links while the card still prints a distance. The reader sees a pin on empty sea and a number with nothing connecting it to anything. The constant is a deliberate honesty choice and should stay; what is missing is a **sentence and a visual state** that says *further than we draw*, so that "honest silence" does not read as "broken".

**No technology layer.** `wind_onshore`, `wind_offshore` and `other` light no layer at all — 32.7 % of the spine. A layout that reserves space for a technology layer, or a legend that implies one is always on, will be empty for a third of arrivals. This reinforces the v9.89 rule rather than conflicting with it: the measurement path is technology-agnostic and **the layout path must be too**.

### 1.8 Desktop baseline, to be held as the no-regression line

Measured at 1400 × 900, deep link, `pointer: fine`:

| | |
|---|---|
| `.hud-header` | `4,4 1392×68` |
| `#map-container` | `4,76 1392×701` — **78 % of height, 99 % of width** |
| `.scada-wrapper` | `4,780 1392×116` |
| `.map-controls` | `15,510 165×236` (the six shell tool buttons, bottom-anchored) |
| `.search-bar-wrapper` | `1104,148 282×23` — no intersection with the card |
| card | `587,-145 340×666` — *note: the top 145 px is above the viewport; a pre-existing desktop clip, out of scope here* |
| measurement lands at | **y = 327 (36 % down)** |
| mobile tray | not installed |

Any increment below must leave these numbers within ±5 %, except where it deliberately improves them.

---

## 2. What "like Uber" licenses here, and what it does not

### 2.1 Adopted in full — the interaction pattern

The map is the surface. One sheet with detents. The answer before the detail. Thumb-zone controls. One primary action visible at a time. Nothing overlaps anything. All of that is right for this product and the measurements above show how far from it the current build sits.

### 2.2 Explicitly not adopted — the routing model and the data architecture

Uber solves a one-dimensional problem on a single traversable network: roads. Energy is multi-modal and volumetric. A cable route crosses road, rail, buildings, overhead line, underground duct, watercourse, bridge, foreshore, seabed, grassland, forest, mountain pass, factory floor and tunnel, and the cost, consentability and risk of each crossing differ. **A UI that renders a route as one line with one length is not a simplification of that; it is a different claim.**

The current corridor estimate is exactly a one-line claim: `sld-sandbox:2333` `corridorBeside()` prints `~19.6 km corridor estimate (×1.245, …)` — a scalar multiplier on a straight line, calibrated against GB transmission cable circuits. It is honest about being an estimate, and it should stay. But the **presentation contract** must be shaped so that the day the engines can return a sequence of segments, the sheet renders it without a redesign.

Design consequence, carried into §3.8: the route block is a **segment ledger**, not a number. Today it renders one row (`straight line`, then one `corridor estimate` row). Tomorrow it renders N rows, each with a medium, a length and its own character. The layout, the detent heights and the scroll behaviour must already accommodate N.

### 2.3 The hard constraint — engines compute, the phone receives an answer

§1.6 measures the violation. The peek detent is the forcing function: a peek that must show *nearest substation, distance, voltage* **immediately, without interaction** cannot be waiting on a 2.76 MiB cross-origin fetch and a client-side nearest search over 5,800 geometries. Either the answer is precomputed and delivered as a row, or the peek is a spinner and the whole pattern fails.

So **P4 (the sheet) is not independent of D1 (the answer product)**. P4 can ship against today's client-side compute and will look right on a warm cache and a good connection; it will show a loading peek on a cold phone. That is stated as a known limitation of P4, and D1 is what removes it.

### 2.4 My dissent, such as it is

"Like Uber" is the right pattern here, with two amendments, and I would not ship it without them:

**Amendment 1 — the peek cannot be a bare number.** Uber's peek is `4 min · £12.40`. A bare peek here would print `Cowley Substation · 15.76 km` and break the honesty rules, which require that a superlative name the sample it searched and that a straight line say it is not a route. The peek must therefore be denser than Uber's: **a measurement plus its qualifier, in the same detent**. That is a real constraint on the peek's height (I budget 168 px, not the ~110 px an Uber peek uses) and it is non-negotiable.

**Amendment 2 — the half detent must not hide what the measurement names.** Uber can cover 60 % of the map because the map is context. Here the map carries the substation the sentence names, the link line to it and the project ring. A 55 dvh half detent hides them. So: **half is ≤ 50 dvh**, and opening to half must pan the map so that the project ring and the named substation are both inside the visible band above the sheet. Without that, the sheet is a card with a nicer gesture.

With those two amendments I believe the pattern is correct and I would build it.

---

## 3. The target design

### 3.1 Layout law (phone: `pointer: coarse` or `innerWidth ≤ 700`)

1. The map is `position:fixed; inset:0; width:100vw; height:100dvh`. It is the page, not a box on it. No border, no radius, no inset.
2. Exactly **three** persistent layers above it, and no others: the **top rail** (48 px, safe-area aware), the **sheet**, and the **thumb bar** docked to the sheet's top edge.
3. Nothing else is `position:fixed` or `absolute` over the map. Every panel that exists today becomes either sheet content or a sheet of its own.
4. Anything that opens over the sheet is itself a sheet, at a higher detent. Sheets stack; nothing floats.
5. `html, body { overflow: hidden }` stays. All scrolling is inside a sheet, with `overscroll-behavior: contain`.
6. Every interactive target ≥ 44 × 44 CSS px, spacing ≥ 8 px.
7. No layout branch reads `technology`. Ever. (v9.89.)

### 3.2 The three zones

```
┌──────────────────────────────┐  0
│  top rail  48px              │   ← ✕ Exit / brand mark / ⌕ search chip / ☰ layers chip
├──────────────────────────────┤  48
│                              │
│         THE MAP              │   ← project ring, link lines, substations
│      (full bleed, 100dvh)    │
│                              │
├──────────────────────────────┤  100dvh − 56 − peek
│  thumb bar 56px              │   ← ONE primary action + overflow chip
├──────────────────────────────┤
│  SHEET — peek 168px          │   ← the answer
└──────────────────────────────┘  100dvh − safe-area-inset-bottom
```

The thumb bar rides on top of the sheet and moves with it, so the primary action stays in the lower third at every detent.

### 3.3 The sheet and its detents

One element, `#gridatlas-sheet`. Three detents, snapped by a drag on the grab handle or on the sheet's own header:

| Detent | Height | Contains |
|---|---|---|
| **peek** | `168px + env(safe-area-inset-bottom)` | Project name (once). Capacity. **The headline measurement: nearest substation, distance, voltage — plus its qualifier.** |
| **half** | `min(50dvh, 420px)` | The measurement block in full: the link rows, the straight-line statement, the corridor/segment ledger, the scope sentence, the denominator. |
| **full** | `92dvh` | Substation intelligence, published envelope, ETYS topology, planned changes, versions. |

Rules:

- **The default detent on a deep-link arrival is `peek`.** The reader gets the answer without a gesture. This is the whole point of the exercise.
- The project name renders **once**. The duplicate at y=188 (§1.4) is deleted.
- The ≈270 px of substation intelligence currently sitting *above* the measurement (y 334–512) moves to `full`. Nothing between the project identity and the measurement.
- The sheet is `z-index: 400`. The map is 500 today; the map becomes 100 and the sheet 400, so the ordering is stated once and no control needs a z-index of its own again.
- Dragging the sheet down past `peek` does **not** close it and does **not** clear the ring. There is no state in which the reader has a project selected and no answer visible.
- `content-visibility: auto` on the `full` block so its 1,300 px of content costs nothing until reached.

### 3.4 The honesty rules, restated as a per-detent contract

These are testable and belong in the gate, not in a reviewer's head.

| Rule | Where it must appear |
|---|---|
| A superlative names the sample it searched | The **peek** carries a short form (`nearest of 278 mapped ≥400 kV`); `half` carries the full `nearestScope()` sentence with the coverage denominator. **Never a peek without the short form.** |
| Nearest is nearest-among-those-with-coordinates, and says so | `half`, full sentence, computed at render from `__GRIDATLAS_NETWORK__.coverage()` as it is today. Not a literal. |
| A straight line is not a route, and states how far off it is | The word **straight** appears in the peek, adjacent to the number. The corridor/segment estimate and its calibration are in `half`. |
| The straight-line feature stays | It is the peek's headline. It is not replaced by the corridor figure; the corridor figure sits beside it. |
| No grading verdicts | No STRONG / GOOD / REMOTE / colour-coded distance anywhere, in any detent. A distance is a distance. |
| Scope never implies capacity | The scope block and any capacity figure are never in the same visual group, and no arrow, colour or adjacency suggests one follows from the other. |
| Out of drawing range is an answer, not an error | See §3.9. |

**Gate-able form:** *no detent may render a superlative without, in the same detent, both the sample it searched and the word "straight".*

### 3.5 Thumb bar — one primary action

TOOLS / GRID / SUBS / SCOPE / CLEAR stop being a permanent five-across row.

- The bar shows **one** primary action, contextual to state: on arrival it is `Nearest substations`; with a substation selected it is `Explore route corridors`; on blank map it is `What grid is here`.
- A single `⋯` chip opens a **tools sheet** carrying the rest (Grid, Subs, Scope, Clear, Export CSV, Radius, Poly Zone, Measure, Grid At Point, GB prices, Versions).
- Bar height 56 px; targets 44 px; bottom edge respects `env(safe-area-inset-bottom)`.
- `GB PRICES · HISTORIC` and `VERSIONS · v9.89` leave the map entirely and become rows in the tools sheet. They are reference material, not map controls.

### 3.6 Layers are a sheet

`.scada-wrapper` — legend, `TOPOLOGY (GEOJSON)`, `PIPELINE NEWS (REPD)`, the disclaimer — is not a permanent band. It becomes a **layers sheet** opened from a `☰` chip in the top rail.

- Rows are 44 px with a 44 px hit area; the checkbox may stay 22 px visually.
- One column below 480 px (already true: `ventusv8.css:130`).
- The disclaimer paragraph moves to the bottom of that sheet.
- The remembered collapsed/expanded state in `localStorage['gridatlas.dash.collapsed']` becomes a remembered *sheet-closed* state. Default on a phone: **closed**.
- Precedent exists in the codebase: `keepLayersInFullscreen()` (`sld-sandbox:7362`) already relocates `.dashboard` into the fullscreen element. This increment generalises that move rather than inventing it.

### 3.7 Search collapses to one control

- Top rail carries a **44 × 44 `⌕` chip**. No always-on 282 px field.
- Tapping it opens a **search sheet**: full-width field, results as 44 px rows, map dimmed behind.
- Selecting a result closes the sheet.
- A deep-link arrival still sets the field's value (that is visible confirmation of what resolved and part of the contract) — but the sheet is **closed** and the results list is **dismissed**. The value is there when the reader opens the chip.

### 3.8 The route is a segment ledger

Per §2.2. The `half` detent's route block is a list, not a line:

```
STRAIGHT LINE          15.76 km      to Cowley Substation
CORRIDOR ESTIMATE     ~19.6 km       ×1.245 · indicative highway screening
                                     not a route, not an offer, not a length
```

rendered from an array. Today the array has one estimate row. The renderer must not special-case `length === 1`, must not put the number in the heading, and must leave room for a `medium` column (`road`, `rail`, `underground`, `overhead`, `watercourse`, `foreshore`, `seabed`, `tunnel`, `building`) and a per-segment note. When an engine can return segments, the sheet renders them with no layout change.

### 3.9 The out-of-range state

When the nearest mapped substation is beyond `MAX_LINK_KM` (40 km):

- The peek still gives the measurement. The distance is real; only the *drawing* is withheld.
- The peek adds one line: **`Further than this map draws links (40 km).`** — a statement, not a warning colour, not an error.
- The map shows the project ring and, at a zoom that contains both, a marker at the named substation with no link line. The reader is never given a pin on empty sea with no explanation.
- `half` carries the existing sentence from `sld-sandbox:3886`.

This is presentation only. `MAX_LINK_KM` does not move; the compute path is untouched.

### 3.10 Desktop — the same components, re-laid-out

At `min-width: 701px` **and** `pointer: fine`:

- `#gridatlas-sheet` becomes a side panel: `position:absolute; right:16px; top:64px; width:380px; max-height:calc(100dvh - 96px)`. Same DOM, same content order, same honesty contract. Detents collapse to one: the panel is always at what the phone calls `full`, scrolled.
- The thumb bar reverts to the existing vertical `.map-controls` stack, bottom-left.
- The search bar reverts to the persistent top-right field.
- The layers sheet reverts to `.scada-wrapper` below the map.
- The header stays.

The content-order improvement (measurement before intelligence) applies to **both**. Desktop's measurement moves from y=327 to roughly y=190. That is an improvement, not a regression, and the gate should record it.

---

## 4. Constraints that outrank the design

Any increment that breaks one of these is a regression however good it looks.

1. **The deep-link contract.** Arrival by `repd_ref`; the null-island and REPD false-origin guard (`place-global-search:208–213`, `sld-sandbox:6001`); `zoom` honoured only when finite and 3–18 (`sld-sandbox:5967`); the project ring drawn on arrival (`sld-sandbox:4794`, placed at `:6154`); `link.arrival_fullscreen` set on touch arrival (`sld-sandbox:6011`). The verifier `pipelinenews/tools/intelligence/202609030132-verify-wider-fleet-deep-link.mjs` reads **composed bytes** and checks **values** — notably the `allowedTechnologies` allow-set — so a change to composed source can move it even when no behaviour changes.
2. **The honesty rules**, as restated per detent in §3.4. The straight-line feature stays.
3. **Technology-agnostic measurement, and now technology-agnostic layout.** v9.89 (`9593f0a`) removed the one branch that gated the measurement on technology. No increment reintroduces a technology branch, including for layout, including for "which layer to reserve space for". §1.7 is why: a third of arrivals have no layer.
4. **Generations are immutable.** Every increment is a new cartridge generation with a new SHA-256 in `current.json`, a new version-ledger row, and a stamped commit. Nothing is edited in place. The shell `releases/202608300453-atlas-v9/` is not touched by any increment below — every CSS change is injected by a cartridge, as `installStyles()` already does.
5. **No page scroll.** `html, body { overflow: hidden }` and `.dashboard { height: 100dvh }` are load-bearing: content that overflows is unreachable, not scrollable. Any increment that adds height must add it inside a sheet.

---

## 5. The staged plan

Two tracks. **P** is presentation and routes to one cartridge. **D** is the data plane and needs an architect decision before anyone writes code.

Ordering principle: cheapest removal of the most visible defect first; nothing that makes a later increment harder; the sheet architecture last among the layout work because it depends on the space the earlier ones free.

### 5.1 The order, at a glance

| # | Increment | Owning file | Cost | Risk | Needs a decision? |
|---|---|---|---|---|---|
| **P1** | The arrival dismisses its own search results | `atlas/cartridges/{gen}-place-global-search-v9-5.js` | ~5 lines | very low | no |
| **P2** | The eight uncovered controls reach 44 px | `atlas/cartridges/{gen}-sld-sandbox-v9-8.js` (`installStyles`) | ~20 lines CSS | very low | no |
| **P3** | Search collapses to one 44 px chip on a phone | `atlas/cartridges/{gen}-place-global-search-v9-5.js` | ~60 lines | low | no |
| **P4** | Full-bleed map is the default on a phone, not a mode | `atlas/cartridges/{gen}-sld-sandbox-v9-8.js` (`trayTarget` / boot) | ~25 lines | medium | **yes — §5.4** |
| **P5** | The card becomes one sheet with three detents, measurement first | `atlas/cartridges/{gen}-sld-sandbox-v9-8.js` (card region) | large | medium-high | no, but see D1 |
| **P6** | Thumb bar: one primary action, the rest in a tools sheet | `atlas/cartridges/{gen}-sld-sandbox-v9-8.js` (`installMobileTray`) | medium | low | no |
| **P7** | Layers become a sheet | `atlas/cartridges/{gen}-sld-sandbox-v9-8.js` (`dashCollapse`) | medium | low | no |
| **P8** | Out-of-range is a first-class answer | `atlas/cartridges/{gen}-sld-sandbox-v9-8.js` (card body) | small | low | no |
| **P9** | The route becomes a segment ledger | `atlas/modules/{gen}-corridor-estimate.js` | medium | low | **yes — §5.4** |
| **P10** | Desktop re-lay-out: the sheet is a side panel | `atlas/cartridges/{gen}-sld-sandbox-v9-8.js` (sheet CSS) | small | low | no |
| **D1** | A measured-answer product: the engine computes, the phone reads one row | new derived product + `atlas/modules/{gen}-pinned-products.js` | large | high | **yes — §5.4** |
| **D2** | `connection-points.v3.json` leaves the arrival path | `atlas/cartridges/{gen}-substation-intelligence-v9-63.js` | medium | high | **yes — §5.4** |
| **D3** | Segments come from an engine, not a multiplier | `grid-distance-maths` + a new product | large | high | **yes — §5.4** |

**On the architect's expectation** — *"killing the overlap and giving the map its full height are worth more to a reader than the sheet architecture, and are far cheaper."*

**Confirmed, with one correction to the ordering.** The overlap fix is even cheaper than expected (P1 is five lines and removes the largest of the three overlaps outright), and full height is nearly free (P4 flips a mode that already exists). But **full height must come after de-overlap, not with it**: the card's `max-height` is derived from the map rect (§1.3), so a full-bleed map produces a 621 px card instead of a ~330 px one, and the overlap gets worse before it gets better. P1–P3, then P4.

**A second, useful consequence.** `.map-controls` is *already* bottom-anchored (`bottom:30px`). It reads as "floating in the vertical middle" only because the map box ends at 57 % of the screen. P4 alone moves the control row from **57 % to 77 %** of the viewport — into the thumb zone — with no control-positioning work at all. The thumb-zone requirement is largely satisfied by full-bleed; P6 is then about *reducing five actions to one*, not about moving them.

### 5.2 Increment detail

---

**P1 — the arrival dismisses its own search results**

*Owning file:* `atlas/cartridges/{gen}-place-global-search-v9-5.js` (cartridge id `uk-gazetteer-flyto`).
*What changes:* in `receiveExactRepdDeepLink()` (currently L496–539), after `selectResult(exact)` at L512, hide `#search-results` (`display:none`, clear its children) and blur `#search-input`. `input.value = repdRef` at L517 **stays** — it is the reader's confirmation of what resolved.
*What a reader sees:* on arrival, the project card is no longer covered by a list of search results. The single most visible defect in both architect screenshots is gone. Nothing else moves.
*Gate:* extend the deep-link verifier family with a browser check at 390 × 664 asserting (a) `#search-results` has no layout box after arrival settles, (b) `#search-input.value === repd_ref`, (c) the intersection area of `#search-results` and `.maplibregl-popup` is 0. Plus a static check that `selectResult` is followed by a dismiss in the composed bytes.
*Must not break:* exact-REPD-first resolution; `state.deep_link` publication at L516–531; the `capture:true` + `stopImmediatePropagation()` binding that keeps the engine's legacy search from running; the field's value.

---

**P2 — the eight uncovered controls reach 44 px**

*Owning file:* `atlas/cartridges/{gen}-sld-sandbox-v9-8.js`, `installStyles()` (currently L3711–3788), extending the existing `@media (pointer:coarse)` block at L3782.
*What changes:* `min-height:44px` (and `min-width` where relevant) for `#btn-fullscreen`, `#btn-fullscreen-exit`, `#fs-curtain-tab`, `.maplibregl-popup-close-button`, `#gridatlas-gb-conditions > button`, `#gridatlas-version-ledger > button`, `.key-item`, and the two 31 px card actions. Injected CSS only — the immutable shell is not edited.
*What a reader sees:* every control on the phone can be hit with a thumb. Exit, Layers, the card's close button and the two reference bars stop being misses.
*Gate:* a browser sweep at 390 × 664 asserting every element matching `button, a, input, [role=button], label.key-item, summary` with a layout box has `height ≥ 44 && width ≥ 44`. Zero exceptions list.
*Must not break:* desktop — the whole block is inside `@media (pointer:coarse)`, so `pointer:fine` is untouched. Verify the `.map-controls` column still fits: at 390 px it grows from 123 px to roughly 190 px, which P4 then absorbs.

---

**P3 — search collapses to one 44 px chip on a phone**

*Owning file:* `atlas/cartridges/{gen}-place-global-search-v9-5.js`.
*What changes:* under `pointer:coarse || innerWidth ≤ 700`, the cartridge injects its own CSS and wraps `.search-bar-wrapper` in a collapsed state: a 44 × 44 `⌕` chip in the top rail; tapping expands to a full-width overlay with the field and results as 44 px rows; selection or dismiss collapses it. Desktop keeps the persistent field.
*What a reader sees:* the top of the map is a clean rail. No 282 px field over the card. Search is one tap away and takes the whole width when it is open, which is when it is actually usable.
*Gate:* at 390 × 664, `.search-bar-wrapper`'s collapsed box is ≥ 44 × 44 and its intersection with `.maplibregl-popup` is 0. At 1400 × 900 the field is present and its box is unchanged from the §1.8 baseline.
*Must not break:* the deep-link value assignment; the capture binding; `LOCATION_ONLY` result-class behaviour.

---

**P4 — full-bleed map is the default on a phone, not a mode**

*Owning file:* `atlas/cartridges/{gen}-sld-sandbox-v9-8.js`, near `trayTarget()` (L5485) and the arrival block (L6011).
*What changes:* when `trayTarget()` is true, apply the fullscreen **layout** at boot — `body.fs-active` + `#map-container.is-fullscreen` — without calling `requestFullscreen()`. The `✕ Exit` affordance is retained and reverts to the boxed layout. The deep-link arrival path continues to call `window.enterFullscreen?.()` and set `link.arrival_fullscreen = true` exactly as today.
*What a reader sees:* the map goes from 44 % of the screen to 100 % on a plain arrival, not only on a deep link. Header, legend and topology list stop consuming 56 % of the phone. The control row moves from 57 % to 77 % of the viewport — into the thumb zone.
*Gate:* at 390 × 664 with no deep link, `#map-container` height ≥ 0.95 × `innerHeight`; `.map-controls` top ≥ 0.66 × `innerHeight`. At 1400 × 900 the §1.8 boxed layout is unchanged. Plus the existing deep-link verifier, unchanged and still green.
*Must not break:* `link.arrival_fullscreen` on deep-link arrival; the `map.resize()` at L6013; `keepLayersInFullscreen()`'s relocation of `.dashboard`; the v9.80 lesson that collapsing `.dashboard` blanks the map — this increment must target the *layout classes*, never `.dashboard`'s display.
**Needs an architect decision — see §5.4 (a).**

---

**P5 — the card becomes one sheet with three detents, and the measurement leads**

*Owning file:* `atlas/cartridges/{gen}-sld-sandbox-v9-8.js` — `addCardBar()` (L4038), `boundCardToMap()` (L3990), `installStyles()` (L3711), and the card body's render order.
*What changes:* the MapLibre popup stops being the container. A single `#gridatlas-sheet` (`position:fixed; left:0; right:0; bottom:0; z-index:400`) with the three detents of §3.3, dragged by the existing pointer-drag code generalised from `addCardBar`. Content is reordered: identity, then measurement, then everything else. The duplicate project title is removed. The `full` block gets `content-visibility:auto`. The existing `#gridatlas-corridor-sheet` (L2407, already `position:fixed; bottom:0; z-index:10000; max-height:min(70vh,560px)`) is the idiom to generalise — this is not a new component type.
*What a reader sees:* on arrival, without touching anything, the bottom of the screen says the project's name, its capacity, and *Cowley Substation · 15.76 km straight · nearest of 278 mapped ≥400 kV*. One drag gives the full measurement block. A second gives the intelligence. The card is never clipped off the left edge and never has 73 px of unreachable content.
*Gate:* at 390 × 664, deep-link arrival, after settle: (a) the measurement heading and its value both have `getBoundingClientRect().bottom ≤ innerHeight`; (b) the peek's own box contains both; (c) the peek's text contains the word `straight` **and** a sample phrase; (d) `#gridatlas-sheet` left ≥ 0 and right ≤ innerWidth; (e) `scrollHeight` of the peek ≤ its `clientHeight` (nothing hidden in the peek); (f) no element with `position:fixed|absolute` other than the top rail and thumb bar intersects the sheet.
*Must not break:* every honesty rule in §3.4; no `technology` read in the layout path; the straight-line row; the project ring persists when the sheet is dragged to peek; `boundCardToMap`'s clamping lesson (keep ≥ 44 px of the grab handle reachable); the card-keeper that re-attaches the measurement when a late popup replaces the decorated one (ledger v9.46).
*Known limitation:* on a cold phone the peek will show a loading state until `connection-points.v3.json` lands. **D1 is what removes it.**

---

**P6 — thumb bar: one primary action, the rest in a tools sheet**

*Owning file:* `atlas/cartridges/{gen}-sld-sandbox-v9-8.js`, `installMobileTray()` (L5496–5635), plus `installGbConditions()` (L5637) and `installVersionLedger()` (L5247) which move their entry points into the tools sheet.
*What changes:* the five-across tray becomes a 56 px bar with one contextual primary action and a `⋯` chip. Grid, Subs, Scope, Clear, the six shell tool buttons, `Grid At Point`, GB prices and Versions become rows in a tools sheet.
*What a reader sees:* one obvious thing to do, at the bottom of the screen, where a thumb is. Nine controls stop competing.
*Gate:* at 390 × 664, exactly one control in the thumb bar has the primary style; every thumb-bar target ≥ 44 px; `.map-controls` no longer intersects `#gridatlas-sheet`.
*Must not break:* the Subs control being found by attribute rather than label text (ledger v9.60); every action reachable in at most two taps; desktop's vertical `.map-controls` stack.

---

**P7 — layers become a sheet**

*Owning file:* `atlas/cartridges/{gen}-sld-sandbox-v9-8.js`, `dashCollapse()` (L2758–2839) becomes `installLayersSheet()`.
*What changes:* on `trayTarget()`, `.scada-wrapper` is relocated into a sheet opened by a `☰` chip in the top rail; default closed. Rows get 44 px hit areas. `localStorage['gridatlas.dash.collapsed']` becomes the sheet's remembered state.
*What a reader sees:* the topology list stops consuming a screenful below the fold. Layers are one tap, and the list is full-width and thumb-sized when it is open.
*Gate:* at 390 × 664, `.scada-wrapper` has no layout box until the chip is tapped; after tapping, every `.key-item` hit area ≥ 44 px. At 1400 × 900 `.scada-wrapper` is below the map exactly as in §1.8.
*Must not break:* **the v9.80 lesson** — the collapse targets `.scada-wrapper`, never `.dashboard`, or the map blanks and the remembered state blanks it again on reload. The engine renders checkbox DOM into `#scada-ui-container` (`substation-intelligence:1021`) and mirrors it into `#fs-curtain-keys`; both targets must still exist after relocation.

---

**P8 — out of drawing range is a first-class answer**

*Owning file:* `atlas/cartridges/{gen}-sld-sandbox-v9-8.js`, card body near `caveatHtml()` (L3798) and the `MAX_LINK_KM` messages (L3886).
*What changes:* when the nearest mapped substation exceeds `MAX_LINK_KM`, the peek adds the line `Further than this map draws links (40 km).` and the map frames both the ring and a marker at the named substation. Presentation only; `MAX_LINK_KM = 40` (L2135) is untouched.
*What a reader sees:* Berwick Bank (78.96 km) and Hornsea 3 (103.79 km) stop looking broken. The reader is told the distance *and* told why nothing is drawn.
*Gate:* an offshore deep link at 390 × 664 renders a peek whose text contains both the distance and the range statement, and the map contains the project ring and a substation marker. No error styling, no warning colour.
*Must not break:* the honesty of the silence — the absence of a link line is the correct behaviour and must stay; no verdict language.

---

**P9 — the route becomes a segment ledger**

*Owning file:* `atlas/modules/{gen}-corridor-estimate.js` (compiled into `substation-intelligence`), with the renderer in `sld-sandbox` `corridorBeside()` (L2333).
*What changes:* the corridor estimate's return shape becomes an **array of segments** — today an array of one, carrying `{ medium: 'indicative', km, factor, calibration }`. The renderer iterates and never special-cases length 1. A `medium` column and a per-segment note are laid out but empty for the single-segment case.
*What a reader sees:* nothing yet. The same estimate, the same calibration sentence, in a row layout that can grow.
*Gate:* value-for-value parity against the current single-estimate output; a fixture with three synthetic segments renders three rows at 390 px without overflow, clipping or a layout change.
*Must not break:* the calibration figures and the "not a route, not an offer, not a length" sentence.
**Needs an architect decision — see §5.4 (b).**

---

**P10 — desktop re-lay-out: the sheet is a side panel**

*Owning file:* `atlas/cartridges/{gen}-sld-sandbox-v9-8.js`, the sheet's CSS block.
*What changes:* `@media (min-width:701px) and (pointer:fine)` turns `#gridatlas-sheet` into a right-hand panel; the thumb bar reverts to `.map-controls`; the layers sheet reverts to `.scada-wrapper`; the search chip reverts to the field.
*What a desktop reader sees:* the layout of §1.8, with the measurement higher up the panel (≈ y 190 instead of y 327) because the content order improved for everyone.
*Gate:* at 1400 × 900 every box in the §1.8 table is within ±5 %, and the measurement's y is lower than 327.
*Must not break:* the §1.8 baseline. Desktop is second, not sacrificed.

---

### 5.3 The data-plane track

**D1 — a measured-answer product**

*What changes:* an engine computes, per REPD reference, the nearest-substation answer and publishes it as a derived product: substation name, straight-line km, corridor estimate, voltage class, the sample count the superlative was drawn from, the coverage denominator, and the out-of-range flag. Pinned by commit and SHA-256 in `atlas/modules/{gen}-pinned-products.js`, alongside the three existing pins.
*Owning files:* a new derived product in the data estate (`data-grid-gb` or `data-gridatlas`), plus one pin entry.
*What a reader sees:* the peek is populated on first paint instead of after a 2.76 MiB cross-origin fetch and a client-side nearest search over 5,800 geometries.
*Why it is the constraint, not an optimisation:* §2.3. The peek's promise — *the answer, immediately, without interaction* — is not deliverable on a cold phone without it.
*Gate:* the peek renders its measurement with `connection-points.v3.json` blocked at the network layer.
**Needs an architect decision — see §5.4 (c).**

**D2 — `connection-points.v3.json` leaves the arrival path**

Once D1 exists, `substation-intelligence`'s arrival fetch (starting at 391 ms, §1.6) becomes a lazy fallback for the case where the answer product has no row. Cold-arrival application data drops from ≈ 4.09 MiB to ≈ 1.14 MiB (`grid_substations.geojson` alone), and a further pass can tile or bbox-filter that.
*Gate:* resource timing on a cold arrival shows no `raw.githubusercontent.com` request before first paint of the peek.
**Needs an architect decision — see §5.4 (c).**

**D3 — segments come from an engine**

The multi-medium route of §2.2: a segment sequence computed where the hard-won data lives, delivered as the array P9's renderer already accepts. `grid-distance-maths` is the natural home for the geodesy; the medium classification needs a source decision.
**Needs an architect decision — see §5.4 (d).**

### 5.4 What needs the architect, and what exactly the question is

**(a) P4 — does "arrival enters fullscreen on touch" mean the Fullscreen API or the layout?**
The deep-link contract records *arrival entering fullscreen on touch*. `sld-sandbox:6011` calls `window.enterFullscreen?.()`, which both adds the layout classes **and** calls `requestFullscreen()` on `#map-container`. P4 makes the *layout* the default on a phone. If the contract means the API call, P4 is contract-touching and needs sign-off. If it means the layout, P4 is a default change and does not. My reading is that the reader-visible commitment is the layout, and that `requestFullscreen()` is the mechanism — but this is the architect's contract, not mine to interpret.

**(b) P9 — may the corridor estimate change its return shape?**
The module's output is consumed by the card renderer and its values are quoted verbatim in honesty text. Changing a scalar to an array of one is behaviour-preserving but is a module contract change, and modules are the estate's unit of ownership. Sign-off needed on the shape before it is cut.

**(c) D1 / D2 — a new pinned product and a change to what arrives.**
This is a data-plane version, not a cartridge edit. It creates a fourth runtime product; it moves a measurement that is currently derived on the handset into an engine, which means the *value the card prints* is thereafter produced somewhere else. Given the pinned-products module's own history — a schema-identical correction that halved Cowley's transformer count invisibly — moving a printed number to a new producer needs the same pin-and-digest discipline and an explicit decision about who owns the arithmetic. The architect owns that call.

**(d) D3 — where does medium classification come from?**
There is no source in the estate today for whether a corridor segment crosses rail, watercourse, foreshore or tunnel. That is a data acquisition decision with cost, not an implementation choice.

**Not needing a decision:** P1, P2, P3, P5, P6, P7, P8, P10 are all presentation, all route to one owning file, and all leave the compute path and the deep-link contract untouched.

### 5.5 Gates — one note on the harness

The existing verifier (`202609030132-verify-wider-fleet-deep-link.mjs`) is a **static source-reading** check: it reads composed bytes and compares values. Most of P1–P10's claims are **geometric** — box intersections, heights, positions at a stated viewport — and cannot be proved by reading source.

Proposed split, so the plan does not quietly assume a runner that does not exist:

- **Static gates** (Node, no network, same idiom as today): the `pointer:coarse` block names the eight selectors; no `technology` identifier appears within the sheet-layout function; the detent constants exist and are ordered; a dismiss follows `selectResult` on the deep-link path; the corridor estimate returns an array.
- **Geometry gates** need a browser at a real narrow viewport. The frame technique of §0.2 works today, driven from Chrome, and its output is a table of boxes that can be diffed against the §1.1/§1.8 baselines and committed to `gridatlas/reports/`. **Whether that becomes a CI job or stays an agent-run check at each cut is an open question** — the `resize_window` defect (§0.1) means the obvious approach is not available, and per the estate's own experience a runner that reports green where it cannot see is worse than no runner.

---

## 6. What I could not measure

1. **A real touch device.** No `pointer: coarse` anywhere in this session. Every `@media (pointer:coarse)` rule is unverified — including whether `.search-input`'s `min-height:44px` actually applies, which the architect's screenshot weakly suggests it may not (≈34 CSS px, ±10 % on my estimate).
2. **The populated topology list.** It never rendered in the frame (`.scada-keys` 5 px, 0 checkboxes). Row pitch and checkbox size are derived from screenshot `10a550cc` at ±10 %.
3. **Cold-cache byte counts for the cross-origin pins.** `raw.githubusercontent.com` sends no `Timing-Allow-Origin`, so `decodedBodySize` reads 0. The 2,896,561 and 10,069,966 figures are the **pin-declared** byte lengths from `atlas/modules/202609030137-pinned-products.js`, not observed transfer sizes. The *fact* that `connection-points.v3.json` is fetched at 391 ms on the arrival path **was** observed.
4. **Real-device timing.** No first-contentful-paint or time-to-peek numbers on a phone on a mobile network. The slowness the architect reports is consistent with §1.6 but I have not measured it on the device that is slow.
5. **The offshore cases end to end.** Berwick Bank's 78.96 km and Hornsea 3's 103.79 km are the concurrent audit's figures, carried here; I verified only that `MAX_LINK_KM = 40` exists at `sld-sandbox:2135` and gates link drawing at `:3637` and `:3672`, which is sufficient to establish the mechanism.
6. **Whether the deep-link failures the concurrent audit is diagnosing interact with any of this.** Deliberately not investigated — that audit owns it.
