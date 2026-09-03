# Prior art — the GridAtlas grid engine, as reached by the Pipeline News MAP button

**Scope.** One code path: a reader clicks **MAP** on a Pipeline News row → arrives in the
GridAtlas Atlas by deep link → the grid engine measures nearest substations and nearest
400 kV and draws the neon links on a card.

Built by a full programmatic sweep of the cross-session memory store
(`logs/parquet/*.parquet`, 30,684 rows, 11 sessions, 2026-08-30 to 2026-09-03), checked
against the live repositories at `202609031318 UTC`.

---

## THE ONE THING TO READ FIRST

> **The compute was already technology-agnostic, and the "unchecked layers" hypothesis is
> already disproved in the shipped code. Both were settled before this investigation
> started.**

Three independent confirmations, each from a different direction:

1. **The engine measures first, on purpose, and the layers are not in the path.** Shipped
   as v9.54 on 2026-09-01 and still the live code today
   (`atlas/parts/202609012045-sld-sandbox-body.js:4124`):

   > *"Measure first. The distances are arithmetic over substation coordinates and need no
   > layer control, no dashboard and no painted basemap; only the layers need the engine's
   > controls. Until v9.54 this awaited arrive() - up to twelve seconds - before the
   > measurement was even attempted."*

2. **The wider fleet was measured working before anyone changed anything.** Driven in
   Chrome against live v9.88 by the concurrent lane
   (`atlas/modules/202609031310-technology-coverage.js`, header):

   > *"Both arrived, flew, opened the card, ticked the Subs control and DREW THE LINKS.
   > Caledon Green measured 1.74 km at 132 kV, 2.98 km at 275 kV and 5.70 km at 33 kV …
   > So the wider fleet was ALREADY computing, and a change that claimed to enable it
   > would have been a change that did nothing while saying it did something."*

3. **The four-technology allow-set that looks like the culprit is inert.** Same file:

   > *"It lives at line 805 of the IMMUTABLE SHELL … Its rejection is caught, and its only
   > effects are a console line and a flyTo the arrival lane in this cartridge has already
   > performed - **which is why the measurement runs anyway.** The shell is carried forward
   > verbatim by contract and this module does not reach into it."*

A fourth, from the Pipeline News side of the same fault
(`bbe4731a`, 2026-09-03 01:03:39):

> *"The neon-links lane measures straight off the link's lat/long — no register, no camera
> — which is why the numbers were right while the view was wrong."*

**Consequence for the live investigation.** If a measurement is missing, unchecked layer
controls are not the cause, and neither is the technology value. Those two doors are
closed and were closed deliberately. Look instead at: the substation payload failing to
arrive (`link.substations_qualifying === 0` means *the payload did not arrive*, not *the
map is empty here*), the popup watcher wiping links when no card stands (v9.50), or
identity resolution.

---

## Method, and what fraction of the record was examined

| pass | rows | share | how |
|---|---:|---:|---|
| full corpus scanned programmatically | 30,684 | 100% | every row read by script for vocabulary, capability, ledger and term-lift extraction |
| broad relevance filter (map / grid / atlas / substation / REPD / deep-link / layer / cartridge) | 9,347 | 30.5% | 20.1 MB of the 22.3 MB of content |
| tight arrival-path filter | 2,286 | 7.4% | 10.1 MB — read or excerpted |
| withheld by the store's sensitivity rule | 1 | 0.003% | `opinion_about_person`, a cvaa vaccine spec, not on this path |

**Exclusion rule.** The 69.5% outside the broad filter were still scanned by script; only
their *content* went unread. They concern other repositories — `companies`,
`data-centres-gb`, `cvaa`, GB price data, the CI/CD spider, the email storm — and contain
no reference to the map, the register, the arrival or the measurement.

**What the full sweep found that the supplied keyword list would have missed.** The brief's
eighteen capability names all exist in the record and all resolve — but they are a subset.
Deriving the vocabulary from the data instead surfaced the things that actually decide the
question:

- **`VERSION_LEDGER` / commit-subject chronology** — 52 ledger generations and 61 commit
  subjects, v9.16 → v9.89. This is the record-of-record for this path and no keyword in the
  brief would have reached it. It is what proves v9.81 and v9.82 closed the two P1s that
  the most recent curated findings file still lists as OPEN.
- **`allowedTechnologies`** — the actual four-member allow-set, its real home in the
  immutable shell, and the finding that it is inert. Not in the brief's term list.
