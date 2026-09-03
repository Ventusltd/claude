# The identity leak: a real planning record printed over a measurement for somewhere else

Measured against live **v9.89** at `https://ventusltd.github.io/gridatlas/atlas/`, cartridge
`atlas/cartridges/202609031316-sld-sandbox-v9-8.js` (7,423 lines), on 2026-09-03.

**Every measurement below was taken with `document.hidden === false`.** The MCP browser tab could not be
made visible — three other agents hold the active tab — so the whole session ran in a **separate Chrome
target of my own**, created over CDP on the debug port (9333) with `Target.createTarget{newWindow:true}`
and re-activated before each measurement. The target was stamped `window.__OWNER__ = 'identity-leak-agent'`
and every attach asserted both that stamp and `document.hidden === false`, aborting otherwise — it aborted
once, correctly, when another agent took focus. `queryRenderedFeatures` returned **797** features across
the viewport and **24** at the project point, so the map was genuinely live: the map-dependent half of this
finding rests on real hit-testing, not on a stalled canvas. The target was closed at the end and the MCP
tab is gone. **Nothing was changed on any shared surface, and nothing was deployed.**

---

## Verdict, first, because it decides urgency

**URL-reachable. Not console-only. And the URL is the artefact — it survives sharing.**

The prior agent reached the false card through `__GRIDATLAS_NEON_LINKS__.selectAt(...)` and concluded that
a shared link would reload the true project, so only a screenshot could carry the falsehood. That is not
what the page does. **A plain deep link with a correct `repd_ref` and wrong `latitude`/`longitude` produces
the identical false card, with no console, no interaction, and no gesture** — and because the state is in
the URL, the recipient of that link sees exactly what the sender saw.

This is not a design debt awaiting a drag handle. It is live on the production URL surface that Pipeline
News already writes links into.

---

## 1. Reproduction — the same card, twice, one parameter apart

Two loads of the live Atlas differing **only in the coordinate pair**. Same `repd_ref=12588`, same
`project=`, same `technology=solar`, same `capacity_mw=840`, same `zoom=12`.

```
TRUE   …?repd_ref=12588&project=Botley+West%2C+Botley+-+Botley+West+Solar+Project
        &technology=solar&capacity_mw=840&latitude=51.8132088&longitude=-1.3489728&zoom=12
FALSE  …?repd_ref=12588&project=Botley+West%2C+Botley+-+Botley+West+Solar+Project
        &technology=solar&capacity_mw=840&latitude=52.10&longitude=-1.60&zoom=12
```

### The identity block — byte-identical in both

Asserted in code: `TRUE.identity === FALSE.identity` returned `true`.

> Botley West, Botley - Botley West Solar Project
> solar
> 840 MW
> Botley West, Botley, Oxford · OX29 4DZ · Oxfordshire
> REPD 12588 · application submitted

### The measurement block — entirely different

| | TRUE load | FALSE load |
|---|---|---|
| head of measurement block | `COWLEY SUBSTATION` | `FECKENHAM SUBSTATION` |
| nearest 400 kV | Cowley Substation · **15.76 km** straight · ~19.6 km corridor | Feckenham Substation · **30.50 km** straight · ~38.0 km corridor |
| nearest ≥33 kV | 3.43 km Yarnton (132 kV) | 3.71 km Shipston (66 kV) |
| ETYS join | Cowley → NESO site **COWL** (NGET); 400, 132 kV | Feckenham → NESO site **FECK** (NGET); 400, 275, 66 kV |
| site envelope | 6 circuits, winter 1,180–2,779 MVA, 12.4–49.4 kA | 6 circuits, winter 955–2,009 MVA, 23.4–32.6 kA |
| circuits reach | CULHAM JET, DIDCOT, EAST CLAYDON, LEIGHTON BUZZARD, MINETY, WALHAM | BERKSWELL, BISHOPS WOOD, HAMS HALL, IRONBRIDGE, MINETY, WALHAM |
| `link.last_selection.nearest_km` | 3.432 | 3.708 |

Full verbatim cards: `evidence/card-TRUE-coordinates.txt`, `evidence/card-FALSE-coordinates.txt`.

### The map corroborates the false card rather than contradicting it

This is the part that makes the artefact convincing, and it is worse than the console route.

- Camera bounds on the FALSE load: **lon −1.4672 to −1.2308, lat 51.7892 to 51.8372** — Oxfordshire.
  Bladon, Begbroke, Yarnton, Wolvercote, Cassington are all on screen. The camera flew to the **register's**
  coordinates.
