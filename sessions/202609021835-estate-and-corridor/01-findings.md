# Findings

Every defect found, with its evidence and how to reproduce it. Ordered by consequence, not by
discovery. None is graded; each states what was measured and what follows.

---

## F1 — The Pages gate demands the pointer commit be HEAD, so every push fails

**Repository** `pipelinenews` · **Status** open · **Severity** live site five days stale

`validate_live_pointer()` requires that the commit which last touched `state/live-set.json`
**be** the deployment HEAD.

```
atman/202608262014-build-pages.py:904
  require(pointer_commit == git_text(root, "rev-parse", "HEAD"),
          "live pointer commit is not deployment HEAD")
```

Meanwhile `pages.yml` triggers on push to paths including `releases/*-pipelinenews/**` — exactly
where daily feature work lands. So a release commit starts a deploy that the gate must refuse.

```
pointer  187ed63  2026-08-29 15:22 UTC   state/live-set.json
HEAD     6e40226  2026-09-02 06:34 UTC   (+191 commits)
result   25 consecutive failed deploys, last success 2026-08-30 11:13 UTC
         138 commits of merged work never published
```

**Reproduce**

```bash
git clone --shared --no-checkout <pipelinenews>/.git pn && cd pn
git remote add gh https://github.com/Ventusltd/pipelinenews.git
git fetch -q gh main && git checkout -q -B repro gh/main
python atman/202608262014-build-pages.py --generation latest --stage _site \
       --timestamp-folder-release 202608291447-pipelinenews
```

**Not a fix, an observation:** either the trigger set narrows to pointer changes only, or the gate
accepts a pointer that is an ancestor of HEAD. Which is right is a decision about what a deploy is
allowed to mean, and belongs to whoever owns that contract.

---

## F2 — The substation name normaliser collapses distinct sites onto one key

**Repository** `gridatlas` · **Status** open · **Severity** wrong asset bound for 7.5% of the network

`atlas/parts/202609012350-substation-intelligence-body.js:51`

```js
const NOISE = /\b(SUBSTATION|SUB STATION|SUBSTN|GRID|SUPPLY|POINT|GSP|NATIONAL|POWER|
                 STATION|WIND|FARM|WINDFARM|OFFSHORE|ONSHORE|EXTENSION|
                 400KV|275KV|132KV|66KV|33KV|11KV|NGET|SSE|SP|SHE)\b/g;
function normalise(name) {
  return String(name || '').toUpperCase()
    .replace(/[^A-Z0-9 ]/g, ' ').replace(NOISE, ' ')
    .split(/\s+/).filter(Boolean).join(' ');
}
```

It strips `ONSHORE`, `OFFSHORE` and `EXTENSION` — the exact words that distinguish physically
different assets. Applied to the 921 NESO site names:

```
distinct keys after normalisation   886
keys claimed by 2+ different sites   34
sites inside a colliding key         69      (7.5% of the network)

MORAY EAST     <- MORAY EAST ONSHORE | MORAY EAST ONSHORE | MORAY EAST OFFSHORE
BEATRICE       <- BEATRICE ONSHORE   | BEATRICE OFFSHORE
ARECLEOCH      <- ARECLEOCH          | ARECLEOCH EXTENSION
BURBO BANK     <- BURBO BANK EXTENSION ONSHORE | BURBO BANK EXTENSION OFFSHORE
DOGGER BANK A  <- DOGGER BANK A ONSHORE | DOGGER BANK A OFFSHORE
```

And the map keeps only the first: `if (key && !byName.has(key)) byName.set(key, point);`

An onshore and an offshore converter station are different assets, at different voltages, often
tens of kilometres apart. For those 69 sites the panel binds to whichever loaded first.

**Corroborated independently.** The routing study (`05`) found 5 cable circuits whose straight-line
distance exceeds their published built length — physically impossible. The worst publishes
**0.33 km against a 24.78 km straight line**. That is this defect surfacing in a second dataset.

This is the same class Codex already fixed once: *"WBUR's exact-name join binds a different
West Burton 96.42 km from the project."* Fixed for that instance, not for the class.

**Reproduce** `scripts/` — the collision census is inline in `00-LOG.md` §3; the 5 impossible
circuits fall out of `scripts/routefactor.py` when filtered to `circuit_type == "Cable"`.

---

## F3 — Site-wide transformer counts are 1.90x overstated