- **`atlas/modules/202609031310-technology-coverage.js`** — uncommitted when this sweep
  began, committed at `202609031316` during it. The single most relevant artefact in the
  estate, and it did not exist when the brief was written.
- **`contracts/atlas-v9-deep-link-contract.v1.json`** — the canonical contract, stale since
  2026-08-30. A divergence, below.
- **502 → 489 / 886** — the real arithmetic behind "~57%", and the instruction not to
  hardcode it.
- **`dist/repd_master.json` is not a served file** — a 404 that has bitten this path twice.

---

# 1. SOLVED — do not rebuild

Anything here recurring is a **regression**, not new work.

| # | what was solved | version / gen | landed | evidence |
|---|---|---|---|---|
| S1 | **A third of the register had a dead MAP button.** | v9.27 · `202608312257` | gridatlas | commit subject, `0e09c52a` 2026-09-01 13:11: *"a third of the register had a MAP button that did nothing"*. Code: *"2,399 onshore wind projects and 109 offshore, so 2,508 of 7,680 — a third of the register — had a MAP button that did nothing at all. Not an error, not a message, nothing."* |
| S2 | **A `repd_ref`-only link now computes the links.** Identity resolved by the search lane is consumed, not re-required from the URL. | v9.44 · `202609011141` | gridatlas | `fe663175` 2026-09-01 12:42: *"Vikram's phone: 'doesn't auto compute the neon lines on mobile'. Reproduced identically in desktop Chrome with ?repd_ref=12588 alone … The URL shape, never the device."* |
| S3 | **Late layer controls are used, not abandoned.** The 12 s budget no longer gives up permanently. | v9.26 · `202608312244` | gridatlas | `fe663175` 2026-08-31 23:49: *"Late is not never. The deep link waited twelve seconds for the engine's layer dashboard and then gave up permanently. That budget is always the wrong number - the dashboard has been measured arriving in two seconds and not arriving at all in eighty-six."* |
| S4 | **The identity wait runs to a terminal state, not a budget.** | v9.45 · `202609011205` | gridatlas | `fe663175` 2026-09-01 13:05: *"The v9.44 identity wait had a fixed 120s budget; a cold phone boots the 35.7 MB query engine first and exceeded it, so the lane gave up permanently."* |
| S5 | **The arrival card precedes the lines.** A register-absent arrival drew links, then opened its card, and the popup watcher wiped them. | v9.50 · `202609011251` | gridatlas | `fe663175` 2026-09-01 13:51: *"five links drew and the popup watcher - whose invariant is that the lines belong to the card - wiped them in the same breath, because the fallback card was opened after the measurement while no popup stood."* |
| S6 | **Nearest 400 kV is measured for every project.** | v9.51 · `202609011433` | gridatlas | ledger `dfac5e26`: *"the 400 kV public record: declared DCO connections drawn and carded, new customer substations named, nearest 400 kV measured for every project"* |
| S7 | **The measurement no longer waits for the layer controls.** West Burton went ~20 s → ~6 s. | v9.54 · `202609011612` | gridatlas | `fe663175` 2026-09-01 17:12 — full quote in the headline above. |
| S8 | **A recovered failure is no longer reported as a failure.** Late-arrival entries move to their own ledger once controls arrive. | v9.52 · `202609011434` | gridatlas | `fe663175` 2026-09-01 14:55: *"entries like 'subs: control not found' stayed in the public failures array after the late controls arrived and were switched on, making a recovered event indistinguishable from a terminal fault."* |
| S9 | **The grid maths installs even when the basemap never paints.** | v9.19 · `202608312154` / v9.34 · `202608312324` | gridatlas | ledger: *"the grid maths installs even when the basemap never paints"*; commit: *"the cartridge now boots on the style rather than on a painted frame, precisely so it can work when the basemap does not - which it did not, all night, on this estate."* |
| S10 | **Grid and subs are one tap on mobile.** | v9.43 · `202609010902` | gridatlas | `fe663175` 2026-09-01 10:02: *"the switches that turn the grid lines and substations on live below the map where a phone never looks."* |
| S11 | **Pipeline News' MAP link carries a REPD reference.** `repd_master.json` had no ref field at all; without it MAP had no identity. | `202609030009-pipelinenews` | pipelinenews | `bbe4731a` 2026-09-03 01:36: *"One cause, two symptoms: blank REPD REF / GLOBALGRID REF columns, and a MAP link with no identity for the Atlas to resolve. An earlier note in this session explained the blank columns as 'spine joins withheld' — that was wrong."* 1,091 of 1,104 (98.8%) resolve. |
| S12 | **A link with coordinates and no identity moves the camera.** Closes the P1 that `bbe4731a` left open. | **v9.81 · `202609030119`** | gridatlas `f1f430d` | Code at `:4058`: *"A link with coordinates and no repd_ref moved nothing. The shell returns at its repd_ref pattern test before reaching any flyTo, and the search lane returns `status: 'ABSENT'` at the same test, so both lanes that own the camera stood down."* |
| S13 | **An unknown technology costs one layer, not the whole arrival.** Closes the other P1 `bbe4731a` left open. | **v9.82 · `202609030128`** | gridatlas `52ebabc` | Code at `:4080`: *"An unrecognised technology used to abandon the whole arrival. `return` cost the card, the ring, the nearest-substation measurement, the declared connection and the substation layer - all arithmetic over two coordinates and a register row. Only the one technology layer needs the id, so that is all it costs now. PROJECT_TECHS accepts 11,065 of the 11,069 ids the register writes."* |
| S14 | **The nearest superlative carries the sample it was drawn from.** | v9.86 · `202609030200` | gridatlas `97d3ffc` | see C1 |
| S15 | **A straight line is not a route; the corridor estimate sits beside it.** | v9.87 · `202609030233` | gridatlas `1fb6262` | see C4 |
| S16 | **The technology vocabulary no longer decides alone — the engine is the authority.** | v9.82+ | gridatlas | Code `:157`: *"The register writes `wind_onshore`. The engine has had a `wind_onshore` layer the whole time. Only this list disagreed with both. So it no longer decides alone … anything the ENGINE has a layer control for is accepted too."* |
| S17 | **Offshore measures instead of withholding, and the wider fleet was confirmed already computing.** | **v9.89 · `202609031313` / `202609031316`** | gridatlas (committed during this sweep) | `atlas/modules/202609031310-technology-coverage.js` — quotes in the headline and in C7. |