- `__GRIDATLAS_PLACE_SEARCH__.deep_link` reports `status: "RESOLVED"`, `longitude: -1.348973`,
  `latitude: 51.813209` — the page holds the true coordinates.
- The project pin source `gridatlas-project-pin`, labelled
  `"Botley West, Botley - Botley West Solar Project"`, sits at **[−1.6, 52.1]**.
- Every neon link in `gridatlas-neon-links` originates at **[−1.6, 52.1]**.

So the pin carrying the real project's name, and all five measurement lines, are drawn **36 km NW of the
visible map** where no reader can see them. Nothing on screen contradicts the card. The reader sees an
Oxfordshire map, an Oxfordshire address, a genuine REPD reference, and a measurement to Worcestershire,
and there is no visual cue that the third does not belong to the first two.

Screenshot: `evidence/false-card-screenshot.png`.

---

## 2. Which blocks moved and which did not

The card is one `.maplibregl-popup-content` with four children:

```
[0] .gridatlas-card-bar              grab bar + minimise + close        DID NOT MOVE
[1] (unclassed div, 148 chars)       name · tech · MW · address · REPD · planning status
                                                                        DID NOT MOVE
[2] .maplibregl-popup-close-button                                      n/a
[3] .gridatlas-neon-block            the whole measurement, 4,776 chars MOVED, correctly
```

Child `[1]` is written by the identity lane from the register row. Child `[3]` is written by
`injectIntoCard` (`:4160`), which does
`content.querySelectorAll('.gridatlas-neon-block').forEach(n => n.remove())` and appends the new one. It
takes `document.querySelector('.maplibregl-popup-content')` — **whatever card is on screen** — and never
reads, writes, checks or clears the identity sibling above it. The two blocks have no relationship in code
beyond sharing a parent.

The card bar also did not move: it still reads *Botley West, Botley - Botley West Solar Project*, so the
falsehood survives the card being minimised to its bar.

---

## 3. The defect, on one line of source

`atlas/cartridges/202609031316-sld-sandbox-v9-8.js:6021`

```js
if ((!coordsUsable() || !isProjectTech(tech)) && q.get('repd_ref')) {
  const resolved = await waitForResolvedIdentity();
  if (resolved) {
    lon = Number(resolved.longitude);   // :6028
    lat = Number(resolved.latitude);    // :6029
    if (typeof resolved.technology === 'string' && resolved.technology) tech = resolved.technology;
    if (resolved.name) name = String(resolved.name);
    const cap = Number(resolved.capacity_mw); …
    link.deep_link_identity = 'resolved-by-search-lane';   // :6037
  }
```

and then, at `:6156`:

```js
await selectAt([lon, lat], name, tech, false, …);
```

The register's coordinates are adopted **only when the URL's coordinates are unusable or its technology is
unrecognised**. A well-formed link — usable coordinates, recognised technology — skips the entire block, so
`lon`/`lat` remain the URL's while the identity lane independently resolves the register row, flies the
camera to it, and renders name, address, postcode, REPD reference and planning status from it.

**The malformed link is defended. The well-formed-but-wrong link is the only one that is not.**

The comment immediately above the arrival lane (`:5885`) states the intended rule — *"The register knows
the coordinates and technology better than any URL restatement, so when the identity lane has resolved, its
published result is the arrival."* The code honours that for technology, name and capacity, and omits it
for the coordinates. The intent is already written down; only the coordinate pair fell out of it.

---

## 4. Reachability — what I tested, and what each path does

| path | tested | result |
|---|---|---|
| **Deep link with mismatched `latitude`/`longitude`** | live, twice, `document.hidden === false` | **LEAKS.** Identity byte-identical, measurement wholly different. No console. Shareable. |
| **Console `selectAt`** | live, **5.5 ms** | LEAKS. Identity, card bar and URL all unchanged; measurement re-derives for the new place. |
| Map click on a substation | live, real `Input.dispatchMouseEvent` at the projected pixel of a rendered `l-subs` feature | **Clean.** The engine replaced the popup wholesale: identity became `Lovelace Road \| 33000` and the measurement became the projects nearest Lovelace Road. Both blocks moved together. |
| Map click on a project | source, `:5840`–`:5878` | Same mechanism as above — the engine opens its own popup, so identity follows. An engine-built popup carries no address, no REPD and no planning status at all, so the dangerous identity block exists **only** on the deep-link / search arrival card. |
| `◈ Grid At Point` (`btn-gridpoint`) | source, `:2976`, `:5563`–`:5578` | Opens its **own** `new gl.Popup`. Never touches the project card. No leak. |
| `SCOPE` chip | source, `:5594`–`:5597`, `:5864` | Same — its own popup. No leak. |
| Dragging the project marker | live DOM + source | **Does not exist.** The ring is a cartridge-drawn source (`gridatlas-project-pin`), not a draggable layer. No drag handler. |
| Editing the coordinate in the UI | live DOM | No control exists. |

