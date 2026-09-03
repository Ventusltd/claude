# GridAtlas — the scenario sandbox

Measured against the live Atlas at `https://ventusltd.github.io/gridatlas/atlas/`, composition generation
**202609031316**, version ledger newest **v9.89** (`9593f0a`). Nothing in the Atlas was changed to produce this.

This is a specification and a plan. It came out of driving the product, not out of reading it, and the
order below follows what I found rather than what I set out to look for.

---

## 0. How this was measured, and the one thing that blocked it

Everything numeric here was taken from a live Atlas session with Botley West (REPD 12588, 840 MW, solar)
loaded by deep link, by calling the page's own published surfaces — `window.__GRIDATLAS_NEON_LINKS__`,
`__GRIDATLAS_SLD__`, `__GRIDATLAS_TOPOLOGY__`, `__GRIDATLAS_MODULES__`.

`document.hidden` was **true** for the whole session and stayed true. The consequences were exactly the
ones this estate has already recorded: `map.loaded()` never became true, the arrival `flyTo` never ran
(the map sat at its default centre −3.5, 54.0 at zoom 12), and `queryRenderedFeatures` returned 0 at every
coordinate including the project's own. **No claim below rests on `queryRenderedFeatures`, on a
screenshot of the map canvas, or on a synthesised map click resolving to a feature.** Where a finding
could only be established from source, it says so and names the line.

What the hidden tab did *not* block: the arrival card rendered and was fully readable; every module
computed correctly; `selectAt` recomputed and repainted the card; the DC power-flow solved and validated.
The measurement engine does not need a painted canvas, which is itself the most useful architectural fact
in this document.

---

## 1. What I found by using it

### 1.1 "Move the project" already exists, and it is one line

`window.__GRIDATLAS_NEON_LINKS__.selectAt(origin, name, tech, fromSubstation, statedMw)` is public on the
page. I took Botley West and put it in a field near Redditch, 40 km north-west:

```js
await __GRIDATLAS_NEON_LINKS__.selectAt([-1.60, 52.10], 'Botley West…', 'solar', false, 840);
```

**3.7 ms.** The entire card re-derived: nearest substations at ≥33 kV within 40 km over all **5,800**
qualifying substations, nearest 400 kV, the corridor estimate, the ETYS topology join, the site-wide
published envelope, and the scope sentence naming its sample. Before the move the nearest 400 kV was
Cowley; after it, Feckenham at 30.50 km straight / ~38.0 km corridor (×1.245), joined to NESO site FECK.

Every honesty rule travelled intact and unprompted. The scope sentence re-counted itself for the new
place — *"nearest of the 278 mapped substations at 400 kV or above that this search could see; the
operator publishes 355 connection points at that class and 214 of them carry coordinates, so 141 cannot
be measured to at all."* The corridor factor re-declared its calibration and refused to apply itself to
an overhead-line question. Nothing had to be taught to move.

So the answer to "what if it were somewhere else" is not a feature to be built. It is a function that is
already correct, already fast, and already unreachable by any reader.

### 1.2 And the moved card is a false planning record

Here is what that same card said after the move, verbatim from the DOM:

> Botley West, Botley - Botley West Solar Project
> solar · 840 MW
> Botley West, Botley, Oxford · OX29 4DZ · Oxfordshire
> **REPD 12588 · application submitted**
> FECKENHAM SUBSTATION …

A real REPD reference, a real Oxfordshire address, a real planning status — sitting above a grid
measurement to a substation in Worcestershire. The measurement block moved; the identity block did not.
The address line and the measurement below it now contradict each other, and nothing on the card says so.

The URL did not change either. A reader who moved the project and pressed share would send a link that
reloads the **true** Botley West — so the recipient sees different numbers from the sender and neither
knows it. A screenshot, by contrast, carries the false version and nothing else.

This is the whole risk in one screen, and it is reachable today by anyone with a console. It is the
reason this cartridge needs the marking design *before* it needs the drag handle.

### 1.3 Capacity changes nothing on the card. I checked four ways.

