# GridAtlas — skin architecture: one engine, many shells

Generated 202609031559. Measured against live GridAtlas **v9.89** (`9593f0a`), composition
**202609031316**, at `https://ventusltd.github.io/gridatlas/atlas/`, in the architect's own Chrome
(Chromium 152) on this laptop, 2026-09-03.

Nothing in the live Atlas was changed. The prototype is not deployed and is not part of any
composition.

**Status of this document.** It was cut short by an instruction to wrap up (three agents were
driving the same Chrome and corrupting each other's tabs). Everything below is marked
**MEASURED**, **BUILT AND VERIFIED**, **DESIGNED, NOT BUILT**, or **NOT ATTEMPTED**. Read those
labels literally.

---

## 0. How to open the prototype

```
cd sessions/202609031559-skin-architecture/prototype
python -m http.server 8731 --bind 127.0.0.1
```

then `http://127.0.0.1:8731/index.html`. It needs a server, not `file://`, because a skin is a
separate `.json` file fetched at runtime — which is the whole point, and `file://` blocks the fetch.

Try `?skin=glanceable`, `?skin=tenfoot`, `?skin=desktop`. The switcher, the layer registry, the
1000-layer virtualised list and the scenario sliders all work. It is a **prototype**, not a
candidate for the Atlas: the map is a canvas dot-plot, not MapLibre, and the substation set is a
geographic subset (428 rows) rather than the live 5,800.

```
prototype/
  index.html                     the host: switcher, stage, detection matrix, layer registry
  engine.js                      THE ENGINE. No CSS, no HTML, no skin id, no technology branch.
  skins/desktop.json             the unregressed baseline
  skins/glanceable.json          watch / car head unit / peek
  skins/tenfoot.json             TV, 10-foot, D-pad
  skins/broken-compact.json      the control case: a skin the engine REFUSES to render
  substations.json               428 real substations, real coordinates, real voltages
  build-substation-subset.py     how substations.json was cut from the release GeoJSON
```

---

## 1. Method, and the two things that nearly invalidated it

### 1.1 `document.hidden` was `true` for the whole session — MEASURED

Every tab in this Chrome reported `visibilityState: "hidden"` from the first call to the last.
I tried four escalating Win32 routes to fix it and **failed**:

| attempt | result |
|---|---|
| `ShowWindow(hwnd, 9)` + `SetForegroundWindow` on `Process.MainWindowHandle` | reported `FG=1247790`, tab still `hidden` |
| `AttachThreadInput` + `BringWindowToTop` + `SetForegroundWindow` | same |
| `EnumWindows` sweep for `Chrome_WidgetWin_1` | returned nothing — **my own bug**, see 1.2 |
| corrected sweep + `SW_RESTORE` + `HWND_TOPMOST`/`NOTOPMOST` | window flipped to *not visible* |

Only one Chrome browser window exists (`563 × 847` logical at `751,178`), and its geometry does not
correspond to any tab's `innerWidth` (1707 and 2327 were reported by two different tabs). The most
likely explanation: **background tabs in Chrome do not receive a resize, so `innerWidth` on a
non-active tab is stale.** That is worth carrying forward on its own — a background tab's viewport
is a *memory*, not a measurement.

**What this means for what follows.** The hidden-tab hazard is specifically about *rendering*:
rAF, WebGL, and anything the engine drives off map events. It does **not** affect `matchMedia`,
`navigator.*`, `screen.*` or `devicePixelRatio`, which are static device facts. So:

- §2's detection matrix is **trustworthy**.
- Geometry read off the **live Atlas** in this session is **not**, and I have not used any.
- Geometry read off **my prototype** is trustworthy because the prototype has no WebGL and no
  rAF dependence — it draws in a `setTimeout(0)` fallback for exactly this reason. Screenshots
  confirmed it painted.

Direct corroboration that this tab was in the failure state: on the live Atlas with a Botley West
deep link, `document.querySelectorAll('.scada-keys input').length === 0` — **zero layer
checkboxes**, exactly the picture the 202609031400 audit reproduced. The bug under investigation
was running underneath the investigation.

### 1.2 A correction to the estate's own foregrounding recipe

`sessions/202609031400-deep-link-audit` records `ShowWindow(hwnd, 9)` + `SetForegroundWindow` as
the fix. **On this machine today it does not work**, and there is a second trap: a `DllImport` of
`GetWindowTextW`/`GetClassNameW` without `CharSet=CharSet.Unicode` marshals the `StringBuilder` as
ANSI, so every window title comes back as **its first character only**. My first sweep printed
`cls=C title=G` and found zero Chrome windows. A sweep that returns the same wrong answer for every
window is a broken instrument, not a finding — the same shape the CLAUDE.md already warns about for
`MSYS_NO_PATHCONV`.

### 1.3 The narrow-viewport method, restated so the next session does not lose it

`resize_window` still lies on this machine. **The method that works, and worked again today:**

> Load a page on the target origin, inject a same-origin `<iframe>` at a declared CSS width, and
> point its `src` at the deep link. Inside the frame `innerWidth`, media queries and `100dvh`
> evaluate **genuinely**; same origin means `contentDocument` is readable and every box is
> measurable with `getBoundingClientRect()`.

Verified again in this session against the prototype: a 320 × 400 frame reported
`innerWidth: 320`, `matchMedia('(max-width:420px)').matches === true`, and the child page ran its
own skin selection inside it. It cannot simulate `pointer: coarse` — the frame inherits the host's
pointer — so anything gated on `pointer:coarse` remains **unverified**.

---

## 2. Part 1 — the detection matrix, as measured

Chromium 152, Windows, `dpr 1.5`, `document.hidden true`.

### 2.1 Pointer and hover

| signal | value here | trust |
|---|---|---|
| `(pointer: coarse)` | `false` | reliable, but it describes only the **primary** input |
| `(pointer: fine)` | `true` | reliable |
| `(pointer: none)` | `false` | reliable |
| `(any-pointer: coarse)` | `false` | reliable — **the honest one for hybrids** |
| `(any-pointer: fine)` | `true` | reliable |
| `(hover: hover)` | `true` | reliable |
| `(hover: none)` | `false` | reliable |
| `(any-hover: hover)` | `true` | reliable |
| `navigator.maxTouchPoints` | `0` | reliable |
| `'ontouchstart' in window` | `false` | reliable, but a *capability*, never a *preference* |

### 2.2 Geometry

| signal | value here | trust |
|---|---|---|
| `innerWidth × innerHeight` | `1707 × 842` | **stale on a background tab** — see §1.1 |
| `outerWidth × outerHeight` | `0 × 0` | **lies.** Zero, from an extension-driven context |
| `screen.width × height` | `1707 × 1067` | reliable |
| `screen.availWidth × availHeight` | `1707 × 1019` | reliable |
| `devicePixelRatio` | `1.5` | reliable |
| `visualViewport` | present | reliable; the only honest source under a soft keyboard |

### 2.3 Identity and capability

| signal | value here | trust |
|---|---|---|
| `userAgentData.mobile` | `false` | **coarse to the point of uselessness.** A tablet, a car head unit, a TV and a fridge all say `false` |
| `userAgentData.platform` | `"Windows"` | reliable, irrelevant to form factor |
| `userAgentData.brands` | `Chromium 152, Not?A_Brand 24, Google Chrome 152` | reliable |
| `navigator.deviceMemory` | `16` | **bucketed and capped at 8 by spec.** Reading `16` means the value is not spec-clamped here; do not treat it as exact, and it is absent in Safari and Firefox entirely |
| `navigator.hardwareConcurrency` | `20` | reliable |
| `navigator.connection.effectiveType` | `"4g"` | a rolling estimate; it changes mid-session |
| `navigator.connection.downlink / rtt` | `10 / 100` | **quantised placeholders.** `10` and `100` are the clamp values, not a measurement |
| `navigator.connection.saveData` | `false` | reliable **only when `true`**; `false` means nothing |
| `navigator.connection` overall | present | **absent in Safari and Firefox** |

### 2.4 Preference and orientation

| signal | value here | trust |
|---|---|---|
| `(prefers-reduced-motion: reduce)` | `false` | reliable, and the only one of these that is a stated *preference* |
| `(prefers-color-scheme: dark)` | `false` (light) | reliable |
| `screen.orientation.type` | `landscape-primary` | reliable |
| `(orientation: landscape)` | `true` | reliable |
| `(display-mode: standalone)` | `false` | reliable |
| `(scripting: enabled)`, `(update: fast)` | `true` | reliable, rarely useful |

### 2.5 Which signals separate the environments the architect named

**This is the part that matters, and the answer is mostly "none".**

| environment | what the browser says | separable? |
|---|---|---|
| **laptop** | fine pointer, hover, not mobile, large screen | — |
| **phone** | coarse pointer, no hover, `mobile: true`, narrow | **YES.** The one environment detection genuinely gets right |
| **tablet** | coarse pointer, no hover, `mobile: false`, wide | **partly.** Separable from a phone by width; separable from a touch laptop by *nothing* |
| **touch laptop** | `any-pointer: coarse` **and** `pointer: fine`, hover | **NO** — indistinguishable from a tablet in a keyboard case, which is the same physical object |
| **smart TV** | `pointer: fine`, `hover: hover`, huge screen | **NO.** A TV and this laptop report identical pointer, hover and scripting. The only signal is UA sniffing (`SmartTV\|Tizen\|Web0S\|GoogleTV\|BRAVIA\|AFTM`), which is a string match, not a measurement |
| **car head unit** | varies by platform; often coarse + no hover, i.e. **a phone** | **NO.** Android Automotive presents as a tablet. There is no viewing-distance signal in any web API |
| **hub (voice + touch, fixed distance)** | coarse pointer, `mobile: false`, mid-width | **NO** — identical to a tablet |
| **watch** | coarse pointer, very narrow, low memory | **partly**, by width alone; there is no watch media feature |

> **A TV and a desktop both report `pointer: fine` and `hover: hover`. So do a control-room wall
> display and a laptop. The two environments that most need different layouts are the two the
> browser cannot tell apart.**

There is no `(viewing-distance)` media feature, no `(device-class)`, and `interaction-media`
proposals for D-pad/remote input have not shipped. Detection can identify *a phone*. For everything
else it is a guess, and **a guess that cannot be overridden is a defect**. That is the entire
argument for §3.

---

## 3. Part 2 — the rule: detection selects a default, the user selects the truth

**BUILT AND VERIFIED** in `prototype/index.html` + `engine.js`.

Precedence, highest first:

1. **`?skin=<id>` in the URL.** A link can pin a skin. This is what a kiosk, a car dock, a TV
   bookmark and every test harness need. Verified: `?skin=glanceable` in a 320 px iframe.
2. **The reader's stored choice** (`localStorage['gridatlas.skin']`). Survives reload and survives
   deep-link arrival. Verified.
3. **Detection**, via `chooseSkin()`. Verified: it selected `desktop` here, scoring
   `desktop 70 · glanceable 0 · tenfoot 0`, and said why: *width ≥ 1024; pointer: fine; hover
   available; UA-CH not mobile; baseline 5*.

Three things the UI does that follow directly from §2.5:

- **The badge always says how the skin was chosen** — `auto-chosen — you can change it` /
  `your choice, remembered` / `pinned by ?skin= in the URL`. An auto-choice that does not announce
  itself as a guess is indistinguishable from a decision.
- **The reasons are printed.** `Why desktop: width >= 1024; pointer: fine; …` — a reader who
  disagrees can see what the machine thought.
- **`Reset to automatic`** exists, so a stored choice is not a trap.

Detection is declared **in the skin file**, not in the engine. `engine.js` contains no skin id
anywhere; `scoreSkin()` evaluates whatever predicates a skin's `detect` block declares
(`maxWidth`, `minWidth`, `minScreenWidth`, `pointer`, `hover`, `mobile`, `saveData`,
`maxDeviceMemory`, `uaMatch`, `baseline`). A new skin declares its own detection.

### 3.1 Does this remove the gestureless-fullscreen defect? — CONFIRMED in source, YES

The mechanism, read from the composed cartridge
`gridatlas/atlas/cartridges/202609031316-sld-sandbox-v9-8.js`:

- `:5485` `function trayTarget()` — `matchMedia('(pointer: coarse)').matches || innerWidth <= 700`
- `:6011` `if ((q.get('repd_ref') !== null || coordsUsable()) && trayTarget()) {`
- `:6013` &nbsp;&nbsp;`window.enterFullscreen?.();`
- `:6014` &nbsp;&nbsp;`link.arrival_fullscreen = true;`

`enterFullscreen` is defined in the substation-intelligence cartridge lineage
(`202609012045-substation-intelligence-v9-63.js:417` and successors). It **adds the layout classes
first** (`body.fs-active`, `#map-container.is-fullscreen`), **then** calls
`el.requestFullscreen()`. On a deep-link arrival there has been **no user gesture**, so
`requestFullscreen()` rejects into an empty `.catch(() => {})`; no `fullscreenchange` fires, so
nothing removes the classes. The page is left with `.map-container { position:fixed; 100vw;
100dvh; z-index:500 }` covering the dashboard, and the layer panel parked at `translateY(-100%)`.

**Where my design lands:**

| | live v9.89 | this prototype |
|---|---|---|
| who decides the layout | `trayTarget()`, at arrival, unasked | the skin, chosen by §3's precedence |
| full-bleed achieved by | Fullscreen **API** + classes | **CSS only.** `.shell .surface { position:absolute; inset:0 }` |
| `requestFullscreen()` calls | 1, gestureless, on every touch arrival | **zero.** The identifier appears once in each file, both times inside a comment saying it is not called; there is no call site |
| failure mode | classes applied, browser not fullscreen, dashboard covered | none — there is no promise to break |
| the reader can undo it | only by finding `✕ Exit` | it is a skin; the switcher is always visible |

**So: yes, and by construction rather than by fix.** Full-bleed is the *default layout* of every
skin (the architect's "gamify must be full-screen first"), and the Fullscreen **API** becomes an
optional extra that a *gesture* may request — never something an arrival does on the reader's
behalf. I did **not** verify on a real touch device that this cures the architect's phone; I
verified the mechanism in source and that my design contains no call that can exhibit it.

---

## 4. Part 3 — where the seam is, and where it is not

### 4.1 The finding: **the seam does not exist in the current code, and it is one line-shape away**

This is the most useful thing in this document, so it is stated plainly.

**The good news is real and specific.** v9.89 did the hard half. `link.measure` is already a
genuine engine namespace, exported at `sld-sandbox:3593` and extended at `:3686–3697`:

```
link.measure = { distanceKm, voltagesKv, representativePoint,
                 nearestSubstations, MIN_KV, MAX_LINK_KM, LINK_COUNT,
                 PROJECT_TECHS, flowDash, flowIndex, OFFSHORE_TECHS,
                 isProjectTech, coverage }
```

`nearestSubstations(lon, lat, subs)` takes a longitude, a latitude and a candidate set, and **reads
no technology at all**. The cartridge's own comment says the separation *is* the invariant and is
checkable from there. That is a seam, and it holds.

**The bad news is that the seam stops one function short of presentation.** The functions
immediately downstream of the measurement **return HTML strings**:

| function | file:line | returns |
|---|---|---|
| `nearestScope(n)` | `sld-sandbox:2543` | `` `<p class="neon-caveat">Scope: …</p>` `` |
| `corridorBeside(km)` | `sld-sandbox:2333` | `` ` &middot; ~19.6 km corridor estimate (<span class="neon-caveat">…</span>)` `` |
| `declaredBlockHtml()` | `sld-sandbox:2562` | `<div class="neon-hd">…<ol><li>…` |
| `caveatHtml()` | `sld-sandbox:3798` | markup |

**A skin cannot re-lay-out a `<p class="neon-caveat">`.** It can only place it. The honesty text —
the sample, the coverage denominator, the corridor calibration, the "straight" qualifier — is
welded to one set of tags and one class vocabulary. A glanceable skin, a TV skin and a desktop skin
all need the same *facts* at three different lengths and three different type scales, and today
they would all receive the same paragraph.

> **Verdict: the seam is in the right place for the measurement and in the wrong place for the
> qualifiers.** The measurement is data. The sentences that make the measurement honest are markup.
> That is the single change that unblocks skins, and it is a return-shape change to four functions,
> not an architecture.

### 4.2 What the prototype puts in the seam instead

`engine.read(subject, subs, opts)` returns one **frozen, flat, tag-free** object —
`gridatlas.reading/1` — carrying `subject`, `scenario`, `state`, `measurement` and `sample`. No
HTML, no class names, no lengths, no colours. That object is the entire contract.

Verified against the live Atlas, same coordinates, same release data:

| | live Atlas v9.89 | prototype engine |
|---|---|---|
| nearest ≥400 kV to Botley West | Cowley Substation · **15.76 km** | Cowley Substation · **15.757 km** |
| corridor estimate | **~19.6 km** (×1.245) | **19.62 km** (×1.245) |
| coverage at 400 kV | 355 published / 214 located / 141 unlocated | identical (snapshotted from the live call) |
| coverage at 33 kV | 886 / 502 / 384 → **56.7 %** | identical |

The geodesy is a verbatim port of `atlas/modules/202609011950-geodesy.js` — `R = 6378.137`,
haversine in the `atan2` operand order the estate ships, because parity is the claim being made.

One honest discrepancy, and it is the architecture working: the prototype's superlative says
*"nearest of the **166** mapped substations at 400 kV or above that this search could see"* where
the live Atlas says a larger number, because the prototype loads a 428-row geographic subset and
the live Atlas loads 5,800 features. **The denominator moved because the sample moved, and the
sentence moved with it.** That is exactly why `nearestScope()` computes it rather than hard-coding
it, and it survived the port.

### 4.3 The honesty contract is enforced **at the seam, by the engine** — BUILT AND VERIFIED

This is the part I would defend hardest.

`engine.FIELDS` is the entire vocabulary a skin may reference. Each entry may declare
`mandatory_with`:

```js
'measurement.headline': {
  mandatory_with: ['qualifier.straight', 'qualifier.sample', 'qualifier.scenario'],
  get: r => r.measurement.target_name + ' · ' + nf(r.measurement.straight_km, 2) + ' km'
}
```

`validateView()` runs before render. If a view names a superlative without naming the sample, the
word *straight*, and the record/scenario marker **in the same view**, the engine **refuses to
render that skin** and prints which rule was broken.

`skins/broken-compact.json` is the control case: a plausible, well-meaning compact skin that drops
the sentences to save pixels. Nothing in the engine mentions it. Measured output:

```
broken-compact/answer: "measurement.headline" may not be rendered without "qualifier.straight"  in the same view
broken-compact/answer: "measurement.headline" may not be rendered without "qualifier.sample"    in the same view
broken-compact/answer: "measurement.headline" may not be rendered without "qualifier.scenario"  in the same view
```

and the three real skins return `[]`.

> **This converts the spec's gate — *"no view may render a superlative without, in the same view,
> the sample and the word straight"* — from a rule a reviewer must remember into a rule a skin
> author cannot get past.** "A glanceable skin that drops the qualifier is a failed skin, not a
> compact one" becomes mechanically true.

Measured on the rendered DOM of all three skins:

| skin | surface | contains "straight" | contains the sample sentence | contains the record/scenario marker | clipped? |
|---|---|---|---|---|---|
| desktop | 700 × 420, right panel | yes | yes | yes | scrolls by design (536 / 398) |
| **glanceable** | **320 × 320, full-bleed sheet** | **yes** | **yes** | **yes** | **no — 288 / 288, it fits** |
| tenfoot | 640 × 360, bottom band | yes | yes | yes | **yes — 558 / 212, a real defect** |

The glanceable row is the answer to the brief's hardest question: **a watch-sized surface can carry
the project, the substation, the distance, the voltage, the word "straight", the sample it searched
and the record/scenario marker, unclipped, at 15 px base.** It does not need to drop anything.

The tenfoot row is a defect **in my skin, not in the architecture** — at 24 px base the sample
sentence overflows a 60 %-height band. Fixing it is editing two numbers in `tenfoot.json`
(`surface.safeAreaPct`, `type.base`) or swapping `qualifier.sample` for a shorter registered field.
**No engine change.** I have left it unfixed and recorded because an honest measured defect is
worth more than a tidied demo.

### 4.4 What the second skin cost — the Winamp test

The claim under test: *adding a skin requires zero engine change.*

| | files touched |
|---|---|
| `desktop.json` (first skin) | engine + host built alongside it, so not a fair test |
| **`glanceable.json` (second skin)** | **`skins/glanceable.json` + one filename in a manifest array. Nothing else.** |
| **`tenfoot.json` (third skin)** | **`skins/tenfoot.json` + one filename. Nothing else.** |
| `broken-compact.json` (control) | same — and it was refused, also with no engine change |

`engine.js` contains no string `"desktop"`, `"glanceable"`, `"tenfoot"` or `"broken"`. The renderer
in `index.html` is one function, `renderShell(skin, reading, w, h)`, which knows no skin id, no
project, and no technology; it applies the skin's palette and type as CSS custom properties and
walks its block list against `FIELDS`.

**The one honest caveat.** The list of skin filenames is an array in `index.html`, because HTTP has
no directory listing. A real integration reads `skins/index.json` — a one-line manifest a
non-programmer edits. That is a deployment detail, not an engine change, but it is not *zero* files
either and I will not claim it is.

**What a future skin author has to write:** one JSON file, no JavaScript.

```json
{
  "id": "hub", "label": "Hub", "author": "...", "for": ["kitchen display"],
  "detect":  { "maxWidth": 1024, "pointer": "coarse", "hover": false, "baseline": 0 },
  "surface": { "fullBleed": true, "chromePosition": "bottom-band", "panelWidth": 520 },
  "type":    { "base": 18, "scale": 1.0, "hero": 34, "lineHeight": 1.35 },
  "palette": { "ink": "...", "dim": "...", "hero": "...", "ground": "...",
               "panel": "...", "rule": "...", "warn": "...", "scenario": "..." },
  "autoCollapse": { "enabled": true, "idle_ms": 6000 },
  "layers":  { "mode": "facets", "pageSize": 30, "startOpen": false },
  "views": [ { "id": "answer", "detent": "half", "blocks": [
      { "field": "qualifier.scenario",   "style": "badge" },
      { "field": "subject.name",         "style": "title" },
      { "field": "measurement.headline", "style": "hero" },
      { "field": "qualifier.straight",   "style": "qualifier" },
      { "field": "qualifier.sample",     "style": "qualifier" } ] } ]
}
```

They may reference only registered `field` ids and only registered `style` names. They cannot
compute, cannot reach into the reading, cannot invent a sentence, and cannot omit a mandatory
qualifier. **That is the Winamp property: the skin is data, the engine is code, and the data cannot
lie.**

---

## 5. The 1000-layer architecture

**BUILT AND VERIFIED at 1000 synthetic layers** against the real registry
(`engine.LayerRegistry`), driving the real virtualised list in the prototype.
**DESIGNED, NOT BUILT:** the integration with MapLibre and with the real 60 layer ids.

### 5.1 Five states, and the distinction the architect's word "minimising" demands

| state | payload | on the map | cost | who causes it |
|---|---|---|---|---|
| `declared` | none | no | **~140 bytes of manifest** | boot |
| `loading` | in flight | no | one fetch | the reader |
| `loaded` | held | yes | paint + memory | the reader |
| `minimised` | **held** | no | memory only; **reopening is 0 ms** | **presentation** |
| → `declared` (unload) | **released** | no | refetch to return | **the engine, and it is always reported** |

> **Minimise is a presentation act. Unload is an engine act. A skin may minimise; only the engine
> may unload, only under memory pressure, and never silently.**

Measured at 1000 declared layers: manifest **136.7 KiB** (140,000 bytes); the same 1000 with
payloads would be **1.18 GiB** (1,265,377,425 bytes). That ratio is the argument: *existence must be cheap, presence must be paid for.*

### 5.2 Two budgets, because they are two resources

- **`paintBudget` = 24** — how many layers may be attached to the map at once.
- **`memoryBudget` = 120** — how many may hold a payload at once.

At the **paint ceiling** the engine **refuses and names what to turn off**:

```
At the paint ceiling (24 layers on the map). Turn one off first —
least recently used: Transmission · circuit · 400 kV · GB, Demand · heatmap · Wales, …
```

It never silently drops a layer. **A silent drop is exactly the false green that let
`wind_onshore`, `wind_offshore` and `other` ship dark.** At the **memory ceiling** the engine
evicts the least-recently-touched `minimised` layer to `declared` and emits an `UNLOAD` event with
`why: 'memory budget'`.

Those numbers are a **starting budget, not a measurement.** I did not measure MapLibre's real
per-layer paint cost. 24 is chosen because the live style already carries 116 layers of which ~25
are GridAtlas's own, so that is the order of magnitude already in play. It must be measured before it ships.

### 5.3 Health is observed, never self-reported

`registry.health()` asks **the map adapter** whether each layer is attached, and compares that to
what the registry believes. It never reads its own flag.

There is a button in the prototype, `Corrupt one layer behind the registry's back`, which removes a
layer from the map without telling the registry — reproducing
`link.technology_layer.enabled === true while the layer is off`. `Check health` then reports:

```
HEALTH: 1 of N disagree with the map: ly-0007 says loaded, map says false
```

**Any layer-health field that a proof can read must be produced by asking the renderer, not by
asking the toggle.** That is the whole lesson of the 32.7 % finding, expressed as an API.

### 5.4 The list is never a list

Discovery at 1000 is **search + facet + page**, virtualised. Measured in the prototype:

- 1000 rows declared; **18 DOM rows existed at the moment of measurement** (visible window ÷ 30 px
  row, plus an 8-row overscan). The count is bounded by the viewport, not by the registry.
- Facets computed from the manifest: group (10), kind (7), voltage (6 bands — a seventh bucket is
  "no voltage", which is correctly absent rather than shown as a band), each with counts.
- A flat checkbox list of 1000 would be 1000 nodes and ~30,000 px of scroll — on a phone that is
  **45 screenfuls**.

`registry.query({text, group, kind, kv, state, offset, limit})` returns a **page of manifest rows**.
A skin renders a page. **A skin never sees a payload**, which is what keeps the seam intact: the
skin declares `layers.mode` — `none` (glanceable exposes no layers at all), `facets` (desktop),
`dpad` (TV) — and the engine answers the same query for all of them.

### 5.5 A layer for every category is broken by construction

Carried forward from the audit and designed against, not rediscovered: `wind_onshore`,
`wind_offshore` and `other` light **no layer** — 32.7 % of a 7,680-row spine. So in this
architecture:

- a manifest row's **absence is a first-class state**, not an error;
- no layout reserves space for a layer that may not exist;
- **no skin branches on technology.** `subject.technology` is a registered *label field* that
  renders as text or not at all. `engine.js` contains no technology branch anywhere.

### 5.6 What happens at the ceiling during "full-scale sandbox play"

The interactive experience is the thing being protected, so: **the budget is enforced on the way
in, never during the interaction.** Panning, zooming and dragging a project touch no budget — they
touch only the ~24 layers already attached. Only *adding* a layer can hit a ceiling, and only that
action can be refused, with a sentence naming what to turn off. Nothing disappears while a reader
is moving the map.

---

## 6. Full-screen first, and chrome that puts itself away

**Full-bleed is the default layout of every skin** — `.shell .surface { position:absolute; inset:0 }`
— and **no skin calls `requestFullscreen()`** (§3.1). The Fullscreen API becomes an optional,
gesture-initiated extra rather than something an arrival does unasked.

**Self-minimise is specified as a behaviour, not an adjective.** `engine.AUTOCOLLAPSE`:

| | value | why |
|---|---|---|
| `idle_ms` | 6000 | no pointer, key, scroll or focus inside the panel |
| `after_commit_ms` | 1200 | a choice was made and the pointer left; collapse shortly after |
| `animation_ms` | 180 | motion is chrome, not content |
| `reduced_motion_ms` | 0 | under `prefers-reduced-motion`, snap; never animate |

**Never auto-collapses, in any skin — the skin may set the delay, it may not invent the
exceptions:**

`mid-edit` (a focused field, or a non-empty uncommitted value) · `unread-result` (a result the
reader has not yet seen) · `error` · `in-flight` (a fetch or recompute still running) · `pinned`
(the reader explicitly pinned it open).

Wired to the layer panel in the prototype and observable in its event log. Deliberately reports
rather than actually collapsing, so the panel stays inspectable during a demo; the exemption checks
run for real.

**Auto-collapse is what makes 1000 layers tolerable.** A panel that opens on demand and closes
itself is a different proposition from a permanent list, and it is the presentation half of
"minimise must not unload".

---

## 7. A value that changes while the reader watches

Designed toward, not scoped — the sandbox behaviour belongs to another cartridge. Two things this
architecture guarantees for it:

**7.1 `state` is a first-class field of the reading.** `settled` | `recomputing` | `unavailable`.
`FIELDS['state.notice']` renders *Recalculating…* and every skin carries it. **A superlative that
silently updates is more dangerous than one that says it is recalculating** — so the reading never
shows a stale number under a new position; it shows the old number *and* the recomputing notice, or
nothing.

**7.2 The record/scenario marker is non-negotiable at every size.** `reading.scenario.kind` is
`record` or `modified`. `FIELDS['qualifier.scenario']` renders `Public record` or
`SCENARIO — reader-modified, not the public record`, and it is in
`measurement.headline.mandatory_with` **alongside "straight"**. A skin cannot design it away for
space. On top of the text, the shell carries `[data-scenario="1"]`, which draws a 3 px scenario-
coloured outline around the entire surface and inverts the badge.

Verified live in the prototype: drag Botley West east, and the ring turns pink, the outline
appears, the badge flips to `SCENARIO`, and the measurement recomputes through the same
`nearestSubstations()` call. **A moved 840 MW project never reads as a consented scheme, at any
skin, at any size.**

---

## 8. Constraints checked

| constraint | status |
|---|---|
| Nearest is nearest-among-those-with-coordinates (~57 %) and the skin says so | **Held.** `qualifier.sample_full` renders 502/886 = 56.7 %, computed, not literal |
| The superlative names the sample it searched | **Held**, and enforced by `mandatory_with` |
| "straight" appears in the same view as the number | **Held**, enforced, and **verified in all three rendered DOMs** |
| No grading verdicts; scope never implies capacity | **Held.** No `FIELDS` entry produces an adjective. Capacity and measurement are separate blocks in every skin |
| Deep-link contract survives every skin | **Partly.** `?skin=` composes with the existing query string and the prototype reads `repd_ref`-shaped subjects. **The null-island guard and `zoom` honouring were NOT ported** — see §9 |
| No skin branches on technology | **Held.** No technology identifier appears in any layout path in `engine.js` or `renderShell()` |
| Desktop unregressed | **Not proven.** The desktop *skin* exists and carries the full content; I did not run the §1.8 desktop baseline against it |

---

## 9. What I did not do — stated plainly

1. **NOT ATTEMPTED: any change to the live Atlas.** Nothing was deployed. The prototype is a
   separate host with a re-implemented engine; it is a demonstration of a seam, not a migration.
2. **NOT VERIFIED: `pointer: coarse` anywhere.** No touch device in this session. Every claim about
   phone or watch behaviour is a claim about CSS width, not about a real coarse pointer. Fifth
   session to fail at this.
3. **NOT VERIFIED: a visible tab.** `document.hidden` was `true` throughout; four foregrounding
   routes failed (§1.1). Prototype rendering is corroborated by screenshot and by
   `getBoundingClientRect()`, both of which were consistent; live-Atlas geometry was not measured
   and is not quoted.
4. **NOT MEASURED: MapLibre's real per-layer cost.** `paintBudget: 24` and `memoryBudget: 120` are
   reasoned starting values. They must be measured before they ship.
5. **NOT PORTED: the deep-link contract's guards.** Null-island / REPD false-origin
   (`place-global-search:208–213`, `sld-sandbox:6001`) and `zoom` finite-and-3–18
   (`sld-sandbox:5967`) are not in the prototype. They belong to the engine, not to any skin, and
   nothing here moves them — but I did not re-implement them and must not be read as having tested
   them.
6. **NOT BUILT: virtualisation against real layers.** 1000 synthetic manifest rows against the real
   registry, not 1000 real GeoJSON products.
7. **NOT DONE: the desktop no-regression run** against §1.8 of the mobile-first spec.
8. **NOT DONE: a real 10-foot check.** The `tenfoot` skin was measured at 640 × 360 as a scale
   model, and it overflows (§4.3). It has not been seen on a television.

---

## 10. Dissent, since it was invited

**I believe the skin architecture is right, with one amendment, and I would build it.** But the
honest form of my agreement is narrower than the brief's framing, so:

**Where the Winamp analogy holds.** A presentation shell for a measurement genuinely is data. Type
scale, palette, block order, which facts appear at which size, how layers are exposed — all of that
is declarative, and today it is scattered through 7,423 lines of one cartridge as HTML string
concatenation. Making it data is a straightforward improvement with a clear test, and the test
passed: two extra skins cost two JSON files.

**Where it does not hold, and the amendment.** Winamp's engine emitted **PCM samples** — a
substrate with no semantics, which is why any skin could draw anything over it without lying. This
engine emits **a claim about the physical world**, and a claim can be misrepresented by layout
alone. Print `Cowley · 15.76 km` in 56 px on a wall and drop one sentence, and the product has said
something it cannot support. A visualiser cannot libel a waveform; a skin can libel a grid
connection.

So: **the skin may own everything except what makes the measurement honest.** That is not a
limitation of the analogy, it is the correction to it, and it is why `mandatory_with` lives in the
engine and not in a style guide. A skin system for this product without an enforced honesty
contract would be actively worse than the current monolith, because it would industrialise the
production of views nobody reviewed.

**The one thing I would sequence differently from the brief.** The brief treats "prototype a second
skin" as the proof. I think **the four HTML-returning functions of §4.1 are the proof**, and the
skins are the demonstration. If the estate does exactly one thing from this document, it should be:

> Change `nearestScope()`, `corridorBeside()`, `caveatHtml()` and `declaredBlockHtml()` to return
> **data**, and move their sentence construction into a field registry with `mandatory_with`. Keep
> the current card as the first consumer, byte-identical in output.

That is a contained, testable change to one cartridge with a value-for-value parity gate. Every
skin in this document, and every skin nobody has thought of yet, becomes possible the moment it
lands. Nothing in the mobile-first spec's P1–P10 conflicts with it, and P5 (the sheet) becomes
much cheaper on the other side of it.

**And a caution about scope.** "Endless avatars for any environment" is the right north star and
the wrong first commitment. There are **four** environments with real readers today — desktop,
phone, tablet, and the peek/glance case — and detection can only distinguish one of them reliably
(§2.5). A car, a TV and a watch are all served by a *glanceable* skin plus a switcher; none of them
needs its own skin until someone is actually holding one. Build the seam, ship two skins, keep the
third as proof the seam is real. That is what this prototype is.
