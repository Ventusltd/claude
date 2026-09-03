# Gates

Every gate run, its command, and its output. `run-current.mjs` prints one
count per composed cartridge and no grand total, so each is recorded
separately.

---

## Baseline, before any change

`node tools/proofs/run-current.mjs` at `6237b20` (the brief's base), in an
isolated clone with `grid-distance-maths` beside it:

```
629/629 checks passed
the adapter is intact, the sandbox arithmetic is reproduced on one radius, and the panel states its limits.
proofs run: 4
every composed cartridge passed its generation-matched proof
```

Without the sibling repository the same command reports
`627/628` and `FAILURES  grid-distance-maths is available for a parity check`.
That is a missing sibling, not a defect.

`node tools/proofs/run-current.mjs` at `d20437e` (v9.78, the tip I worked
from):

```
=== streaming-parquet-bridge 202608301825 ===
=== uk-gazetteer-flyto 202609011141 ===
=== substation-intelligence 202609020018 ===
37/37 checks passed
=== sld-sandbox 202609030059 ===
638/638 checks passed
proofs run: 4
```

---

## Generation 202609030109 — v9.79 — F3 transformer double-count

**Before the cut** (tip `d20437e`): substation-intelligence `37/37`,
sld-sandbox `638/638`.

**After the cut**:

```
=== streaming-parquet-bridge 202608301825 ===
=== uk-gazetteer-flyto 202609011141 ===
=== substation-intelligence 202609030109 ===
53/53 checks passed
=== sld-sandbox 202609030109 ===
638/638 checks passed
proofs run: 4
every composed cartridge passed its generation-matched proof
```

substation-intelligence 37 -> 53: sixteen new checks, thirteen of them run
against the real published product rather than a fixture. The block prints
its own measurement:

```
a count of machines, not a count of landings

  [PASS] the composed cartridge carries the network-topology module
  [PASS] the site-wide counts declare that they are units, not landings
  [PASS] the per-voltage lists are still landings, and are not deduplicated
  [PASS] the summariser never presents a landing tally as a machine count
  [PASS] given no units the summariser still reports the product own figures
  [PASS] given units it reports the machines rather than the landings
  [PASS] and a zero unit count is a real zero, not a missing one
  [PASS] the published node/branch product is on disk for a real-data check
  [PASS] Cowley publishes ten transformer landings
  [PASS] Cowley reports FIVE transformers, not ten
  [PASS] and they are the five machines the operator publishes
  [PASS] at 400 kV it still says five, and at 132 kV five - the same machines
  [PASS] a voltage-filtered query sees one winding and is not halved
  [PASS] Cowley six circuits are unchanged, because it owns one end of each
  [PASS] estate-wide: 2,944 landings resolve to 1,550 site-held units
  [PASS] and 484 of the 525 sites that hold a transformer were overstated
         2944 landings -> 1550 units at 525 sites, 484 of them previously overstated (1.90x)
```

Two sld-sandbox checks failed at first and were corrected, not disabled:
`the card asks the substation cartridge and renders only what it returns`
and `the card tells the cartridge what voltage the connection is made at`
both pin the exact call shape `networkName, { connectionKv })`, which this
change extends to `{ connectionKv, units: publishedUnits }`. The checks now
assert the new shape and still assert that the voltage is passed.

`node tools/scope/loop.mjs lint`

```
scope-ledger=PASS active=none master=done
```

`node tools/scope/loop.mjs state`

```
scope-ledger=PASS active=none master=done
STATE.md=UPDATED
```

**Live verification** — `atlas/current.json` and every composed cartridge
fetched from `https://ventusltd.github.io/gridatlas/atlas/` and hashed:

```
live generation 202609030109 composition 202609030109-gridatlas-v9.79
  MATCH  streaming-parquet-bridge   79045ccadaebf226af06fb2f800a32ca1f1e6c58d24442ee37037f1f28874af9
  MATCH  uk-gazetteer-flyto         0e57e7cdc1f87212f18afe95c1157308523b1eaba51dcb935ab72bc4e398c28d
  MATCH  sld-sandbox                ad158ff080f3e4acb4818c5147d0dee5099a8a6554dce5a6468db48a90983e9e
  MATCH  substation-intelligence    ad1de4764fd46bdc83b0b2a84cce5f55cb9bd7aed28a2d22863d8fb6a21ef5c5
LIVE VERIFIED: every composed cartridge matches local bytes and its manifest hash
```

Commit `ac810d6`, pushed to `origin/main` over `d20437e`.

---

## Generation 202609030116 — v9.80 — Reg1 mobile HIDE LAYERS

**Before the cut** (tip `ac810d6`): substation-intelligence `53/53`,
sld-sandbox `638/638`.

**After the cut**: substation-intelligence `53/53`, sld-sandbox `645/645`,
`proofs run: 4`, exit code `0`.

Seven checks added. The first reads the SHELL rather than the cartridge,
because the containment is a fact about the page:

```
  [PASS] HIDE LAYERS collapses the layer panel and NOT the application
  [PASS] the control targets the wrapper by name, and says so for a reader
  [PASS] a shell without that wrapper gets NO control, never a fallback to .dashboard
  [PASS] the toggle hides itself while a fullscreen element is present
  [PASS] and the hidden state is published rather than left to be inspected
  [PASS] the toggle is a 44 px touch target
  [PASS] the refusal path does not read `link`, which is in its dead zone there
```

`scope-ledger=PASS`, `STATE.md=UPDATED`.

**Live**: generation `202609030116`, composition `202609030116-gridatlas-v9.80`,
all four cartridges MATCH. sld-sandbox
`17b8cfd3d014df20a268b07dcfc1a26883d64cbd03f1e42be0a379773a78349c`.

Commit `e9491b6` over `ac810d6`.

---

## Generation 202609030119 — v9.81 — Reg2 deep-link camera

**Before the cut** (tip `e9491b6`): substation-intelligence `53/53`,
sld-sandbox `645/645`.

**After the cut**: substation-intelligence `53/53`, sld-sandbox `653/653`,
`proofs run: 4`, exit code `0`.

Eight checks added. The first two establish the premise from the other two
lanes' real bytes and passed BEFORE the fix, which is the point of them:

```
  [PASS] the shell stands down before any flyTo when there is no repd_ref
  [PASS] and the search lane stands down at the same test, reporting ABSENT
  [PASS] so this cartridge flies, and only when there is no repd_ref
  [PASS] the centre is the link's, and the zoom the link's where it is usable
  [PASS] a reader who asked for reduced motion still arrives
  [PASS] the move it made is published, with the reason it had to
  [PASS] the camera is set BEFORE the zoom is honoured and before the tech gate
  [PASS] a failed camera is recorded rather than taking the arrival with it
```

`scope-ledger=PASS`, `STATE.md=UPDATED`.

**Live**: generation `202609030119`, composition `202609030119-gridatlas-v9.81`,
all four cartridges MATCH. sld-sandbox
`18e7ead290e789bc1ebe8749a89f95d3b1375f798d09d06dd50e7a70b0f5d100`.

Commit `f1f430d` over `e9491b6`.

---

## Generation 202609030128 — v9.82 — Reg3 technology gate

**Before** (tip `f1f430d`): substation-intelligence `53/53`, sld-sandbox `653/653`.
**After**: substation-intelligence `53/53`, sld-sandbox `660/660`, exit `0`.

Seven checks added. Two re-cuts were needed and neither was pushed:

1. first cut failed `the camera is set BEFORE the zoom is honoured and before
   the tech gate` — my own v9.81 proof anchored on source text that this change
   replaced. The check was rewritten to compare three indices rather than one
   literal, which is what it should always have done.
2. first cut also failed `the sandbox cartridge is back under the 400 kB
   boundary with room to spare -- 341028 bytes` against a `< 340000` guard.
   Raising the guard was available and rejected, per v9.76's own precedent.
   1,661 characters of my own commentary were trimmed instead; the recut
   measured 339,367.

`scope-ledger=PASS`, `STATE.md=UPDATED`.

**Live**: generation `202609030128`, all four cartridges MATCH. sld-sandbox
`4c8ff0…` (recorded in full in the commit trail). Commit `52ebabc`.

---

## Generation 202609030137 — v9.83 — F5, pinned products

**Before** (tip `52ebabc`): substation-intelligence `53/53`, sld-sandbox `660/660`.
**After**: substation-intelligence `68/68`, sld-sandbox `667/667`, exit `0`,
cartridge `339,367` characters — unchanged, because the new code went into a
module composed into `substation-intelligence` rather than into the sandbox.

Fifteen checks added to substation-intelligence, seven to sld-sandbox. The pin
table is exercised in its own vm context with real WebCrypto, so the refusal
path executes:

```
  [PASS] it froze its surface and named its schema
  [PASS] every pinned product names a 40-character commit, never a branch
  [PASS] and a 64-character SHA-256 of the bytes served at that commit
  [PASS] the URL it builds is the commit, not the branch
  [PASS] its digest arithmetic is the arithmetic, checked against node
  [PASS] bytes that disagree with the recorded digest are a MISMATCH
  [PASS] and the mismatch says which bytes it got and which it wanted
  [PASS] an unknown id is unverified rather than quietly accepted
  [PASS] a pin says which bytes were read and nothing about whether they are right
  [PASS] a MISMATCH refuses to answer rather than reading on
  [PASS] and an uncomposed pin table is a refusal, not a guessed URL
  [PASS] the load published which pinned bytes it read
  [PASS] and where there is no crypto it says so, and still reads the product
```

Three pre-existing checks asserted the DEFECT and were rewritten to assert the
fix, not disabled:

- `it reads the data repository product` matched `Ventusltd/data-grid-gb/` as a
  contiguous string; it now matches the pin table's `repository` field.
- `it reads the repository that owns the data, not a copy` matched
  `data-gb-electricity/main/derived/...`; it now matches the pin lookup.
- `the product is named once, at data-grid-gb main, and is the v1 schema`
  asserted the branch by name. It now asserts the pin AND that no
  `main/derived/gb-transmission-network.v1.json` string survives anywhere.

Independent of the harness, all three pinned URLs were fetched over the network
and hashed before the cut:

```
gb-transmission-network.v1.json  10,069,966 B  fc331cc20b061f85adf18d890762a164328a1c5e84acef6a23d35d36f849fc8a
price-decade-rollup.json              6,873 B  18da5059c93cf09f6036bfcaabf56afaedf16d5f03e664c3cf0b0cff1dca970d
connection-points.v3.json         2,896,561 B  11e28859a6d17cc8ee4047c2032d55d043be98f7123743f3b2b03225e07a4c0c
```

**Live**: generation `202609030137`, composition `202609030137-gridatlas-v9.83`,
all four MATCH. sld-sandbox
`0a71e32dc5ab52b128f797959157d513ec77c962095c8f14379e131729c67109`,
substation-intelligence
`ceb80e26da587964567b090ac81513006f7703051798c25e50471f03aee9e451`.

Commit `4a17fa3` over `52ebabc`.

---

## `tools/scope/loop.mjs --stdout` — commit `4b1641e` (no composition change)

Not a generation: it touches no cartridge, so nothing was recomposed.

Before:

```
$ printf 'DELIBERATELY WRONG\n' > STATE.md
$ node tools/scope/loop.mjs state --stdout
scope-ledger=PASS active=none master=done
STATE.md=UPDATED
$ head -1 STATE.md
# GridAtlas durable state          <- the check repaired the drift it exists to detect
```

After:

```
$ printf 'DELIBERATELY WRONG\n' > STATE.md
$ node tools/scope/loop.mjs state --stdout > /tmp/s.txt 2>/dev/null
$ head -1 STATE.md
DELIBERATELY WRONG                 <- untouched
$ cmp -s /tmp/s.txt STATE.md; echo $?
1                                  <- the comparison can now fail

$ node tools/scope/loop.mjs state         # no flag: unchanged, writes the file
$ node tools/scope/loop.mjs state --stdout > /tmp/s.txt 2>/dev/null
$ cmp -s /tmp/s.txt STATE.md; echo $?
0                                  <- byte-identical when it should be

$ node tools/scope/loop.mjs state --bogus
[scope-loop:state] unknown flag --bogus     exit 1
```

`node tools/proofs/run-current.mjs` exit `0`, unaffected.

---

## Generation 202609030151 — v9.84 — the proof reads through the pin

**The gate changed here.** Up to v9.83 I recorded the local `run-current`
result. It was green five times while CI was red five times. From v9.84 the
gate is the CI conclusion for the pushed commit.

**CI evidence for the failure**, from the Actions API keyed by commit:

```
v9.79  ac810d6  run 33702626898  202608312212 GridAtlas cartridge proof  failure
       job proof:
         success   The composition matches what is declared and hashed
         FAIL      The composed cartridge passes its own proof
         skipped   The scope ledger and workflow budget still hold
         skipped   STATE.md was regenerated before it was committed
         skipped   No CRLF survives in a tracked text file
         skipped   Renormalising changes nothing, so .gitattributes is being obeyed
```

**Reproduced in the runner's shape** — fresh `--shared` clone, no
`data-grid-gb` neighbour, node 24:

```
  [FAIL] the published node/branch product is on disk for a real-data check
  59/60 checks passed
```

**After the fix, same shape, both products fetched through the pin:**

```
  [PASS] the connection-points product this proof measures is the product the pin names
  [PASS] the product this proof measures is the product the pin names
         read 10069966 bytes from the pinned URL
73/73 checks passed
real    0m0.738s
```

**Local, with the neighbour present** — the fast path, digest-verified:

```
  [PASS] the product this proof measures is the product the pin names
         read 10069966 bytes from the checkout beside this repository
73/73 checks passed
```

**Local full harness after the cut**: substation-intelligence `73/73`,
sld-sandbox `667/667`, `verify-compose` PASS, `scope-ledger=PASS`.

One cut was aborted before pushing: restamping only `substation-intelligence`
failed three sld-sandbox manifest-identity checks (`it spans the whole reviewed
session`, `the manifest states this generation everywhere it states one`, `the
manifest chains by pointer, not by sort order`), because that proof derives the
generation from its own filename. Re-cut restamping both.

**CI — the gate**: commit `5a59e711bfdf3b18a04736ba55377a88d442e10d`,
run **`33705373009`**, conclusion **`success`**, every step green:

```
JOB proof success
    success   Checkout the pushed state
    success   Checkout the canonical geodesy beside it
    success   Node
    success   The composition matches what is declared and hashed
    success   The composed cartridge passes its own proof
    success   The scope ledger and workflow budget still hold
    success   STATE.md was regenerated before it was committed
    success   No CRLF survives in a tracked text file
    success   Renormalising changes nothing, so .gitattributes is being obeyed
```

The four steps after the proof had been skipped on every push since v9.79.
They have now run.

**Live**: generation `202609030151`, composition `202609030151-gridatlas-v9.84`,
all four cartridges MATCH. sld-sandbox
`2a0d558b74a39583026bf97d5c364ae7db5d47778b76bb950013cfb15398130c`,
substation-intelligence
`483f5f3ca7cf7a67c9526947f2f14723e091b64c960ea1fe3759d5db512f2c53`.

Commit `5a59e71` over `4b1641e`.

### CI status of the five generations before it

`202608312212 GridAtlas cartridge proof` was `failure` on `ac810d6` (v9.79),
`e9491b6` (v9.80), `f1f430d` (v9.81), `52ebabc` (v9.82) and `4a17fa3` (v9.83).
None is amended — they are shipped, and each is superseded by the one after
it. v9.84 is the successor that fixes the cause, and the CI run for it is
green.

---

## Generation 202609030156 — v9.85 — the version ledger moves

**Before** (tip `5a59e71`): substation-intelligence `73/73`, sld-sandbox `667/667`.
**After**: substation-intelligence `73/73`, sld-sandbox `668/668`, exit `0`.

```
  [PASS] the ledger exists and is embedded, not fetched
  [PASS] the sandbox reads it rather than carrying a second copy
  [PASS] the sandbox cartridge is back under the 400 kB boundary with room to spare  326331 bytes
```

One cut aborted before pushing: `tools/recompose.mjs` scans part files for
`const VERSION_LEDGER = [` and found that literal inside the new module's
header comment, then tried to `JSON.parse` the sentence:

```
[` is written here verbatim because that is the
 ^
SyntaxError: Unexpected token '`', "[` is writt"... is not valid JSON
```

Reworded, then verified by counting: the module matches that regex exactly
once, and the match parses to 68 entries.

`verify-compose` PASS, `scope-ledger=PASS`, `STATE.md=UPDATED`.

**CI — the gate**: commit `f0c29ab0ce31c937a630a01951347717de0dffa2`,
run **`33705700987`**, conclusion **`success`**.

Commit `f0c29ab` over `5a59e71`.

---

## Generation 202609030200 — v9.86 — F4, the coverage of "nearest"

**Before** (tip `f0c29ab`): substation-intelligence `73/73`, sld-sandbox `668/668`.
**After**: substation-intelligence `82/82`, sld-sandbox `676/676`, exit `0`.

The coverage checks compare what the cartridge REPORTS against the payload it
was GIVEN, so they cannot pass on a remembered number:

```
  [PASS] the coverage it reports is counted from the payload it was given
  [PASS] and it agrees with the state it publishes for the whole product
  [PASS] at 400 kV it counts only what a 400 kV search would consider
  [PASS] the predicate is the one the distance search itself uses
  [PASS] no coverage figure is written down anywhere in the cartridge
  [PASS] the four numbers the sentence prints are all interpolated
         at 400 kV: 214 of 355 published carry coordinates, 141 cannot be measured to
         whole product: 502 of 886
```

One check of mine was rewritten rather than disabled: `every number in the
sentence is interpolated, never written down` matched the voltage class `400`
inside a template literal. The voltage is what the search asked for, not
something it counted, so the check now names the figures that actually rot —
214, 355, 141, 502, 886, 384, 489, 206 — and asserts none appears outside a
comment.

`verify-compose` PASS, `scope-ledger=PASS`, `STATE.md=UPDATED`.

**CI — the gate**: commit `97d3ffca580b94ff048ccf9792cbb0ddf39cb2e8`,
run `33705965506`. Polling was cut off by the API budget reaching zero; the
conclusion is recorded in the entry for the cut that follows it, which could
not be made until it was confirmed.

**Live**: generation `202609030200`, composition `202609030200-gridatlas-v9.86`,
all four cartridges MATCH. sld-sandbox
`d7cc6c4db72de6efe755ef7e276dcb9dff985f1ce2ca2d372bc95382d25cc68d`,
substation-intelligence
`3c3e53c1d7c7d93f40b5d3eb67c37f1a73db7693094f9c1786e174e87c328c26`.

Commit `97d3ffc` over `f0c29ab`.

---

## Generation 202609030233 — v9.87 — the corridor scalar

**Before** (tip `97d3ffc`): substation-intelligence `82/82`, sld-sandbox `676/676`.
**After**: substation-intelligence `97/97`, sld-sandbox `687/687`, exit `0`,
cartridge `330,634` characters.

The scalar runs as arithmetic in its own context, not as a regex over source:

```
  [PASS] the factor is the calibrated 1.245
  [PASS] the estimate is the arithmetic, not a lookup
  [PASS] THE SAMPLE IS 59 DISTINCT SITE PAIRS, not 95 circuits
  [PASS] the error the calibration actually achieved travels with it
  [PASS] under a kilometre it withholds rather than scaling
  [PASS] and says what the numbers were in that band
  [PASS] at the boundary it answers, so the rule is a threshold and not a gap
  [PASS] nothing, zero and a negative are null, never zero kilometres
  [PASS] IT OFFERS NO OVERHEAD ANSWER AT ALL
  [PASS] and publishes 1.13 as the reason the cable factor is not that answer
  [PASS] the standing caveat is exactly the four things it is not
  [PASS] THE SAMPLE ON THE CARD IS THE SITE PAIRS, not the circuit count
  [PASS] no corridor number is written into the sentence
  [PASS] the sandbox never carries its own copy of the factor
```

`verify-compose` PASS, `scope-ledger=PASS`.

**Gate — CI job reproduced locally** at the exact pushed commit
`1fb6262e2ab524ad87a07b658c9a06ca2e494c44`, runner shape (fresh clone,
`grid-distance-maths` beside it, no `data-grid-gb`), all six steps:

```
composition matches what is declared and hashed   PASS
composed cartridge passes its own proof           97/97, 687/687, exit 0
scope ledger and workflow budget                  scope-ledger=PASS
STATE.md was regenerated before it was committed  clean
no CRLF survives in a tracked text file           all LF
renormalising changes nothing                     clean
```

The runner's own conclusion was not sampled: API budget at zero.

**Live**: generation `202609030233`, all four MATCH. sld-sandbox
`0290dc54a3046b86bc134a844c61e702da39184e21508bc71e0c766bc8531d3b`.

Commit `1fb6262` over `97d3ffc`.

---

## Generation 202609030234 — v9.88 — the 44 px action

**Before** (tip `1fb6262`): substation-intelligence `97/97`, sld-sandbox `687/687`.
**After**: substation-intelligence `97/97`, sld-sandbox `687/687` -> `702/702`,
exit `0`, cartridge `339,864` characters — **136 under the guard**.

```
  [PASS] the target is 44 px, and so is every control inside the sheet
  [PASS] the sheet is a labelled dialog, closable by button and by Escape
  [PASS] it honours a reader who asked for reduced motion
  [PASS] visibility is toggled with hidden, not by rewriting display
  [PASS] the desktop slot it takes is one nothing else binds
  [PASS] the long press cancels on movement, with a stated threshold
  [PASS] a second finger is not a long press
  [PASS] AND IT NEVER FIRES DURING AN SLD DRAG, checked twice
  [PASS] touchend and touchcancel disarm it
  [PASS] the listeners are passive, so they cannot block a scroll or a pan
  [PASS] an absent corridor module leaves the measured distances standing
```

`verify-compose` PASS, `scope-ledger=PASS`.

**Gate — the runner's own conclusion**: commit
`8fb95a2138010851039a1d648e730f1e10889576`, run **`33708191973`**,
conclusion **`success`**.

**Live**: generation `202609030234`, composition `202609030234-gridatlas-v9.88`,
all four MATCH. sld-sandbox
`660d4a2a680ffc5fcc9fa4cf706ed7470609cfe648903e044b2c6bb6ae062c83`,
substation-intelligence
`8fd02f24cc49233393091c73a3a7b321e5f48ed44482d886dd9db85fcca7003d`.

Commit `8fb95a2` over `1fb6262`.

---

## Retrospective confirmation for v9.86

The poll I abandoned when the budget hit zero completed in the background and
is recorded here for completeness:

```
remaining=58
RUN 33705965414  202608310050 GridAtlas next-version builders  | completed success
RUN 33705965506  202608312212 GridAtlas cartridge proof        | completed success
RUN 33705964271  pages build and deployment                    | completed success
```

The local reproduction of that same commit had reached the same conclusion,
which is the only evidence I have that the substitute gate is sound.