**Repository** `data-grid-gb` consumers · **Status** open · **Severity** 92% of sites affected

The card for COWLEY states *"6 circuits · 10 transformers"*. There are **5** physical transformers:

```
COWL41 <-> COWL11   278 MVA
COWL41 <-> COWL11   269 MVA
COWL41 <-> COWL11   269 MVA
COWL41 <-> COWL12   269 MVA
COWL41 <-> COWL12   269 MVA
```

*"At 400 kV: 5 transformers"* and *"At 132 kV: 5 transformers"* are both correct — the same five
machines seen from each winding. The site-wide line adds them.

**Mechanism.** The count is per node-end at the site. A circuit's two ends are usually at
*different* sites, so it contributes 1 — which is why circuit counts are right. A transformer's
two ends are at the *same* site, so it contributes 2.

```
transformers with both ends at one site   1,394 of 1,472   (95%)
sites with transformers                     525
sites where the two counts differ           484   (92%)
network-wide: 1,472 real units shown as 2,944       (1.90x)

worst: IVER 12 shown as 24 · HORNSEA OFFSHORE 12 as 24 · BEAULY 10 as 20
```

**Reproduce** `scripts/verify_cowley.py` — note it contains the `Counter[400]`/`Counter[400.0]`
bug described in `00-LOG.md` §7; the corrected recount is inline in the log.

---

## F4 — "Nearest" is asserted over 57% of the network

**Repository** `gridatlas` / `data-grid-gb` · **Status** open · **Severity** superlative unsupportable

`state.nearest` iterates `located`, built from connection points that carry coordinates.

```
connection points published          886
with coordinates                     502   (57%)
invisible to a distance search       384   (43%)

400 kV   355 published, 214 located, 141 blind   (40%)
275 kV   261 published, 197 located,  64 blind   (25%)
132 kV   575 published, 358 located, 217 blind   (38%)
```

*"Nearest 400 kV substation: Cowley · 15.76 km"* is nearest among **214 of 355**. Two in five
400 kV sites cannot be seen, so a nearer one may exist and the card cannot know.

**Root cause is upstream and documented.** `sources/sources-manifest.json` says it plainly:
ETYS names substations and does not locate them, so the only geometry the estate holds comes from
OpenStreetMap via a GridAtlas release. That is also why F2 exists — the join must go through names.

**Two fixes, both needed:** geocode the 384, and until then state the coverage wherever the word
*nearest* appears.

---

## F5 — The Atlas fetches its own product from a moving branch

**Repository** `gridatlas` · **Status** open · **Severity** supply chain

```js
const PRODUCT = 'https://raw.githubusercontent.com/Ventusltd/data-grid-gb/'
  + 'main/derived/connection-points.v3.json';
const REQUIRED_SCHEMA = 'data-grid-gb.connection-points.v3';
```

The NESO inputs are pinned by SHA-256 with an explicit rationale — *document ids are stable and
'latest' links are not*. The estate's own product is fetched from `main`. Only the schema string
is checked, and a v3 file with different numbers still passes.

An immutable Atlas release can therefore change what it says without any of its own bytes changing.
The discipline already exists in the repo; it is simply not applied to the last hop.

---

## F6 — Four published sites answer 404 at their root

**Status** open · **Severity** observation, may be intentional

```
companies             404
data-gb-electricity   404
data-interconnectors  404
pipelinenews          404      (releases/<stamp>/ answers 200)
```

Whether a root landing page is intended is a decision, not a defect measurable from outside.
Recorded because a reader who trims the URL sees nothing.

---

## F7 — Standing red CI, estate-wide

**Status** open · At scan time, **37 workflows** had a failing most-recent run.

```
data-gridatlas         hourly watchdog          11/11 failed, last 18:40 same day
data-interconnectors   GridBot build             4/4  failed, 0 successes in 10 sampled
cvaa                   self-test + fleet audit   5/6  failed
globalgrid2050         V9.6.2 exact commit       10/11 failed
pipelinenews           Deploy Pages              27/28 failed
```

The `data-gridatlas` hourly watchdog is the notable one: it has alarmed into a void every hour and
nothing consumed the alarm.

Also recorded: `globalgrid2050` carries **241 workflow files** against `gridatlas`'s 5, and
8,140 lifetime runs. That is the largest maintenance surface in the estate by a wide margin.
