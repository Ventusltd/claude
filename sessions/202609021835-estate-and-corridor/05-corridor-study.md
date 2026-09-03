# The corridor study — a feature scoped, gated, and cancelled

The proposal: replace the straight line between a project and a substation with a road-routed
corridor, satnav style, penalising railway crossings. It was scoped in detail, then the gate was
run before building. **The gate failed.** The feature was cancelled the same afternoon.

This is the most valuable single entry in this repository, because it is a six-month build stopped
by an hour of measurement.

## The gate, and why it could be run at all

The validation set was already in the data and nobody had noticed. NESO publishes `cable_km` for
circuits that are **fully buried** — real routes with a real built length, between two sites whose
coordinates the estate holds. So three numbers exist per circuit:

- straight-line great-circle distance between the two sites (the baseline to beat)
- road-routed distance between the same points (the candidate)
- published built length (the truth)

**Gate set before running:** median absolute error < 15% against published `cable_km`, AND beat the
straight line on >= 80% of circuits.

## Result

```
method                                    median abs err   beats straight   gate
straight line, raw                              25.4%            —          baseline
road-routed, primary + trunk + motorway         20.3%      52.6% of 95      FAIL
straight line x one constant (k = 1.245)         8.4%            —          PASS  (8.6% LOO)
```

**A single multiplier beats a 275,585-node routing graph.**

Independently recomputed rather than taken on trust: 95 circuits confirmed, 59 distinct site pairs
confirmed, 5 impossible circuits confirmed, best k = **1.245 -> 8.45%** against the study's
1.243 -> 8.34%. Differences are grid resolution in the fit, not disagreement.

```
k = 1.245     bootstrap range 1.22 - 1.33
              73% of circuits within 15% of real built length
              needs no graph, no snapping, cannot fail
```

## Why routing lost

**It breaks worst exactly where it is needed.** Splitting by detour ratio is unambiguous:

```
67 circuits with routed/straight <= 2x      14.2% median error
14 circuits above 2x                       199.3% median error
   (the straight line on those same 14:      25.7%)
```

All urban. Worst cases:

```
Dewar Place - Whitehouse       published 2.48 km   straight 1.83   routed 18.67
Gorgie - Telford Road                    4.60              2.94          14.24
Kirkstall - Skelton Grange               8.61              7.44          17.07
Pudding Mill Lane - West Ham             2.17              1.81           4.57
```

**Crossing penalties made it monotonically worse.** This overturned the design's central idea:

```
penalty per crossing (km-equiv)    0     0.5    1      2      3      5      8      20
median absolute % error         20.26  21.43  23.45  23.45  24.14  24.14  24.14  33.32
```

Best penalty is **zero**. Crossing count correlates with routing error at Spearman **-0.12** — no
signal. It correlates only with route length (Pearson 0.48), which is trivial. Roads cross railways
at bridges that already exist; the suspicion was recorded in the scope and the weighting was
proposed anyway. The measurement settled it.

**Snapping is a real cost, not a rounding term.** 41 of 190 endpoints sat more than 1 km from any
routable road; worst 15.19 km. 14 circuits failed a 5 km snap gate outright. Remote Scottish and
offshore sites cannot be reached by a road graph at all — one validation circuit is a 39 km subsea
cable.

## The graph that was built

```
primary + trunk merged     275,585 nodes   319,152 edges   61,092 km   built in 9.3 s
from                       2,247,183 shape points
giant component            96.04% of nodes   (above the 90% soundness bar)
edges crossing a railway   1.52%
```

Sanity checks all passed: haversine agrees with spherical Vincenty to 3.7e-13; route length equals
its leg sum to 2.2e-15; identical-point route = 0.0; **zero violations** of routed >= straight.
Four edges of 319,152 differ from their own geometry by at most 9 cm, from junction coordinates
rounded at 1e-6 degrees. Benign.

One real bug found and fixed mid-study: Windows `array('l')` is 4 bytes, so `bytes(8*n)`
allocations produced double-length zero-padded arrays. Switched to `'q'`.

## The bound on this negative result — important

**Only primary, trunk and motorway roads exist in the estate.** No secondary, tertiary or
residential. The observed failure mode — urban detours where the real link uses minor streets —
points directly at that gap. Adding motorways moved median error by nothing (20.26% -> 20.26%), so
what is missing is *minor* roads, not major ones.

A dense OSM network is therefore **untested, not disproven**. But the bar it must now clear is
**8.4%**, not 15%, because the constant already passes. That is a far harder target for vastly more
machinery.

## Two corrections this forced

**The sample is 59, not 95.** Parallel circuits duplicate the same geometry between the same two
sites. Every confidence statement must use the pair count.

**Five circuits are geometrically impossible** — straight line exceeds published built length. The
worst publishes **0.33 km against a 24.78 km straight line**. That is F2, the name-join defect,
surfacing independently in a second dataset. It raised F2's priority.

## What to ship instead

Keep the straight line. Add one calibrated line beside it:

```
15.76 km straight  ·  ~19.6 km corridor estimate
(x1.245, 73% of GB cable circuits within 15%)
```

Cheap, honest, carries its own uncertainty, bound to a 59-pair evidence base. The tracer UI design
survives unchanged — the neon corridors draw a calibrated straight line rather than a routed path,
and the right-click / long-press gesture design is unaffected.

**Do not apply any of this to overhead lines.** Their measured factor is 1.13 and they cross open
country; road-routing an OHL question would be worse than the straight line.

## The UI design that survives

The v8 engine binds `click`, `dblclick`, `mousemove`, `mousedown`, `mouseup`, `keydown`. It binds
**no `contextmenu` and no `touchstart`** — both gesture slots are free.

- desktop: right-click. Displaces nothing.
- touch: long-press ~500 ms with a movement threshold, so a pan never fires it.
- both: a TRACE tile beside Zone Draw and the radius tool, following the collapsible-panel pattern.

Corridors coloured by the **voltage class of the target**, reusing the palette already carrying the
400 / 275 / 132 / 66 / 33 kV layers. Straight line stays untouched; this is purely additive.

The exploration case is the interesting one: the card already names what a circuit reaches
(CULHAM JET, DIDCOT, EAST CLAYDON, LEIGHTON BUZZARD, MINETY, WALHAM). Tracing from a substation
rather than a project walks the published network one hop further per press.

**The line it must not cross:** a drawn corridor will be read as a buildable route. It is a
corridor length estimate — not a wayleave, consent, design or cost. Drawing it beautifully raises
that risk rather than lowering it.

## Scripts

`scripts/build_graph.py`, `router.py`, `run_study.py`, `analyze.py`, `crossings.py`, `sweep.py`,
`calib.py`, `sanity.py`, `rail.py`, `edge_rail.py`, `common.py`. Outputs in `data/out_*.json`.
`scripts/routefactor.py` produces the route-factor distribution independently.