**Way one — the card.** I re-selected the same coordinate at 8 MW, 840 MW and 5,000 MW and diffed the
rendered card text. **Byte-identical, all three.** The only "840 MW" anywhere on the card comes from the
arrival card built out of the URL string; the argument is never read by anything that prints.

**Way two — the power flow.** The one place capacity is genuinely consumed is the DC injection response at
400 kV. I solved it directly on the live 573-bus model at Feckenham, at 100 MW and at 840 MW:

| | 100 MW | 840 MW |
|---|---|---|
| top branch share | −54.581073 % | −54.581073 % |
| second | −54.581073 % | −54.581073 % |
| third | +50.039339 % | +50.039339 % |
| branches above the 5 % floor | 127 | 127 |

Identical to six decimal places, and they must be: `share = flow_mw / mw` over a linear DC solve, so the
percentages are scale-invariant by construction. The card prints only shares. **Changing capacity cannot
change a single printed digit of the flow answer.** It changes the noun in the heading and nothing else.

**Way three — what *did* move.** In the same result object, `flow_mw` went −54.58 → −458.48 and
+50.04 → +420.33, exactly ×8.4. And those branches carry published summer ratings — 1,746, 2,217 and
2,211 MVA. So a capacity-dependent, provenance-bound quantity **already exists in the result and is
already thrown away.** That is the honest opening for capacity, and section 3 takes it.

Cost: model assembly 2.9 ms (cached after first use), re-solve **13–20 ms**.

**Way four — the layout.** `__GRIDATLAS_SLD__.fitToStatedCapacity()` is a real consumer: set `targetMw`
and it moves module and inverter counts until the array lands on the figure, publishing a signed residual
(0.27 % at 840 MW, −4.0 % at 84 MW). 1.7–10.9 ms. The SLD opens with a complete electrical and financial
model in 8.8 ms. But it is a different surface, reached by a button, and it does not feed the grid card.

### 1.4 There are already **three** arbitrary-point answers, on **two** datasets, and they disagree

`◈ Grid At Point` (`btn-gridpoint`) is the architect's described behaviour, already built. Its engine is
`__GRIDATLAS_NETWORK__.nearest(lon, lat, {limit})` and it answered my moved coordinate in **0.5 ms**:

> FECKENHAM 30.5 km · BERKSWELL 31.9 km · COVENTRY 40.7 km · PATFORD BRIDGE 42.9 km · KITWELL 46.4 km

So the coordinator's guess is confirmed: computing at an arbitrary point is not new work. But the shape of
what exists is more interesting than that, and it is the thing that decides the design.

| | Grid At Point | Grid Finding Scope | the project card (`selectAt`) |
|---|---|---|---|
| dataset | NESO published connection points | OSM substations | OSM substations |
| pool | 886, of which **502 have coordinates** | 5,800 at ≥33 kV | 5,800 at ≥33 kV |
| distance ceiling | none observed — returned 46.4 km | 25 km (outer band) | **40 km** (`MAX_LINK_KM`) |
| voltage floor | transmission classes only | ≥33 kV, classified by membership | ≥33 kV |
| answers with | named sites + km + topology block | census by 2/5/10/25 km band | full card: distances, corridor, ETYS, site-wide envelope, voltage-class context |
| cost | **0.5 ms** | not isolated | **3.7 ms** |
| reachable by | a map click, armed | a map click, armed | **a project feature only** |

**At my moved coordinate the nearest OSM substation at ≥33 kV is 3.71 km away and the nearest NESO
published connection point is 30.5 km away.** Both numbers are correct. One is a distribution substation
that OpenStreetMap has mapped; the other is a transmission connection point that NESO publishes. A reader
who presses one button sees a site with grid on its doorstep; a reader who presses the other sees a site
30 km from anything. Neither card tells them the other exists — the source-registry survey sentence names
which cartridges *could* have answered, but the numbers are never put side by side.

This is the real gap, and it is not the one I expected. Moving a project does not need a new engine. It
needs the **composition** — all three answers at one point, labelled by dataset, under one identity — and
that composition exists today only for a coordinate that happens to have a project feature drawn on it.

### 1.5 The blank click does not reach the scope