Both armed chips also sit behind the zero-feature guard at `:5847` (`if (!features.length) { clearLinks(); return; }`), which is §1.5 of the scenario-sandbox scope and is unchanged.

**Conclusion: no click, drag or chip reaches the false state. The URL does.** Note also that `btn-gridpoint`
and the `SCOPE` chip are installed by `installMobileTray` (`:5496`, `:6175`) and are absent from a
1,400 px desktop DOM entirely — they are mobile-tray controls, which is worth knowing for whoever fixes this.

### How a reader gets such a URL without typing one

Pipeline News builds the Atlas link from its own row — `repd_ref`, `latitude`, `longitude` taken together
(`pipelinenews/releases/javascript/*-atlas-*-deep-link-cartridge.js`), so in the happy path they agree.
But the Atlas resolves `repd_ref` against **its own pinned register** via DuckDB, a different snapshot from
the one Pipeline News serialised into the link. Two independently pinned registers, one link. **Any
divergence between them — a corrected coordinate, a re-snapshot, a re-pointed REPD row — silently prints
one source's identity over the other source's geometry, with no warning and no reconciliation.**
I did not measure such a divergence and do not claim one exists today; I claim only that nothing in the
page would reveal it if it did, and that the same code path is what a hand-edited URL exercises.

---

## 5. Did the honesty sentences travel?

**Yes. All of them, correctly.** This is the uncomfortable part: the measurement engine's epistemics are in
better order than the identity block they sit under, and their correctness is what makes the false card
read as authoritative.

- **The corridor sentence re-derived and carried its calibration verbatim** — *"~38.0 km corridor estimate
  (×1.245, 73% of GB transmission cable circuits within 15% of published length, 59 distinct site pairs)"* —
  and re-declared its refusal: *"Calibrated on cable circuits… Overhead line crosses open country and
  measures 1.13; this factor is not applied to an overhead-line question."*
- **The word "straight" travelled**, correctly attached to the new distance: *"Feckenham Substation · 30.50
  km straight"*.
- **The scope sentence is identical in both loads, and that is correct, not stale** — *"nearest of the 278
  mapped substations at 400 kV or above that this search could see; the operator publishes 355 connection
  points at that class and 214 of them carry coordinates, so 141 cannot be measured to at all."*
  Those figures describe the **dataset**, not the location, so they must not change when the origin moves.
  I checked this specifically rather than assuming it: 214 of 355 is the coverage of the ≥400 kV pool, a
  property of the pinned register. (The ~57% figure is the *other* pool — 502 of 886 published connection
  points, 56.7% — and it belongs to `◈ Grid At Point`, which does not render into this card.)
- **The voltage-class context sentence adapted to what was actually found**, which is the sharpest proof the
  measurement half is location-aware: *"132 kV distribution in England and Wales, transmission in Scotland.
  33 kV primary distribution…"* became *"66 kV largely legacy industrial distribution, much of it being
  reinforced to 132 kV and above. 33 kV primary distribution…"*.
- The ETYS provenance, the Appendix D non-interchangeability caveat, the "ratings are not added together"
  sentence, the planned-rows disclaimer, the hop-is-not-a-distance sentence and the closing beta caveat all
  re-derived for Feckenham with their sources named.

**Nothing on the card is stale except the identity block.** Every sentence that describes the measurement is
true of the place it measured. Only the five lines that say *which project this is* are true of somewhere
else — and they are the five lines that make it a planning claim.

---

## 6. What a share carries, and what a screenshot asserts

**A shared link (the URL route).** The recipient loads the URL and the page rebuilds the false card from
scratch: same register-resolved identity, same URL-driven measurement, same Oxfordshire camera. Sender and
recipient see the same thing, and neither has any way to know it is wrong. This is the reverse of the prior
finding — the link does not heal the falsehood, it **is** the falsehood, and it is the durable form.

**A shared link (the console route).** The URL never changes — asserted: `before.url === after.url` after
the `selectAt` move. So here the recipient does load the true project, and sender and recipient see
different numbers under the same identity without either knowing. Silently divergent rather than jointly
wrong.