**Also solved, method rather than product** — these cost hours each and are recorded so they
are not paid for twice:

- **Driving MapLibre in a backgrounded tab.** `requestAnimationFrame` never ticks, so
  `map.on('load')` never fires. Screenshot-pumping does **not** fix it; a `setInterval`
  calling `m._render(0)` does. `window.map` is the `<div id="map">`, not the map.
  (`202609021813/02-measurements.md`, "Method note".)
- **`dist/repd_master.json` is not a served file.** *"Fetching it 404s on the live host and
  in a local checkout alike -- measured both ways -- because the streaming bridge
  reconstructs the register from parquet and hands it straight to MapLibre."*
  (`atlas/modules/202609030048-pipeline-news-layers.js`.)

---

# 2. CONSTRAINTS — do not violate

Each carries its reason, because a constraint without its reason gets removed by the next
person who finds it inconvenient.

### C1 · Every superlative carries its sample, and the denominator is computed at render time

> *"EVERY SUPERLATIVE CARRIES ITS SAMPLE. 'Nearest 400 kV substation' is nearest among what
> this search could see … Both numbers are COMPUTED at render time from what was fetched. A
> literal would go quietly false the day the pinned product moves - Codex's join correction
> alone takes located points from 502 to 489 - and a stale denominator under the word
> 'nearest' is worse than none. **It states the sample. It does not grade the result.**"*
> — `atlas/parts/202609012045-sld-sandbox-body.js:307`

**Why.** The upstream product is mutable and the Atlas fetches it from `main` with no cut
in between. The instruction was explicit (`5b94bee7`, 2026-09-03 02:14:58):

> *"**DO NOT HARDCODE THE COVERAGE NUMBERS.** Codex is about to change them under you, and
> the Atlas fetches that product from mutable `main` … You would ship a page that silently
> starts lying. **Compute the coverage from the product you actually fetched, at runtime,
> and render the number from that.**"*

### C2 · The ~57% is 502 of 886, and it is a real blindness, not a caveat

