# Session log — 202609021835 to 202609030120 UTC

Full record, in order. Wrong turns are kept and marked `WRONG`, because the value of a log
is mostly in what it stops the next session repeating.

Channel purpose as stated at the outset: *"running CI/CD automation testing and discuss state,
not build here, as there is already an active claude session we need to protect the context for."*
That constraint held for the first third and then the user redirected to building. Both are recorded.

---

## 1. Estate discovery

Started with no knowledge of where anything lived.

- Home directory holds **worktrees**, not repos: `coord24`, `g963`, `codex-grid-202609020010`,
  `dggb-mapclick`, `global-10x`, `global-lane-index`. Each `.git` is a file pointing at
  `C:/Users/vikra/OneDrive/Documents/GitHub/<repo>/.git/worktrees/<name>`.
- The canonical repos are under `OneDrive/Documents/GitHub/`.
- `gh` CLI is **not installed**. No `GH_TOKEN`, no `~/.git-credentials`. GitHub API is therefore
  unauthenticated: **60 requests/hour**, and `/actions/runs/<id>/logs` returns **403**.
- That last point shaped the whole session: CI failures could not be read, so they had to be
  **reproduced locally** instead. This turned out to be better evidence than a log would have been.

**WRONG, and corrected within the hour:** I first assumed the 15 repos cloned locally were the
estate. The user corrected me. `GET /users/Ventusltd/repos` returns **30**. I had scanned half.
Lesson recorded: enumerate from the remote, never from the disk.

---

## 2. PipelineNews — the deploy jam

Symptom from the Actions API: `Deploy PipelineNews Pages` had **27 of 28 sampled runs failing**.

Logs unreachable, so the gate was run locally against a clean checkout of `origin/main`:

```
python atman/202608262014-build-pages.py --generation latest --stage _site \
       --timestamp-folder-release 202608291447-pipelinenews

PAGES BUILD GATE FAILED: live pointer commit is not deployment HEAD
  atman/202608262014-build-pages.py:904
```

The gate requires the commit that last touched `state/live-set.json` to **be** HEAD.

```
pointer  187ed63  2026-08-29 15:22 UTC   state/live-set.json
HEAD     6e40226  2026-09-02 06:34 UTC   (+191 commits)
```

And `pages.yml` triggers on `releases/**`, which is exactly where daily feature work lands. So
every ordinary push starts a deploy the gate is guaranteed to refuse. Not flaky — a contradiction
between the trigger set and the only condition the gate accepts.

At first measurement: **24 consecutive failures**, last success 2026-08-30 11:13 UTC, **138 commits**
of merged work unpublished. By the end of the session it had reached **25**.

This also answered a question the user asked much later — *"I don't even know which gridatlas or
pipelinenews is the latest version"*. The live pointer says `202608291447`; `main` had release
folders up to `202609021945`. The live site genuinely is not the latest, and this is why.
Confusing it further, `globalgrid2050.com/pipelinenews_intelligence/<stamp>/` **does** serve,
because that path deploys from a different repository that is not jammed. Two publication routes,
disagreeing.

---

## 3. GridAtlas — the deep link, and a theory I disproved

The user reported grid compute not working on mobile via a Pipeline News MAP link. The coordination
board carried a diagnosis from another session ending: *"What I cannot do from here, and will not
pretend otherwise: load the page."*

Loaded it. Findings, in order:

**The standing suspect was wrong.** The board blamed the v9.76 migration that moved six modules —
geodesy among them — out of the sandbox into `substation-intelligence`, shared via
`window.__GRIDATLAS_MODULES__`.

```js
window.__GRIDATLAS_MODULES__  ->  11/11 resolved, geodesy present
__GRIDATLAS_TOPOLOGY__.parsedProduct  ->  921 sites, 2679 nodes, 1392 circuits
```

The registry resolves, geodesy runs, distances compute. The module-boundary theory is disproven.

**WRONG, mine, caught by re-reading:** I first reported `sites: 0` and concluded the product had
not indexed. `T.sites` is a **number** (921), not a collection; I had called `len()` on an integer's
absence. The product was fully parsed all along. Corrected before it reached the user.

**The real fault is the name join.** The site index is whole-string exact:

```
site('CLEVE HILL')                       -> CLEH
site('Cleve Hill')                       -> CLEH
site('Cleve Hill 400kV Substation')      -> null
site('Cleve Hill Solar Park Substation') -> null
site('London Array OWF SVC pods')        -> null
```

**WRONG again, and this one reached the user before correction:** I concluded the join was exact
and that essentially all suffixed names fail. Then the user supplied a working card — Botley West,
where `Cowley Substation` binds to NESO `COWL`. So a normaliser exists above the raw index. Found it:

```js
const NOISE = /\b(SUBSTATION|SUB STATION|SUBSTN|GRID|SUPPLY|POINT|GSP|NATIONAL|POWER|
                 STATION|WIND|FARM|WINDFARM|OFFSHORE|ONSHORE|EXTENSION|
                 400KV|275KV|132KV|66KV|33KV|NGET|SSE|SP|SHE)\b/g;
```

That is what makes Cowley work. It is also what causes the real defect — see `01-findings.md`.

Lesson recorded: when a user says a thing worked, believe them and go looking for the second
code path. The board entry made the same mistake in the opposite direction and had to append
its own correction.

---

## 4. The estate census

Built a parallel scanner: `--shared` clones (instant, no object copy) plus a fetch of only the
delta, 20 workers, git stats and the Actions API concurrently.

- 15 repos, first pass: **44.7 s**
- Deep pass with tree stats, extensions, branch distances, HTTP probes: **41.9 s**
- Lines of code across the estate: **5.2 s**
- Datapoints across 1,246 unique data blobs: **12.0 s**
- Parquet, from footer metadata: **20.0 s**

GPU and NPU were requested and are not applicable: git object walking, HTTP and JSON parsing are
pointer-chasing and I/O. The binding constraint was GitHub's 60 req/hour, not silicon.

Findings recorded in `02-measurements.md`. The two that mattered:

**The line count was not what it appeared.** 27,907,565 total text lines, of which only
**830,985** are code, markup or config. 97% is committed data. A line count on this estate
measures GeoJSON, not work.

**The datapoint count nearly doubled after a second look.** First pass counted text formats only:
98,164,271. Then 773 parquet files — 190.7 MB, invisible to a text scan — added **96,178,149**.
Total **194,342,420** on unique content, 160.3M more if duplicate release copies are counted
(48% of data bytes are duplicates; one file appears 54 times).

Lesson recorded: enumerate formats before counting, and dedupe by git blob SHA. Both errors were
mine and both were caught only because the user pushed on the number.

---

## 5. Homepage work, under governance

The user asked for the dashboard on the homepage. The artifact URL is private to their Claude
account, so it was self-hosted in the repo instead — a private link on a public page is a login
wall for every visitor.

`globalgrid2050/index.html` carries two constraints not visible in the file:

1. `homepage_versions/README.md` requires a numbered snapshot with recorded line/word/char counts
   and a plain-English change intention **before** any edit.
2. `scripts/catalogue_gridatlas_v9.py` fails closed unless the V8 sentinel —
   `    { name:"UK Energy Atlas Grid Overlay V8", url:"./repd_grid_atlasv8/" },` with exactly four
   leading spaces — appears once byte for byte, and its route appears once in the whole file.

Five generations shipped, each verified before commit: sentinel once, route once, both
`GRIDATLAS_V9_AUTOMATION` markers intact, and every pre-existing `name:` and `note:` string
byte-identical.

| stamp | change | snapshot |
|---|---|---|
| 202609021858 | publish the scan, link it from About & Media | v015 |
| 202609021923 | remove the note from the row | v016 |
| 202609021924 | rename row to `Log`; new generation without the username | v017 |
| 202609021937 | rebuild as a vertical scan log; widen what is measured | v018 |
| 202609021952 | strip every name; count lines of code | v019 |

**WRONG, caught before commit:** my first snapshot was `homepage_v012.html`. I had listed the
folder *before* fast-forwarding, and the incoming commits had already added v012–v014. The `cp`
overwrote a real snapshot, which that README forbids outright. Restored v012 to its original hash
`1173ddc0…` and took v015 instead. Lesson recorded: fetch first, then enumerate.

Every deploy verified by SHA-256 against the live URL, both the page and the homepage.

**A trap worth recording.** The anonymisation request was nearly satisfied cosmetically: the
*rendering* used ordinals while the embedded JSON payload still carried every repo name, author,
branch, workflow name, commit subject, file path and URL — one View Source away. That generation
was thrown away and the payload rebuilt from a whitelist of numeric fields. 95,700 bytes became
48,933. Lesson recorded: redact the payload, never the view.

---

## 6. pandapower and attribution

`Ventusltd/pandapower` is a **fork** of `e2nIEE/pandapower` — 828 MB of someone else's code, and
excluded from every count in this session.

Licence is **BSD 3-Clause**. It permits use, modification, commercial and closed-source
redistribution, subject to retaining the notice and not using the copyright holders' names to
promote a product. There is no obstacle to what was asked.

The user's instinct — *"I want to attribute the correct people not middlemen"* — reframed it
better than the licence question did. Fraunhofer authored pandapower; they did not author
power-flow. Full attribution stack in `04-licensing.md`.