`grid-finding-scope-on-a-blank-click` is a declared capability, the SCOPE chip is on the map, and the
`grid-scope` module is loaded, correct, and carries its own refusal text. But in
`atlas/cartridges/202609031316-sld-sandbox-v9-8.js` the click handler reads, in this order:

```js
if (!features.length) { clearLinks(); return; }   // :5847
…
if (!hit) {                                        // :5858
  clearLinks();
  if (pointArmed) await runGridAtPoint(…);
  if (scopeArmed) await runGridScope(…);           // :5864
  return;
}
```

`interactiveLayerIds` (`:5733`) returns only the engine's own `l-*` layers — never the basemap. So a click
on genuinely empty ground has **zero** features and returns at `:5847`, before the scope branch. The scope
runs only when the click lands on some `l-*` feature that is neither a project nor a substation — a grid
line, an EV point, a pipeline layer. The literal blank click the capability is named for is the one case
it cannot serve.

I could not confirm the positive half live (the hidden tab makes `queryRenderedFeatures` return 0
everywhere, so *every* click looks blank). I did confirm the destructive half live: firing a
zero-feature click took the project popup from 1 to 0. **A stray click loses the reader's project.** In a
sandbox where the reader is meant to be poking at the map, that is not a small thing.

Both `SCOPE` and `◈ Grid At Point` sit behind this same guard (`pointArmed` at `:5863`, `scopeArmed` at
`:5864`), so the ceiling applies to both.

### 1.6 A small honesty defect in the published state

`link.armGridScope(on)` sets the internal `scopeArmed` but never writes `link.grid_scope_armed`
(`:3595`); only the chip's own handler does. After `armGridScope(true)` the page reports
`grid_scope_armed: false`. A reviewer asking the page which modes are live gets a stale answer. Two
characters to fix, and it belongs in Increment 0 because the scenario cartridge will publish state the
same way.

### 1.7 The compute is not the problem, and it never was

| operation | measured | over |
|---|---|---|
| Grid At Point, nearest published connection points | **0.5 ms** | 886 points, 502 located |
| move the project, full card re-derivation | **3.7 ms** | 5,800 substations |
| DC injection re-solve | **13–20 ms** | 573-bus 400 kV model |
| DC model assembly | 2.9 ms | once per session, cached |
| open the SLD with electrical + finance | 8.8 ms | — |
| fit a layout to a stated capacity | 1.7–10.9 ms | — |

Everything on the interaction path is single-digit to low-double-digit milliseconds on a desktop CPU.
The 4.09 MiB arrival is a **cold-start** cost, paid once, before any of this. Section 5 takes that
seriously; but the honest reading is that drag-to-recompute is a rendering and marking problem, not a
compute problem, and moving this particular arithmetic to a server would make it slower.

---

## 2. What exists, what is partial, what is new

| | state | evidence |
|---|---|---|
| Recompute the grid answer from an arbitrary coordinate | **exists, three times over** | `selectAt` 3.7 ms; `network.nearest` 0.5 ms; `gridScope.scope` — §1.4 |
| Measurement is technology-agnostic | **exists**, verified | v9.89; `currentPolicy` decides only which sentences print, the arithmetic reads no technology |
| A census from a bare point | **exists** | `gridScope.scope()`, bands 2/5/10/25 km, carries `what_this_is_not` inside the result |
| Named connection points from a bare point | **exists** | `◈ Grid At Point`, 0.5 ms, 886 published / 502 located |
| Reaching either by clicking blank ground | **partial — blocked** | returns at `:5847` before both branches (§1.5) |
| The three answers **composed** at one point, labelled by dataset | **new — and it is the real gap** | 3.71 km vs 30.5 km at the same coordinate (§1.4) |
| Capacity as a parameter | **exists, display-only** | identical cards at 8 / 840 / 5,000 MW (§1.3) |
| Capacity driving the layout | **exists, elsewhere** | `fitToStatedCapacity`, residual published, SLD surface only |
| Capacity driving a grid number | **new** | `flow_mw` against published ratings is computed and discarded (§1.3) |
| Drag machinery on the map | **exists, elsewhere** | `drag-array-and-rotate-handle`, `export-cable-with-editable-route`, `touch-drag-array-rotation-and-route` — the SLD sandbox's array centre and route pins |
| A draggable **project marker** | **new** | the ring is drawn by the cartridge, not a layer; it has no drag |
| Marking a scenario as not-the-record | **new — nothing exists** | §1.2 |
| A scenario in the URL | **new — nothing exists** | the URL never changes (§1.2) |
| Latency headroom for continuous recompute | **exists** | §1.7 |