> *"Out of 886 published NESO connection points, only 502 (56.66%) possess verified
> geographic coordinates. 384 connection points (43.34%) are completely unlocated …
> **Voltage Blindness:** At 400 kV, 141 out of 355 substations (39.7%) have no coordinates …
> Stating 'Nearest 400 kV substation: Cowley · 15.76 km' is mathematically false. It is
> nearest among the 60.3% of 400 kV sites with coordinates."* — defect F4, `5b94bee7`
> 2026-09-03 02:13:58

Enforced in the proof: *"it says a nearer one may exist rather than implying none does"*
(`tools/proofs/202609031316-sld-sandbox.proof.mjs:2575`).

### C3 · Nothing is graded, ever — and this is machine-enforced

`tools/proofs/202609031316-sld-sandbox.proof.mjs` greps the **served bytes**:

```
check('the card still refuses to grade the result',
  !/\b(STRONG|REMOTE|EXCELLENT|POOR|FAVOURABLE)\b/.test(cartridgeSource));
check('it states the sample and grades nothing', … !/\b(good|poor|strong|weak|excellent|
  limited|well.connected|constrained)\b/i …);
check('no verdict language decorates the record', !/STRONG|REMOTE|well.placed|ideal|advantage/…);
```

**Why the gate greps source rather than rendered output**, stated in the coverage module:

> *"No verdict word appears anywhere in this module, not even to disown one: the sandbox
> proof greps the served bytes for them and cannot tell a comment from a card, **which is
> the right way round.**"*

So: do not write `STRONG`, `REMOTE`, `well-placed`, `ideal`, `advantage`, `headroom` into
this cartridge — **not even inside a comment explaining that you must not**.

### C4 · A straight line is not a route; the corridor figure is additive and cable-only

> *"ADDITIVE. The straight-line distance is unchanged, still first, still the measurement;
> the corridor figure sits beside it and is labelled an estimate every time it appears.
> **Only for a CABLE question.** The factor is calibrated on cable circuits, which follow
> the highway network; overhead line crosses open country and measures 1.13. The module
> publishes that number and **deliberately offers no forOverhead()**, so this cannot
> quietly become the answer to a question it was not measured on. Under about a kilometre
> the module withholds the estimate rather than scaling."*
> — `atlas/parts/202609012045-sld-sandbox-body.js:324`

And the top-of-file statement of what a line is not:

> *"A straight line to mapped geometry. Not a cable route, not a connection length, no
> wayleave, crossing, terrain or consent content. A mapped substation does not confirm
> capacity, voltage suitability or connection rights, and fault level and thermal headroom
> cannot be inferred from distance at all."*

### C5 · Scope never implies capacity

> *"'When you click on a blank space, the user should be able to see grid in the vicinity.
> Call it the GRID FINDING SCOPE — analysis of what is there, **NOT indicative of
> capacity**.' — Vikram, 2026-09-01 … It does not say whether a connection is available,
> likely, cheap or possible. Nothing in a payload of substation positions can support any
> of that: capacity depends on queue position, committed connections, thermal and fault
> headroom, consent and commercial terms, and none of those is a distance. **A scope that
> counted substations and implied opportunity would be the most dangerous thing this estate
> could ship, because it would look like analysis.**"*
> — `atlas/modules/202609012040-grid-scope.js:1`

### C6 · The measurement is independent of the layer controls — by design

See the headline. The corollary a future agent must not undo: **do not reintroduce an
`await` on the layer controls before the measurement.** The layer switch-on runs alongside
and finishes whenever the engine is ready.

### C7 · No onshore-only filter, because the data cannot support one

> *"The OSM `location` tag - the field that would say offshore, platform or underwater - is
> present on ZERO of them … Fourteen features carry 'offshore' in their name; read against
> their coordinates, at least four are ONSHORE substations serving an offshore wind farm …
> So a name filter would drop Hornsea - a landfall connection - from the very search it was
> supposed to sharpen. **A filter whose predicate is wrong four times in fourteen is worse
> than no filter, because it looks like precision.**"*
> — `atlas/modules/202609031310-technology-coverage.js`

The coordinator **asked for** this filter and it was refused with measurement. Do not
re-request it without new data.

### C8 · The lines belong to the card

> *"When the card closes, they go with it -- leaving neon on the map with nothing explaining
> it is how a screenshot ends up quoted without its caveat."*
> — `atlas/parts/202609012045-sld-sandbox-body.js:4064`

This invariant is why S5 was a bug: it is load-bearing, not incidental.

### C9 · Identity is the REPD reference and nothing else