**A screenshot, either route.** The image asserts, in one frame and with no way to check it:

> **Botley West, Botley - Botley West Solar Project · solar · 840 MW ·
> Botley West, Botley, Oxford · OX29 4DZ · Oxfordshire · REPD 12588 · application submitted**
> — measured to **Feckenham Substation**, 30.50 km, site envelope 955–2,009 MVA, joined to NESO site FECK.

A genuine REPD reference and a genuine planning status, above a grid position belonging to a site 36 km
away in another county, on a map of the true site. That is a fabricated planning claim about a live 840 MW
application, and it is the architect's stated existential risk in one image.

---

## 7. Does anything already mark it?

**No. Nothing, on any surface.**

- `document.body.innerText.match(/scenario|hypothetical|not a record|illustrative|moved/gi)` → `[]`
- `Object.keys(__GRIDATLAS_NEON_LINKS__).filter(k => /scen|hypo|moved|dirty|provenance/i.test(k))` → `[]`
- No badge, banner, dashed ring, ghost marker or tooltip anywhere in the card.
- `link.deep_link_identity` is **`(undefined)`** on the false load — because it is set at `:6037`, inside
  the very branch the false case skips. The one published field that records where the identity came from
  is silent in exactly the case where a reader would need it.

There is nothing to un-hide. This has to be built.

The single most useful fact for whoever fixes it: **the page already holds both numbers at once.**
`__GRIDATLAS_PLACE_SEARCH__.deep_link.longitude/latitude` is `(-1.348973, 51.813209)` and the measurement
origin in `gridatlas-project-pin` is `(-1.6, 52.1)`. The mismatch is a subtraction the page can already do
and does not.

---

## 8. The minimal marking I would recommend

Not a design; the smallest set that makes the artefact non-fabricable. A separate agent implements this and
**must ask before acting** — I have changed nothing.

**8.1 — Reconcile the coordinates, and say which won.** This is the fix, and it is the smallest one. When
`repd_ref` resolves, take `resolved.longitude`/`resolved.latitude` **unconditionally**, not only when the
URL's are unusable — i.e. hoist `:6028`–`:6029` out of the `:6021` guard. Then the identity and the
measurement are always the same place by construction, and the whole URL route closes. Publish the
reconciliation either way: `link.origin_source = 'register' | 'link'` and, when they differed,
`link.origin_discrepancy_km`. This alone is worth doing before anything below.

**8.2 — When origin and identity disagree, the identity block is replaced, not badged.** For the console
route, and for any future scenario sandbox, the two lines that turn a mistake into a fabricated planning
claim are the registered address and the planning status. They must be **removed**, not annotated:

```
SCENARIO — not a record
Based on Botley West, Botley (REPD 12588)
Measured 36.2 km NW of the registered site
```

The REPD reference stays, prefixed *Based on*, because provenance is the point — but it is never again
printed as a bare `REPD 12588` beside a measurement that does not belong to it.

**8.3 — Mark the card bar too.** `.gridatlas-card-bar` still reads the true project name, so the falsehood
survives minimisation. Whatever mark 8.2 applies must reach the bar.

**8.4 — Publish a dirty flag, so a proof can assert the mark is up.** `link.scenario = { moved_km, bearing,
origin_source, identity_source }`. Without it, 8.2 rots the first time the card is refactored.

**8.5 — Make the measurement visible where the reader is looking.** The pin and all five links being
drawn 36 km off-screen is what removes the last chance of noticing. Either fit the camera to the
measurement geometry, or draw a ghost ring at the registered position with a tie line — but the reader must
never be shown a map that silently agrees with an identity the numbers do not belong to.

I would treat 8.1 as the fix and 8.2–8.5 as the marking that keeps it fixed. 8.1 alone removes the
shareable form; without 8.2 the console form remains, and it is the form the scenario sandbox will
deliberately create.

---

## Evidence in this directory

| file | what it is |
|---|---|
| `evidence/card-TRUE-coordinates.txt` | full verbatim card, register-correct coordinates |
| `evidence/card-FALSE-coordinates.txt` | full verbatim card, same `repd_ref`, coordinates moved |
| `evidence/state-TRUE.json` | camera, pin, `deep_link`, `last_selection`, identity block, `document.hidden` |
| `evidence/state-FALSE.json` | the same, for the false load |
| `evidence/false-card-screenshot.png` | the artefact as a reader would screenshot it |
| `evidence/console-move-measurement-block.txt` | measurement block after the console `selectAt` move (5.5 ms) |