The honest summary: **the engine is ready and the epistemics are not.** Almost none of the work is
arithmetic — the cartridge is thin, and it is thinner than I expected before I used Grid At Point. Nearly
all of the work is (a) carrying a project's identity and capacity to a new point, (b) composing three
existing answers so a reader cannot be misled by seeing only one of them, and (c) making sure a reader can
never mistake what they made for what is recorded.

---

## 3. The specification

### 3.1 One cartridge: `scenario-sandbox`

It owns: the scenario state object (origin, capacity, provenance, dirty flags); the draggable marker and
the drop-a-point affordance; the capacity control; the scenario banner and every mark in §4; the
`scenario=` URL parameter and its round trip; the "return to the record" action.

It owns no arithmetic. It calls `link.selectAt`, `network.nearest`, `gridScope.scope`,
`injectionResponse.respond` and `corridorEstimate` exactly as they stand. **No change to the measurement
engine, and none to the `grid-scope`, `geodesy` or `injection-response` modules.** The two edits it needs
outside itself are the click-order fix at `:5847` and the `grid_scope_armed` publication at `:3595`, both
in `sld-sandbox`, both tiny, both staged before the cartridge exists.

Its one substantive piece of new *content* is the **composed point card** of §1.4: the three existing
answers at one coordinate, each labelled with the dataset it came from and that dataset's own coverage.
The form that keeps it honest is to name the pool in the same breath as the number, which the estate
already does everywhere else:

> Nearest mapped substation at 33 kV or above: 3.71 km — OpenStreetMap, 5,800 mapped, ceiling 40 km.
> Nearest published connection point: 30.5 km, FECKENHAM — NESO, 886 published, 502 with coordinates,
> so 384 cannot be measured to at all.
> These count different things. Neither is the other's answer.

Without that last line the two numbers look like a contradiction or, worse, like a choice.

### 3.2 Move the project

Drag the ring, or long-press to drop a new point. Recompute on `dragend`, and also on a throttled tick
during the drag (§5). On release the card re-derives exactly as `selectAt` already does it, and the
scenario banner appears the instant the marker leaves its true position by more than **50 m** — a
threshold, not zero, so that a nudge that lands back on the site does not falsely accuse the reader of
having moved anything.

Distance moved from the record is stated on the card, in km and bearing. It is the cheapest possible
guard against a reader forgetting what they did.

### 3.3 Change the demand — and what it may honestly claim

Capacity becomes an input. Because §1.3 is what it is, the cartridge must be exact about the three tiers:

**Tier A — what capacity legitimately changes today.**

1. **Flow against published ratings.** `respond().branches[].flow_mw` scales linearly and the branches
   carry `published_ratings_mva`. At 840 MW injected at Feckenham the top branch takes 458 MW on a
   circuit with a 1,746 MVA summer rating. That sentence is publishable *with its existing caveats
   carried verbatim*: declared DC model, 100 MVA base, flat 1.0 pu, no losses, no taps, intact network,
   response to a new injection and **not a loading** — what is already on the circuit is not in this
   number. It is a screening quantity about the published model, not headroom, not a rating assessment,
   and no verdict is attached: the number is stated beside the rating and the reader draws the
   conclusion. No colour, no "comfortable", no "constrained".
2. **The layout.** `fitToStatedCapacity` with its published residual, already correct.

**Tier B — what capacity plausibly bears on but the estate cannot support today.** Whether a 33 kV
connection is credible at 840 MW is a real engineering question and the honest answer is that this
platform holds nothing that decides it. A voltage class is chosen by fault level, transformer capacity,
export arrangement and the operator's own design standard, none of which is in any pinned product here.
The cartridge may state the *arithmetic* — 840 MW at 33 kV is ~14.7 kA, which no distribution switchgear
in the payload is described as carrying — and must stop there, as a statement about current, not about
possibility. **Anything beyond that is an architect decision (§7), and until it is taken, this tier
prints nothing.**