`state/live-set.json`: `"identity_rule": "EXACT_REPD_REF_ONLY"`, golden sentinel Beacon Fen
`13599`. The contract adds `"name_is_identity": false`, `"coordinates_are_identity": false`.
Coordinates move the camera (S12) but never establish identity.

### C10 · The 13 unresolved wider-fleet rows carry no ref rather than a guess

> *"The 13 that do not -- 11 absent from the CSV, 2 ambiguous -- carry no ref and link
> without one: card and measurement still work, only the camera does not move. **A guessed
> identity would point the Atlas at a different project.**"* — `bbe4731a` 2026-09-03 01:10

### C11 · The immutable shell is carried forward verbatim, and slots are what `index.html` loads

> *"The composer replaces a script TAG, so the only slots that exist are the four the shell
> loads, and that file was an orphan: the map went dark and v9.58 restored it."* — v9.59,
> `fe663175` 2026-09-01 18:02. v9.57 claimed a slot on the strength of a **directory
> listing**; the map went dark in production. **Rollback by composition, never by repair.**

### C12 · Borrow the styling, never the attribute another owner dispatches on

> *"The engine delegates a `change` listener on #scada-ui-container … and any checkbox
> carrying `data-layer-id` is routed to its own handleLayerToggle -- which would be handed
> an id it has no config for. These controls carry `data-pn-layer` instead … Same lesson as
> the wider-fleet tabs in Pipeline News."*
> — `atlas/modules/202609030048-pipeline-news-layers.js`

Related and paid for twice: replacing `.gauges.innerHTML` in Pipeline News destroyed nodes
the spine holds references to — *"Caught by clicking, not by reading."*

### C13 · Proximity is never an offer

Proof check: *"proximity is still not a connection offer, for any technology"* against the
string *"not a connection, a capacity, a queue position or an offer"*.

---

# 3. OPEN / UNKNOWN

### O1 · A plain map click still does not enable the substation layer — **verified open today**

`bbe4731a` (2026-09-02) recorded it as an observation, not a fix:

> *"`enableSubstationLayer()` has exactly two call sites — `runDeepLink` and
> `openSldFromProject`. Neither is the map-click selection path. Reproduced: clicked Mynydd
> Gorddu Wind Farm on the map → `last_selection` set, 5 links drawn,
> `substation_layer_enabled: false`, `l-subs` still `none`. **Links drawn to invisible
> substations.** Not wind-specific — holds for every technology. Possibly deliberate.
> Flagged, not fixed."*

**Checked against current code (`202609031316`):** call sites are now `:4111` (deep link)
and `:5362` (`openSldFromProject`) plus the definition and an exposed API handle. The
map-click path still does not enable it. **Still open, unchanged.** The record does not say
whether it is deliberate.

### O2 · The canonical deep-link contract is stale — **divergence found**

`contracts/atlas-v9-deep-link-contract.v1.json`, untouched since commit `5819ffc`
(2026-08-30), still declares:

```json
"identity": { "required": ["repd_ref", "technology"],
              "technology": { "allowed": ["solar","bess","wind_onshore","wind_offshore"] } }
```

The implementation as of v9.89 measures for **all** technologies, accepts nine bucket
values from Pipeline News including `biomass`, treats an unknown technology as
non-fatal (S13), and moves the camera on a link with **no** `repd_ref` (S12). **The engine
is now more permissive than its own published contract.** Either the contract should be
widened to match, or the implementation is out of contract. The record does not say which
was intended — no session addresses the contract file after 2026-08-30.

### O3 · A shipped capability string contradicts the shipped behaviour — **divergence found**

`atlas/manifests/202609031316-composition.json` (the newest, committed) still declares:

```
offshore-opens-a-card-and-withholds-the-measurement
```

while the code composed into that same cartridge says *"OFFSHORE MEASURES NOW"* and
*"OFFSHORE WIND NOW MEASURES"*. The capability list also does not mention the
`technology-coverage` module. Cheap to fix, and worth fixing: this estate treats the
capability list as an interface, and the Pipeline News harness
(`tools/intelligence/202609030132-verify-wider-fleet-deep-link.mjs`) reads composed
cartridges for exactly this kind of declaration.

### O4 · The inert allow-set in the immutable shell