The decisive argument turned out to be architectural rather than legal: pandapower is
Python/NumPy and the Atlas runtime is client-side JS cartridges. It cannot ship there. So it
belongs as an offline validation oracle, not a dependency — which is also the stronger
credibility claim.

---

## 7. The Cowley card, verified figure by figure

Recomputed every claim on the Botley West card from `gb-transmission-network.v1.json`, without
reading the cartridge, so agreement is real agreement.

Everything verified except one number. Circuits, seasonal rating ranges, reactive compensation,
planned changes with their per-year addition/change/removed breakdown, the year span, the reach
list, and — impressively — the fault-current scoping. There are 18 rows at COWLEY; the card
correctly reports only the **15 peak-demand** ones. The 3 minimum-demand rows run 11.4–28.8 kA and
would have widened the range misleadingly. Someone thought about that.

The one error is the site-wide transformer count. Detail in `01-findings.md`.

**WRONG, mine, caught immediately:** my first verification reported four divergences. Three were
my own bug — `Counter[400]` and `Counter[400.0]` are the same key in Python, so `.get(400) + .get(400.0)`
double-counts. Only one divergence was real. Recorded because it is exactly the kind of error that
would have been reported as someone else's defect.

---

## 8. Provenance, verified to the cell

Full chain in `03-provenance.md`. The headline: all three NESO source documents were re-downloaded
during the session and matched their pinned SHA-256 **byte for byte**, and the card's `12.4 kA`
was traced to sheet `D3.1`, row `137`, column 4 of the NESO workbook: `12.4764249011479`.

This is stronger provenance than most commercial tools ship, and it took about ten minutes to audit
from scratch without asking the user anything.

---

## 9. The corridor scope, and the gate that killed it

Scoped a routed-corridor engine: replace the straight line with a road-routed path, satnav style,
penalising railway crossings. Measured the route factor first — median **1.16** overall, **1.34**
for cable circuits, **1.13** for overhead — and found the design's own acceptance test sitting in
the data: NESO publishes `cable_km` for circuits that are fully buried, so a router can be checked
against real built lengths.

Ran that gate through a subagent before building. **It failed.**

```
straight line, raw                        25.4%  median abs error
road-routed, primary+trunk+motorway       20.3%  beats straight on 52.6% of 95   FAIL
straight line x one constant (k=1.245)     8.4%  8.6% leave-one-out              PASS
```

A single multiplier beats a 275,585-node routing graph. Verified independently: my recompute gave
k=1.245 → 8.45% against the agent's 1.243 → 8.34%.

The railway-penalty design was also wrong. Sweeping the penalty 0 → 20 km made median error worse
**monotonically**, 20.26% → 33.32%. Best penalty is zero; crossing count correlates with error at
Spearman −0.12. Roads cross railways at bridges that already exist — I had suspected this and
proposed weighting it anyway.

Full study, including the bound on the negative result, in `05-corridor-study.md`.

---

## What this session got wrong, collected

Kept together because the pattern matters more than the individual errors.

| wrong | how it was caught | lesson |
|---|---|---|
| Scanned 15 repos as if that were the estate | user said so | enumerate from the remote |
| Read `T.sites` (an integer) as an empty collection | re-reading the shape | check the type before the value |
| Declared the name join exact and universally failing | user supplied a working card | when a user says it worked, find the second code path |
| Counted text formats only; missed 773 parquet files | user pushed on the number | enumerate formats before counting |
| Overwrote `homepage_v012.html` | `git status` said `M` not `??` | fetch before enumerating |
| Anonymised the view, not the payload | grepping my own build | redact the data, never the render |
| `Counter[400]` vs `Counter[400.0]` double-count | recount without the bug | verify your verifier |
| Proposed railway crossing penalties | the sweep made it worse | measure the weight, don't assume it |

Six of eight were caught by measuring again rather than by reasoning harder.

---

## Open at session end

- `estate_scan/202609021858/`, `.../202609021924/`, `.../202609021937/` are superseded but still
  serve. The 1858 generation carries the user's username; 1937 and earlier carry every repository
  name in their payload. Unlinked, publicly reachable, deletion not authorised.
- The `estate_scan/**` path added to `deploy-pages.yml` is **untested** — all three commits also
  touched `index.html`, which already matched the filter.
- Geocoding the 384 unlocatable connection points: not started.
- The 34 colliding name keys: diagnosed, not fixed.
- The transformer double-count: diagnosed, not fixed.
- Chrome extension disconnected for part of the session; the vertical reveal animation of the Log
  was verified as text under a stubbed DOM in Node, never watched.