**Tier C — what capacity must never appear to change.** Nearest substation, distance, corridor estimate,
voltage class of the nearest thing, the scope census. These are geometry. When a reader changes the
capacity the cartridge must make it visible that these did *not* move — the honest form is a quiet line
under the capacity control:

> Capacity does not change the distances above. Nearest is nearest whatever the project is.

Without that line, a reader typing 840 into a box and watching a card re-render will believe the card
responded. It did not. That sentence is the difference between a sandbox and a pretence.

`scope-never-implies-capacity` binds harder here than anywhere else in the estate, because for the first
time the *reader* supplies the megawatts. A number the reader typed feels validated by the act of being
accepted. It is not. The capacity control must therefore carry, permanently and not behind a disclosure:

> This is your figure, not an offer. Nothing here says the network can accept it.

### 3.4 The arbitrary point

Drop a point with no REPD identity. Same compute, no project record, no name, no address, no planning
status, no `repd_ref`. The card head reads **Scoped point** with the coordinate. This is the one state
that is *inherently* safe, because there is no true record to be confused with — and it is the state that
the blank-click fix (§1.5) unlocks for free.

All three answers are already available at such a point (§1.4). What is missing is the route to them and
the composition of them. This is therefore the **cheapest** of the three features and should ship first
of the three, not last: it exercises the composed card, the dataset labelling and the click fix, with no
identity to get wrong and no scenario to mark.

---

## 4. Hypothetical versus record — the part that is not negotiable

The rule: **at no moment may a reader, or a screenshot, or a link, be unable to tell a scenario from the
record.** Five mechanisms, all required, none sufficient alone.

**4.1 The card is re-headed, not annotated.** The moment origin or capacity departs from the record the
card's identity block is *replaced*, not badged:

```
SCENARIO — not a record
Based on Botley West, Botley (REPD 12588)
Moved 41.2 km NW of the registered site · capacity as recorded
```

The registered address and the planning status are **removed**, because they are the two lines that made
§1.2 dangerous. They return when the reader returns to the record. The REPD reference stays, prefixed
"Based on", because provenance is the point — but it is never again printed as a bare `REPD 12588` beside
a measurement that does not belong to it.

**4.2 The scenario reads differently.** A persistent band across the top of the card and a changed marker
— a hollow, dashed ring in place of the solid project ring, and a ghost ring left at the true position
with a tie line between them. The reader can always see where the project actually is. This also survives
a screenshot cropped to the map, which the banner alone does not.

**4.3 One action back to the truth.** "Return to the record" restores the true origin and the registered
capacity, drops the scenario marks, and re-derives. Always present, never behind a menu, never
destructive of anything but the scenario.

**4.4 The link says what it carries.** A modified scenario changes the URL — silence here is the failure
mode. The record parameters stay exactly as they are, and the scenario is carried *additively*:

```
…?repd_ref=12588&project=…&capacity_mw=840&latitude=51.8132088&longitude=-1.3489728
   &scenario=1&scenario_lon=-1.60&scenario_lat=52.10&scenario_mw=840
```

So the true record is always recoverable from the link, the scenario is unmistakably a separate thing,
and a consumer that does not understand `scenario=` renders the record — which is the safe default, not a
silently different one. An arrival with `scenario=1` opens with the banner already up and never shows the
registered address. An arrival at an arbitrary point carries `scenario=point` and no `repd_ref` at all.

**4.5 The dirty flags are published.** `link.scenario = { moved_km, bearing, capacity_source: 'reader' |
'record', origin_source: 'reader' | 'record' }`, so a proof and a reviewer can assert from outside the
page that the marks are up whenever the state is dirty. This is the gate that keeps 4.1–4.4 from
rotting.