`allowedTechnologies` at line 805 of
`atlas/releases/202608300453-atlas-v9/ventus-corev8engine.js` rejects every wider-fleet
value. It is **harmless today** — its rejection is caught and its only effects are a console
line and a redundant `flyTo`. But it is in an immutable release, so it cannot be edited;
it can only be superseded by a new shell release. The record states the position clearly
and does not propose changing it. The Pipeline News board entry `1a9868e` (2026-09-03
02:34) hands three facts to the GridAtlas lane:

> *"no Pipeline News release has ever emitted technology=Landfill Gas; the allow-set's four
> members are exactly the four technologies the wider fleet is defined as excluding, so all
> 1,104 links fail by construction whatever value this side sends; and there is now a
> harness here that reads the composed allow-set and fails when it rejects us."*

That harness is expected to keep failing while the shell is immutable. **The record does not
say whether that failure has been accepted as permanent or is still considered a defect.**

### O5 · Governance items, the architect's call alone (from `bbe4731a`)

- Three published Pipeline News releases unlisted on the homepage (`202609021945`,
  `202609022308`, `202609030009`); newest named is `202609020611`. *"Naming a release there
  is a governed act."*
- `releases/current-v3.json` still points at `202608291447`.
- `202609021945` carries a **forward-dated generation** and *"will not satisfy cvaa's
  monotonic-utc-generations vaccine"*.

### O6 · Where the record is genuinely silent

- **No end-to-end timing measurement of the current arrival exists.** v9.54/v9.55 measured
  ~20 s → ~6 s for West Burton on 2026-09-01. Nothing since v9.55 re-measures arrival
  latency, and eleven generations have shipped since.
- **The token-matched half of the ETYS→OSM name join was never hand-sampled.** It was
  handed out as a task: *"`exact_name` 486, `distinctive_tokens` 88, `unlocated` 312 of 886.
  Sample the token-matched 88 by hand. How many pair a substation with an unrelated site
  that shares a place name? What is the false-positive rate?"* (`fe663175` 2026-09-01
  18:17). Codex's later correction rejected 16 unsafe bindings and gained 3, but the record
  does not show the 88 being sampled.
- **The declared-connections table is hand-curated** — roughly a dozen REPD identities with
  Order citations, inside the cartridge. Verification against the made Orders was requested;
  the record does not show it completed.
- **Whether O1 is deliberate.** Flagged twice, never decided.

---

# 4. Materially important, outside the strict brief

Kept because the architect's concern is fragmentation, and discarding these would be the
loss they are trying to stop.

- **The estate ships one geodesy.** v9.66/v9.67 unified every distance onto
  `atlas/modules/202609011950-geodesy.js`, *"so every version ever shipped returns the same
  distance to the last digit"*, after two implementations coexisted in one cartridge. Do
  not add a second distance function; `nearest()` owns its distance.
- **Two `v9.40`s once existed simultaneously** (Claude's and Codex's, cut from v9.39 within
  the same hour) and were absorbed into v9.41. Generation stamps must be **read from the
  clock**, not typed — v9.68's stamp sorts before its own parent because the parent's name
  was typed four hours ahead.
- **A proof that passed while production was broken.** v9.77 / Codex stop-ship
  `202609020030`: *"The first proof passed while production was broken because it chose a
  connected slack by hand and the caller chose the first lexicographic bus; the successor
  proof runs the production path itself."* A proof must run the production path.
- **`Math.max` over `NaN` survived a voltage floor** (v9.64): *"NaN < floor is false, so a
  substation whose voltage did not parse SURVIVED a 132 kV floor and was censused as though
  it qualified."*
- **Magnitude is not a unit** (v9.32): a railway third rail showed as a 750 kV substation
  because the parser guessed volts vs kilovolts from the size of the number. OSM `voltage`
  is in volts at every magnitude.
- **The Pages deploy jam is three gates deep, not one line** — 25 consecutive failed
  deployments stranded 138 commits and left the site five days stale, because
  `build-pages.py` required `pointer_commit` to be `HEAD` rather than an ancestor.

---

## Verification notes

Everything in §1 marked with a code line, and every quote in §2 sourced to a file path, was
read from the working repositories at `202609031318 UTC`, not from the record alone.
Items sourced only to a transcript timestamp are `RECORD ONLY, UNVERIFIED` unless a file
path accompanies them. The three divergences (O1, O2, O3) were each found by checking the
record against current code and are the most actionable output of this pass.

`gridatlas` HEAD at time of writing: `ed2135f`, `atlas/current.json` generation
`202609031316`, sld-sandbox v9.89.
