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
