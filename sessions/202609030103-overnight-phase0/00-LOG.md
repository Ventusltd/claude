# Overnight, GridAtlas UI / composition / browser-runtime lane

Started 2026-09-03 00:50 UTC. No conversational memory; everything below was
re-derived from the repositories tonight.

---

## 0. Before anything was written: the repository was not mine alone

The first thing I did after reading the brief was `git status` in gridatlas.
The tree was dirty with a generation `202609030051` that nobody had committed.
Three minutes later the same files were `202609030052`. Three minutes after
that, `202609030053`. A second agent was live in `atlas/**` — my exact lane —
re-cutting its generation each time it recomposed.

I stopped writing and went looking. `tools/overnight/shift-log.json` ends at
2026-09-02 00:19, so it was not the overnight runner. `Get-CimInstance
Win32_Process` showed two other `claude.exe` CLI processes and an active Codex
session. That agent went on to commit and push `d20437e`, **v9.78 generation
202609030059**, "a PIPELINE NEWS (REPD) section in the layer dashboard".

Decision: do all exploratory and verification work in an isolated
`--shared` clone, and touch the real tree only to apply a verified change,
cut, and push — fetching immediately before every cut. This cost perhaps
forty minutes and it was the right trade: had I edited `atlas/current.json`
in that window I would have deleted their composition.

**Two mechanical notes for anyone repeating this.** A `git clone` of gridatlas
fails on Windows with `Filename too long` in `nightly/**`; clone with
`--no-checkout` and `git sparse-checkout set --no-cone '/*' '!/nightly'` to a
short path such as `C:/gaw`. And the proof harness's `grid-distance-maths`
parity check needs that repository as a *sibling* of the clone, so copy it
beside the clone or the harness reports a failure that is really a missing
sibling.

## 1. The baseline the brief gave me is not the number the harness prints

The brief said the harness "was 629/629 before you started". It is more
subtle than that, and it matters for every gate I record below.

`tools/proofs/run-current.mjs` prints **no grand total**. It runs one proof
per composed cartridge and each proof prints its own count; the last line you
see is simply the last proof to run. So:

- at commit `6237b20` (the brief's base) the *sld-sandbox* proof printed
  `629/629` — that is the brief's number;
- at `d20437e` (v9.78, where I actually started) it printed `638/638`;
- the *substation-intelligence* proof printed `37/37` at both.

I record every proof's count separately in `02-gates.md`. Reading the last
line as a total would have hidden the fact that I added sixteen checks and
the "total" did not move.

## 2. Generation 202609030109, v9.79 — F3, the transformer double-count

Confirmed, and the brief's file:line reference had moved. The brief named
`atlas/cartridges/202609012211-sld-sandbox-v9-8.js:1016` and
`atlas/parts/202609012350-substation-intelligence-body.js:134`. The live
arithmetic is at **`atlas/modules/202609012245-network-topology.js:294`**;
the parts reference is line **132**, not 134, and it is a *second*, different
instance of the same defect reading a figure published upstream.

Measured against `data-grid-gb/derived/gb-transmission-network.v1.json`:

```
transformers      2,944 landings -> 1,550 units   484 of 525 sites differ  1.90x
circuits          2,784 landings -> 2,638 units    78 of 636 sites differ  1.06x
planned changes   4,460 landings -> 3,696 units   282 of 645 sites differ  1.21x

COWL  10 landings -> 5 units
      COWL41<->COWL11 278 | COWL41<->COWL11 269 | COWL41<->COWL11 269
      COWL41<->COWL12 269 | COWL41<->COWL12 269
```

**Contradicts the brief on one point.** The brief (and F2/F3 in the findings)
says circuit counts are correct. They are correct at 558 of 636 sites and
*wrong at the 78* that own both ends of an internal circuit — Sellindge
reports 22 for 14. Same mechanism, smaller blast radius. I corrected all
three aggregates rather than only transformers, and said so in the commit.

**What I got wrong, twice, and what caught it.**

1. I first reached for halving — records/2 — because 95% of transformers are
   internal. Measuring it before writing it showed halving is wrong at **57 of
   525 sites** and that **24 sites publish an odd number of landings**, so
   halving invents a fractional machine. Keying the unordered node pair is
   exact and also survives a voltage-filtered query, which sees only one
   winding of an internal machine and which halving would have quartered.
2. My first implementation read the counts with `Number(units && units.circuits)`.
   `Number(null)` is **0, not NaN**, so `Number.isFinite` was true for every
   caller that passes no units — which is all of them — and a site publishing
   eight circuits reported none. The proof caught it. I had already cut the
   generation, so I unwound the uncommitted cut (renamed the proofs back,
   deleted the new cartridges and manifests, `git checkout` on current.json,
   and stripped the ledger row the cut had appended) and re-cut. Nothing was
   pushed in between.

**A third defect, found while fixing the first.** The substation-intelligence
proof hard-coded `CARTRIDGE = 202609012045-substation-intelligence-v9-63.js`
while the composition served `202609020018` — three generations later. It was
passing against bytes nobody was serving. That is the exact drift class
`run-current.mjs` and `recompose.mjs` were both written to stop, reproduced
inside a proof. It resolves its path from `atlas/current.json` now.

Live-verified: all four composed cartridges match local bytes and their
manifest hashes at `https://ventusltd.github.io/gridatlas/atlas/`.

## 3. Generation 202609030116, v9.80 — Reg1, HIDE LAYERS blanked the app

Confirmed exactly as briefed, and the shell structure is the evidence:
`.dashboard` opens at `index.html:22` and contains BOTH `.map-container`
(line 36, holding `#map`) and `.scada-wrapper` (line 112, holding the layer
keys and the legend). The control collapsed `.dashboard` to `max-height:0;
overflow:hidden`, so it took the WebGL canvas down with the checkboxes, and
the choice is remembered per browser so the reload a reader reaches for
blanked it again.

Retargeted to `.scada-wrapper`. **No fallback**: a shell that stops publishing
that wrapper gets no control at all and says so on `__GRIDATLAS_DASH__`. The
last fallback is what blanked the map.

Toggle hidden while a fullscreen element is present, because
`keepLayersInFullscreen` MOVES the layer panel into the fullscreen element and
a fixed-position button outside it acts on a node the reader is not looking at.

**One thing I nearly shipped.** My first refusal path called
`link.failures.push(...)`. `link` is declared at line 1170 and this control
runs on the way past at line ~466 — a ReferenceError at load that would have
taken the whole cartridge, not just the control. Caught by reading before
running. The proof now asserts that the control body never touches `link`.

## 4. Generation 202609030119, v9.81 — Reg2, and its real mechanism

The brief pointed at `202609011141-place-global-search-v9-5.js:497`. That is
one of three lanes involved and, on its own, not where the fix belongs.
Measured from the real bytes of all three:

- the **shell** returns at `if (!/^[A-Za-z0-9-]{1,40}$/.test(repdRef)) return;`
  inside `focusCanonicalProjectDeepLink`, **before** it reaches any `flyTo`;
- the **search lane** returns `status: 'ABSENT'` at the same test, with no
  `flyTo` before it;
- the **sandbox** then called `honourRequestedZoom(map)`, which eases the ZOOM
  and never sets the CENTRE.

So a link with coordinates and no `repd_ref` zoomed in on whatever view the map
had opened with. That is worse than not moving, because it looks deliberate.

The camera move belongs in the sandbox, which is where v9.67 already put the
arrival zoom for the same reason (the shell cannot be edited). It flies to the
link's coordinates only when `repd_ref` is absent; the identity path is
untouched, per the brief. Zoom is the link's own where usable and 12 otherwise
— the shell's long-standing hard-coded value and what Pipeline News sends — so
existing links land exactly where they landed before.

The proof establishes the premise from the other two lanes' bytes rather than
asserting it, so if either lane ever starts flying, the check fails loudly
instead of leaving two cartridges fighting over the camera.

## 5. Generation 202609030128, v9.82 — Reg3, and the brief's premise corrected

The brief said a whitelist "rejects 20 of 24 REPD categories" and asked me to
expand it. Three things are wrong with that as stated, and I could not fix the
thing it names.

**Where the whitelist is.** `allowedTechnologies = new Set(['solar','bess',
'wind_onshore','wind_offshore'])` is at
`atlas/releases/202608300453-atlas-v9/ventus-corev8engine.js:805` — the
immutable shell. `AGENTS.md` says `atlas/releases/` is immutable, and the
substation-intelligence cartridge carries that engine byte for byte as its
slot contract, asserted by its own proof. Not mine to widen.

**Widening it would change nothing a reader sees.** The product it gates,
`uk_renewables_pipeline/v9/data/v9.1/build_manifest.json`, publishes 18
`atlas_partitions` covering exactly those four technologies and declares
`scope.technologies` as the same four. A wider whitelist moves the throw one
fetch later, from "canonical project technology is invalid" to "no canonical
Landfill Gas partitions".

**The parameter never carries a raw DESNZ label.** Pipeline News sends the
normalised id — I read a real built link:
`?repd_ref=13599&project=Beacon+Fen+Energy+Park&technology=solar&capacity_mw=400&latitude=52.9989987&longitude=-0.4092339&zoom=12`.
`Landfill Gas` is a `repd_technology` value, and it normalises to `biomass`,
which the sandbox has always accepted.

I also nearly filed a false defect here. A grep for `technology=` found 229
occurrences with an empty value and I briefly believed 229 of 231 links were
broken. They are `data-technology="..."` attributes on filter buttons. Checked
the context before writing it down.

**Measured, over `data/repd_projects_202608290716.parquet` — 11,069 rows, the
REPD product this Atlas's own search lane reads:**

```
25 DESNZ categories normalise to 14 ids
shell whitelist (4 ids)      accepts  6,560 of 11,069   59.3%
                             rejects  4,509 — including all 3,397 rooftop solar
sandbox PROJECT_TECHS (18)   accepts 11,065 of 11,069   99.96%
                             rejects  4 — normalised `other`
                                        (2 "Unknown", 2 "Air Source Heat Pumps")
```

**What I fixed.** `other` is added. Far more consequentially, the guard did
`return` — abandoning the card, the project ring, the nearest-substation
measurement, the declared connection and the substation layer. All of that is
arithmetic over two coordinates and a register row; only the one technology
layer needs to know what a project generates. An unrecognised id now costs
that layer alone.

## 6. The size boundary, which cost me two re-cuts

`the sandbox cartridge is back under the 400 kB boundary with room to spare`
asserts `cartridgeSource.length < 340000`. My generations pushed it over twice.

Precedent is explicit: v9.76's own note says "the boundary refused the cut and
it was right to. Raising it, or leaving the module uncomposed and calling the
version shipped, were both available and both rejected." So I did not raise it.
I trimmed 1,661 characters of my own commentary at v9.82 and another 804 at
v9.83, and at v9.83 I moved the new code into a module composed into
`substation-intelligence`, which has 200 kB of headroom, instead of into the
sandbox.

Growth since the guard was set is not all mine: v9.78's `pipeline-news-layers`
module is 479 lines. **The sandbox cartridge is at 339,367 characters against
a 340,000 guard.** Anything card-facing tomorrow needs headroom made first, and
the only sanctioned way to make it is to move a block into the sibling
cartridge — as v9.76 did and as v9.83 did.

## 7. Generation 202609030137, v9.83 — F5, and the collision it was about to cause

The coordinator was right to make this urgent. Codex has committed `b91e45b`
on `codex/20260903-phase0-integrity` in data-grid-gb. I read both products
(read-only) and diffed them:

```
                        main 1c9909d      codex b91e45b
schema        data-grid-gb.connection-points.v3   IDENTICAL
points                       886                886
located                      502                489
COWLEY transformers           10                  5
ABHAM  transformers            4                  2
```

Every one of the 886 records differs, under an unchanged schema string. The
Atlas fetched that file from `main`. So a published, immutable Atlas release
was one merge away from halving a number on its card with none of its own
bytes changing — and v9.79's client-side deduplication would have been applied
to a figure that no longer needed it.

Three products, all from `main`, all now pinned to a commit **and** hashed:

```
connection-points.v3.json         1c9909d1138704b2…  11e28859…  2,896,561 B
gb-transmission-network.v1.json   1c9909d1138704b2…  fc331cc2… 10,069,966 B
price-decade-rollup.json          d310e3cec8cd14bc…  18da5059…      6,873 B
```

All three URLs were fetched and hashed before the cut and serve exactly those
bytes.

The table lives in one module in `substation-intelligence`, which the shell
evaluates before the sandbox — the same route the geodesy module already
takes. A digest that disagrees refuses. An absent WebCrypto (any non-secure
context) reports unverified and still reads the product, because refusing on
absence would make the Atlas unusable outside production while proving nothing.
The proof exercises **both**: the pin table runs in its own context with real
WebCrypto so the MISMATCH path executes, while the cartridge's fixture context
has none and proves the unverified path still loads.

**Pinning strands Codex's correction, and that is deliberate.** It is stated in
the cut message and in the module: the correction does not reach a reader until
a human moves the pin, which is one file and one cut. The alternative is not
knowing which of the two numbers is on the card.

## 8. `loop.mjs state --stdout` — a governance check that could not fail

Codex's audit flagged that a read-only helper rewrote `STATE.md`. It is worse
than that. `tools/scope/loop.mjs` reads only `process.argv[2]`, so `--stdout`
was never implemented — it was silently discarded and the command took its
ordinary path, which writes the file.

`AGENTS.md` step 2 of the handover contract says: "Prove `node tools/scope/
loop.mjs state --stdout` exactly matches STATE.md." **That check could not
fail.** I proved it: put the single line `DELIBERATELY WRONG` in STATE.md, run
the command, and the file comes back correct. A drifted STATE.md was repaired
by the check that existed to detect it, and the operator saw a match every
time.

Fixed in `4b1641e`: `--stdout` renders to stdout and writes nothing, the
ledger line moves to stderr under that flag so the stream can be diffed
directly, and an unrecognised flag exits 1 rather than being ignored. The same
experiment now leaves `DELIBERATELY WRONG` on disk and the comparison
disagrees.

## 9. The gate I was running was not the gate — five red CI runs

The coordinator stopped me. `202608312212 GridAtlas cartridge proof` had been
**red since v9.79** while my local run was green every time.

I caused it, at v9.79, and the cause is the shape this repository keeps
finding: the checks I added resolve the published product by probing for a
neighbouring `../data-grid-gb` checkout. My machine has that neighbour. The
runner checks out `gridatlas` and `grid-distance-maths` and nothing else.

Confirmed from the Actions API rather than reasoned about — v9.79
(`ac810d6`), run `33702626898`, job `proof`:

```
    success   The composition matches what is declared and hashed
    FAIL      The composed cartridge passes its own proof
    skipped   The scope ledger and workflow budget still hold
    skipped   STATE.md was regenerated before it was committed
    skipped   No CRLF survives in a tracked text file
```

Reproduced locally in the runner's shape — a fresh `--shared` clone at
`C:/gaw`, `grid-distance-maths` beside it, no `data-grid-gb`:

```
  [FAIL] the published node/branch product is on disk for a real-data check
  59/60 checks passed
```

**The worse defect was underneath it.** The eight real-data checks were
guarded by `if (topologyModule && PRODUCT_FILE)`. With the product absent they
did not fail — they did not run. *"Cowley reports FIVE transformers, not ten"*
had never executed on a runner in its life. And because `run-current` exits at
the first failing proof, the 667-check sandbox proof behind it never ran there
either. A missing input that makes a proof **quieter** is worse than one that
makes it red, because a red is visible. That is the same lesson as the
`--stdout` finding two hours earlier, in a different file, and I walked into
it myself in between.

**What I nearly did wrong.** My first fix was to add a `data-grid-gb` checkout
to the workflow. The coordinator refused it, correctly: an `actions/checkout`
at a branch is a mutable edge, and I had spent the previous generation
removing the last of those. I reverted it. The amended instruction allowed a
*pinned* checkout, but by then the better answer was already working — read
the product **through the pin the composition declares**, which needs no
workflow change at all and exercises the pin end-to-end.

A neighbouring checkout is used only when its bytes hash to the pinned digest
and match its recorded length; otherwise the pinned URL is fetched, which is
what the runner does and what the Atlas does. Neither available means every
dependent check fails with the reason.

## 10. Three more defects fell out of fixing that one

- **`bytes_seen` counted characters.** My own module reported `text.length`,
  which is UTF-16 code units. The node/branch product is **10,069,964
  characters and 10,069,966 bytes**, so a completely correct file disagreed
  with its own recorded length by two.
- **A short response and a wrong one now read differently.** Truncation is
  what a length names immediately; a digest only says "different".
- **The proof's fixture had drifted from the product it was copied from.** The
  hand-written stub claimed Cottam's winter range as **2,780–3,326 MVA**; the
  product publishes **2,009–3,326**. That check had been passing against a
  minimum nobody serves. The loader now runs against the pinned product itself
  — 886 points, 502 located — so the summariser is measured against what ships.

That last one is the argument for the whole change, made by accident: a
fixture is a shape somebody wrote, and it rots quietly.

## 11. Standing corrections to how I was working

- **A local proof run is not a gate.** From v9.84 the gate is the CI
  conclusion for the pushed commit, polled from
  `/actions/runs?head_sha=<sha>`. v9.84 is run **33705373009**, `success`,
  with every step green including the four that had been skipped behind the
  failure since v9.79.
- **Every generation must restamp `sld-sandbox`.** Its proof derives the
  generation from its own filename and asserts the composition manifest
  matches. A cut that restamps only `substation-intelligence` fails three
  manifest-identity checks. Found by doing it.

## 12. Generation 202609030156, v9.85 — headroom, made the sanctioned way

The three remaining features were all card-facing and the sandbox had about
600 characters of room. Raising the guard was available and was rejected, as
it was at v9.76 and at every cut tonight.

The `VERSION_LEDGER` was **13,657 characters of pure data** sitting in the
cartridge with the least room, and every cut appends another row to it. It
moved to a module composed into `substation-intelligence`, which the shell
evaluates first — the same route geodesy already takes. The sandbox reads it
under the same name, so no reader below it changed, and falls back to an empty
ledger the panel reports rather than a throw that would cost the session.

```
sandbox cartridge   339,367 -> 326,331 characters
                     84.8%  ->   81.6% of the 400 kB boundary
```

**A comment a tool reads is code.** My first version of the module header
quoted the declaration it was describing — `const VERSION_LEDGER = [` — and
`tools/recompose.mjs` scans part files for exactly that literal when it appends
the row for a cut. It found my comment before it found the data and tried to
`JSON.parse` an English sentence. The cut died with `SyntaxError: Unexpected
token '`'`. Reworded; the module now matches that regex exactly once, verified
by counting the matches rather than by reading it again.

## 13. Generation 202609030200, v9.86 — F4, and the two denominators

"Nearest 400 kV substation: Cowley · 15.76 km" is nearest among what the search
could see, and the card said nothing about that. Two different limits, and the
brief named only one of them:

- **the search itself.** `nearestTransmission` runs over the substation
  features the MAP has loaded, not over the published connection points. So
  the first denominator is how many features were actually eligible. It is
  counted inside the loop whose predicate decides eligibility, because a
  second implementation of that predicate in a caller would drift from it.
- **the published list.** ETYS names substations and does not place them, so
  the geometry comes from OpenStreetMap through a GridAtlas release.

The second is computed at runtime from the fetched payload, using exactly the
predicate `state.nearest` uses, so the denominator on the card is the
denominator of the search. Against the pinned product it reproduces the
finding's figures exactly, without either being written down:

```
at 400 kV       214 of 355 published carry coordinates, 141 cannot be measured to
whole product   502 of 886
```

**No coverage figure is a literal anywhere in the served bytes.** The proof
asserts that none of 214, 355, 141, 502, 886, 384, 489 or 206 appears outside a
comment, and that all four printed numbers are template interpolations. The
voltage class stays a literal, because 400 kV is what the search asked for
rather than something it counted — my first version of that check was blunter
and failed on exactly that, which is how the distinction got made explicit.

This matters more than the usual tidiness argument: Codex's correction, waiting
behind the pin, takes located points from 502 to 489 on its own. A sentence
with a number typed into it would have gone quietly false the day the pin moved.

## 14. The GitHub API budget is a shared, hard constraint

I burned the unauthenticated 60/hour to zero polling CI, and the coordinator
reports a `globalgrid2050` gate skipped a check as a result. That is my cost
imposed on another lane.

The limit is **per IP**, and four agents plus the estate's own gates draw on
the same pool. `git fetch` and `git push` do not touch it; only the REST API
does.

Protocol from here, and it should be the standing one: query the free
`https://api.github.com/rate_limit` first, never sample below 25 remaining,
and poll **once per cut, not once per curiosity**. My earlier loop of twelve
polls at 25-second intervals per generation was the whole problem — four
generations of that is the entire hour's budget.