**The existing rules all still travel:** nearest is nearest-among-the-mapped and names its sample; the
superlative names its sample; a straight line is not a route and says how far off; no grading verdicts;
`scope-never-implies-capacity`. A scenario earns no relaxation of any of them — it needs them more,
because the reader chose the inputs.

---

## 5. The latency budget, and whether the compute has to move

**Target: first repaint of the card within 100 ms of `dragend`; a continuous read-out during the drag at
≥30 fps.** Both are met today, by a wide margin, on the device.

| stage | measured | budget |
|---|---|---|
| nearest-substation + card re-derivation | 3.7 ms | 40 ms |
| corridor estimate, ETYS join, envelope | included above | — |
| DC injection re-solve (only when capacity or origin changes at a 400 kV site) | 13–20 ms | 40 ms |
| DOM write of the card | not isolated; card is ~4.9 kB of text | 20 ms |

**During the drag**, do not run the full card. Run only the cheap half — nearest substation name, distance
and voltage — into a one-line read-out that follows the marker, throttled to one `requestAnimationFrame`.
On `dragend`, run everything. The DC solve never runs during a drag.

**What has to be true for this to hold, and it already is:** the 5,800-substation payload (~1.2 MB) is
warmed at install, the 921-site topology and the 573-bus 400 kV model are built once and cached, and none
of the interaction path touches the network. The 4.09 MiB arrival is a cold-start cost paid before the
sandbox is reachable at all.

**So: no, the compute does not have to move server-side for this to be viable, and moving it would make it
worse.** A round trip to an engine is 40–200 ms on a good connection; the local answer is 3.7 ms. The
architect's principle — the engine computes, the phone renders — is right about *derivation of the data
product*, and it is already honoured: the phone is not deriving substation positions, corridor
calibrations or the ETYS model, it is receiving them precomputed and doing a haversine sweep and a sparse
solve over them. That is rendering an answer, not deriving one.

**Where the principle does bite, and it is the real data-plane question:** the 4.09 MiB arrival. That is
about the *cold start*, not the interaction, and it is the mobile-first spec's data-plane track, not this
one. The scenario sandbox should not be the reason that work happens, and it must not wait for it.

**If it ever cannot be met** — a much larger substation set, or a solve that stops being sparse — the
degradation is stated in advance: the drag read-out drops to nearest-only, the full card recomputes on
release with an explicit "measuring…" state (the arrival already has `showStatus`, and it says what it is
waiting for), and the capacity control debounces to 400 ms. The interaction becomes drop-then-answer
instead of drift-and-watch. It does not become wrong; it becomes slower, and it says so.

---

## 6. The increments

Each has one owning file and one gate. Order matters: **every safety mechanism ships before the
affordance that makes it necessary.** Nothing in 1–3 gives a reader a new way to make a hypothetical.

| # | what | owning file | gate |
|---|---|---|---|
| **0** | `armGridScope` publishes `grid_scope_armed` (§1.6) | `atlas/cartridges/…-sld-sandbox-v9-8.js` | page reports `grid_scope_armed: true` after `armGridScope(true)` |
| **1** | Blank click reaches SCOPE and GRID AT POINT: move the zero-feature return below the `!hit` branch, and stop a stray click destroying the card (§1.5) | same | a click on a coordinate with no `l-*` feature, scope armed, produces a `.gridatlas-scope-block`; nothing armed, the open project card survives |
| **2** | **The composed point card.** All three answers at one coordinate, each labelled with its dataset and that dataset's coverage (§3.1) | `atlas/modules/…-point-composition.js` (new, pure) | at one coordinate the card carries both the OSM number and the NESO number, each naming its pool, plus the line saying they count different things |
| **3** | **The arbitrary point.** Drop a point, no identity, `scenario=point` | `atlas/cartridges/…-scenario-sandbox.js` (new) | card head reads Scoped point, no `repd_ref` anywhere in card or URL, composed card present |
| **4** | Scenario state + all five marks of §4, driven only by the console/URL — no drag, no input box yet | `atlas/modules/…-scenario-state.js` (new, pure) | with `scenario=1` in the URL: banner up, registered address and planning status absent, "Based on REPD 12588" present, `link.scenario` dirty flags correct |
| **5** | `scenario=` round trip and "Return to the record" | `atlas/cartridges/…-scenario-sandbox.js` | share → reload → identical scenario; return → identical to the unmodified record, byte for byte |
| **6** | **Move the project.** Draggable ring, ghost ring, tie line, drag read-out, recompute on release | same | `dragend` → card re-derived and marks up within 100 ms; ghost ring at the true origin; `moved_km` matches an independent haversine |
| **7** | **Capacity as an input** — Tier A flow-against-rating and Tier C's "this did not change" line; Tier B prints nothing | same | at 8 / 840 / 5,000 MW the distance block is byte-identical and asserted so; the flow line scales ×; the reader's-figure caveat is present at every capacity |
| **8** | Chrome self-minimises: the controls collapse into the sheet of `sessions/202609031543-mobile-first-spec/00-SPEC.md` | same | the sheet's detents unchanged; no new floating control above the card |

