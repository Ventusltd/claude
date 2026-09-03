# Licensing and attribution

The question was whether pandapower's licence permits studying and absorbing its electrical
engineering logic, and if not, whether the physics could be derived independently.

## pandapower is BSD 3-Clause. There is no obstacle.

`Ventusltd/pandapower` is a **fork** of `e2nIEE/pandapower`, 828 MB, excluded from every count
in this session. Upstream licence, fetched and read during the session:

```
BSD 3-Clause License
Copyright (c) 2016-2026 University of Kassel
              2016-2026 Fraunhofer Institute for Energy Economics
              2016-2026 Energy System Technology (IEE) Kassel
              2016-2026 individual contributors
```

Permits use, modification, and redistribution in source and binary form, commercially and in
closed source, subject to three conditions:

1. Retain the copyright notice, conditions and disclaimer in redistributed source
2. Reproduce them in documentation for binary distribution
3. **Do not use the copyright holders' or contributors' names to endorse or promote a derived
   product** without prior written permission

No copyleft, no share-alike, no obligation to open-source anything. The physics-derivation
workaround is unnecessary.

## The decisive argument is architectural, not legal

pandapower is Python/NumPy/pandas. The Atlas runtime is client-side JavaScript cartridges loaded
through `window.__GRIDATLAS_MODULES__`. pandapower cannot ship into that. So "just use it" was
never available for the live engine regardless of licence.

That turns the licence question into a non-question:

| | |
|---|---|
| shipped engine | own JS, written from the physics and the standards |
| pandapower | offline, in CI, as the independent reference the engine is checked against |
| legal status | not a derivative work; clauses 1 and 2 never attach to shipped code |
| clause 3 | trivially satisfied, because the name is never used to promote |

It is also **stronger for credibility**. "We use pandapower" borrows a reputation. "Our engine
agrees with pandapower to within X across N reference networks" proves the engine is right.

## The line clause 3 draws

It separates **stating a fact** from **implying a relationship**. Attribution is required by the
licence; endorsement is forbidden. They are not in tension — keep them on different surfaces.

**Safe** — NOTICE file, `/attributions` page, docs, technical appendix:

> Power-flow and short-circuit results are validated against pandapower (BSD-3-Clause,
> (c) 2016-2026 University of Kassel, Fraunhofer Institute for Energy Economics and Energy
> System Technology IEE, and contributors), used as an independent reference implementation in
> our test suite. Its authors are not affiliated with, and do not endorse, Ventus Ltd or
> GlobalGrid2050.

That final sentence removes clause-3 ambiguity entirely and costs nothing.

**Unsafe** — homepage, deck, press, investor materials: their logos, "powered by Fraunhofer
technology", a partners or trusted-by slide, or anything placing their mark beside yours.

**Never use the phrase "validated by Fraunhofer".** Validated *against* pandapower is a fact you
performed. Validated *by* Fraunhofer says they did it — false, and an endorsement claim. One
preposition is the whole difference.

## Attribute the originators, not the middlemen

The user's framing, and it is correct: Fraunhofer authored pandapower. They did not author
power-flow. Citation is also not endorsement — a bibliography cannot be read as a partnership,
which is why it is the safe register.

### Layer 1 — the method. None of it is protectable.

| contribution | attribution |
|---|---|
| Symmetrical components, the basis of unbalanced fault analysis | C. L. Fortescue, *Method of Symmetrical Co-ordinates Applied to the Solution of Polyphase Networks*, AIEE, 1918 |
| Complex/phasor method making AC analysis tractable | C. P. Steinmetz, International Electrical Congress, 1893 |
| Earth-return impedance, real line impedance | J. R. Carson, *Wave Propagation in Overhead Wires with Ground Return*, Bell System Technical Journal, 1926 |
| Newton-Raphson power flow | W. F. Tinney & C. E. Hart, IEEE Trans. PAS-86, 1967 |
| Sparse ordered factorisation, what makes it tractable at scale | W. F. Tinney & J. W. Walker, Proc. IEEE 55, 1967 |
| Fast decoupled load flow | B. Stott & O. Alsac, IEEE Trans. PAS-93, 1974 |
| First digital computer load flow | J. B. Ward & H. W. Hale, AIEE, 1956 |
| alpha-beta-0 transformation, and the foundational textbooks | Edith Clarke, *Circuit Analysis of A-C Power Systems*, 1943 / 1950 |
| Transmission line equations | Oliver Heaviside, 1880s |
| Circuit laws | G. R. Kirchhoff 1845; G. S. Ohm 1827 |

### Layer 2 — the reference implementation. Credit the paper, not the institution.

L. Thurner, A. Scheidler, et al., *pandapower — An Open-Source Python Tool for Convenient
Modeling, Analysis and Optimization of Electric Power Systems*, IEEE Transactions on Power
Systems 33(6), 2018. BSD-3-Clause, (c) University of Kassel and Fraunhofer IEE.

Naming the authors and the paper is proper credit. Naming the institutions in a deck is what
clause 3 restricts. The copyright line belongs in NOTICE — that is clause 1, required.

### Layer 3 — the data.

NESO ETYS appendices B and D; DESNZ/REPD; OpenStreetMap contributors (**ODbL — note the
share-alike reaches derived *data*, unlike BSD on code**); Elexon; Open Charge Map.

## Civil engineering literature, verified by fetching

| source | what it settles |
|---|---|
| National Grid, *Undergrounding high voltage electricity transmission lines: the technical issues* | Working width **40-65 m** for a 400 kV double circuit; trench ~1.5 m wide, 1.2 m deep, four trenches of three cables; **joint bays every 500-1,000 m**; deep tunnelling named as the technique enabling river and railway crossings |
| IET / Parsons Brinckerhoff (2012), *Electricity Transmission Costing Study* | Prices trenchless crossings as discrete events; watercourses categorised by span, large ~150 m, medium ~70 m |
| CIGRE TB 770, WG B1.48, *Trenchless Technologies* | HDD, microtunnelling, pipe ramming, ploughing; which technique suits which obstacle and span |
| CIGRE TB 889, WG B1.61 (2022), *Installation of Underground HV Cable Systems* | Supersedes TB 194 (2001); bend radii, pulling tensions, drum section lengths |

**The National Grid figure has engineering consequences.** A 400 kV underground circuit needs a
40-65 m working swathe — wider than most B-road verges and many A-road corridors. Any router must
carry a corridor-width feasibility term, not only a length.

## How literature should enter data-grid-gb

Not as prose. An essay cannot be verified; a **parameter with a citation** can. It should arrive
in the same shape as everything else in that repository: `sources/literature-manifest.json` pinned
by SHA-256 like the NESO appendices, and `derived/civil-parameters.v1.json` carrying the numbers,
each with its source.

```json
{ "id": "swathe_width_m_400kv_double", "value": [40, 65], "unit": "m",
  "source": "national-grid-undergrounding-technical-issues",
  "note": "construction working width, not permanent easement" }
```

Then the router reads parameters from a product rather than hardcoding them, every civil number
can cite a source the way fault currents already cite sheet D3.1 row 137, and a challenged
parameter is answered with a document rather than an argument.

What not to write: anything reading as design advice, sizing, or a route recommendation. The
repository's own `not_a_connection_assessment` line is the boundary.