The order changed once I used Grid At Point. The arbitrary point moved from last to third, because it is
the cheapest and it needs no scenario marking at all; and the composed card moved to second, because
every later increment renders through it. **Increments 4 and 5 still ship before 6 and 7** — the marking
before the affordance that makes it necessary — and that is the part of the order that is not
negotiable.

**Increment 8 coordinates with the mobile-first spec and does not compete with it.** That spec establishes
a bottom sheet with detents as the single home for chrome, and shows that the card already covers 53 % of
a phone screen with 36 % of it painted over by floating controls. The scenario controls must therefore
live **inside the sheet**, as a collapsed row that expands on demand — a capacity stepper and a "move"
toggle — and must not add a floating element. Two exceptions, both on the map because they are about the
map: the drag handle, and the scenario banner, which must remain visible when the sheet is at its lowest
detent for the reason in §4.2. That spec's sequencing law also applies unchanged here: de-overlap ships
before full-bleed.

---

## 7. What needs the architect

1. **Tier B — the voltage-class question.** May the cartridge say anything about whether a connection
   voltage is plausible at a given capacity? My position is that with the data pinned today it may state
   the current arithmetic and nothing else, and that anything resembling "33 kV is not appropriate at
   840 MW" — however true — is a grading verdict this platform does not make. If the answer is yes, it
   needs a source, and a rule that names it.
2. **The flow-against-rating sentence.** It is the only capacity-driven grid number available. It is also
   the one most likely to be quoted out of its caveats, because "458 MW on a 1,746 MVA circuit" reads
   like headroom and is not. Ship it, or leave capacity honestly inert until there is something better?
   I lean to shipping it *with* Tier C's disclaimer, because a sandbox where the input visibly does one
   real thing teaches more than one where it does nothing.
3. **The 50 m move threshold.** Chosen, not derived. Below it, no scenario is declared.
4. **Whether the sandbox is reachable from Pipeline News at all**, or only from inside the Atlas. A MAP
   button that can land a reader on a scenario is a different institutional risk from one that cannot.
5. **The two distance ceilings.** The project measurement stops at 40 km and says "no mapped substation
   within 40 km"; Grid At Point has no observed ceiling and returned 46.4 km. On the composed card those
   two conventions sit in adjacent lines. Harmonise them, or state both ceilings explicitly? I lean to
   stating both, because they are properties of different datasets and hiding that is how the two numbers
   start to look like one.

---

## 8. What I did not establish

- The positive half of §1.5 — that an armed scope or Grid At Point on a feature-bearing pixel draws its
  card — could not be confirmed live, because a hidden tab makes every pixel look featureless. Both
  engines were exercised directly and both answered. The negative half was confirmed.
- I did not press `◈ Grid At Point` and then click the map as a user would; I called its engine. The
  button exists, the handler is at `:5863`, and the engine answers in 0.5 ms. The binding between them is
  what §1.5 says it is.
- No touch drag was exercised. The SLD's `touch-drag-array-rotation-and-route` capability is declared and
  the array-centre and route-pin machinery is real, but I did not put a finger on it.
- The 100 ms `dragend` budget is arithmetic over measured stage timings, not an end-to-end measurement of
  a drag, which needs a visible tab.
