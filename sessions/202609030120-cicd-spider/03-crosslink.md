# 03 — the estate crosslink graph

Measured 2026-09-03, pass 1. Machine-readable companion: `crosslink.json`,
written in `federation_contents_cartridge.v1` shape so it can be adopted
upstream without translation. **Nothing was written into
`data-federation-map-for-globalgrid2050-all-repos` — that is not my lane. This
artefact is ready to adopt.**

## What existed before this

`data-federation-map-for-globalgrid2050-all-repos` holds a real schema and a
real UI scope, and covers **12 of 33** repositories under
`data/federation_map/cartridges/provenance=declared/`. Four of those twelve
manifests carry `"edgeCount": 0`. The `contents` cartridge for
`globalgrid2050` has 11 edges, all of type `contains` — intra-repo containment,
not federation. **There is not one inter-repository edge in the map.** The
covered set omits `gridatlas`, `pipelinenews`, `data-grid-gb`, `cvaa`,
`data-centres-gb`, `grid-distance-maths`, `spiders`, `companies` and every
repository created since 2026-07-01.

The schema for crosslinking exists. The crosslinking did not.

## Method

Static extraction from 18 local working copies (the 18 of 33 org repos that are
cloned on this machine). Every edge cites a file and a line. Nothing is taken
from a declaration; if I could not point at a line, I did not record an edge.

Edges are tiered by where the evidence lives, because a URL in a session log is
a *mention* and a URL in a cartridge is a *dependency*:

| tier | edges | meaning |
|---|---:|---|
| **shipped** | 274 | live code, config, workflows, published surfaces |
| record | 127 | session logs, threads, governance briefs, `codex/` |
| doc | 59 | README and prose |
| archive | 64 | `archive/`, `workflow-archive/` |
| **total cross-repo** | **524** | |

Everything below counts **shipped** only. Kinds: 150 published-surface,
96 contract, 18 repo-ref, 9 runtime-data, 1 api.

## Load-bearing repositories — highest in-degree

| repo | in | depended on by |
|---|---:|---|
| `globalgrid2050` | 10 | companies, data-centres-gb, data-federation-map, data-gb-electricity, data-gridatlas, data-interconnectors, gb-electricity-ui, gridatlas, pipelinenews, spiders |
| `gridatlas` | 7 | chatgpt-audits, companies, cvaa, data-grid-gb, data-gridatlas, globalgrid2050, pipelinenews |
| `pipelinenews` | 5 | chatgpt-audits, companies, data-gridatlas, globalgrid2050, gridatlas |
| `data-centres-gb` | 4 | data-federation-map, globalgrid2050, gridatlas, pipelinenews |
| `data-gb-electricity` | 4 | data-federation-map, globalgrid2050, gridatlas, pipelinenews |
| `data-federation-map…` | 3 | data-centres-gb, globalgrid2050, spiders |
| `globalgrid2050-hompage` | 2 | globalgrid2050, spiders |
| `companies`, `data-grid-gb`, `data-gridatlas`, `gb-electricity-ui`, `registry_of_all_content…`, `reports`, `solar-electrical-topology…`, `spiders` | 1 each | |

`globalgrid2050` is the published surface everything points at; `gridatlas` is
the application everything composes into. Breaking either breaks the most.
`data-grid-gb` has in-degree 1 and is nonetheless the sharpest risk in the
estate, because that single edge is unpinned and feeds a shipped map — degree
measures blast radius, not fragility.

## Mutable edges — defect F5, five of them, estate-wide

An unpinned edge is a surface where a product can change under a shipped
consumer with no cut in between.

| from | to | ref | path | evidence |
|---|---|---|---|---|
| `gridatlas` | `data-grid-gb` | **`main`** | `derived/connection-points.v3.json` | `atlas/cartridges/202609012045-substation-intelligence-v9-63.js:1474` |
| `gridatlas` | `data-grid-gb` | **`main`** | `derived/gb-transmission-network.v1.json` | `atlas/cartridges/202609012141-sld-sandbox-v9-8.js:1415` (and the 2211 / 2234 successors) |
| `gridatlas` | `data-gb-electricity` | **`main`** | `derived/price-decade-rollup.json` | `atlas/current.json:292` |
| `pipelinenews` | `globalgrid2050` | **`main`** | `dist/major_project_news_v9_5_1.json` | `index/202608261927-compile-index.mjs:128` |
| `globalgrid2050` | `gridatlas` | **`main`** | `atlas/current.json` | `scripts/verify_published_versions.py:54` |

Against four that ARE pinned, all of them in `pipelinenews` and `spiders`:
`companies@148335a6`, `data-centres-gb@c5dfdee3`, `data-centres-gb@43286474`,
`globalgrid2050@88894beb`. So the estate already knows how to pin. It pins in
the repository that was hardened and does not pin in the repository that ships
the map.

### The one that is loaded right now

`data-grid-gb` commit `b91e45b` ("20260903: correct transformer identity and
fail-closed joins", 2026-09-03T01:21Z) sits on branch
`codex/20260903-phase0-integrity`. `origin/main` is still `1c9909d`, so the edge
has not fired. Semantic diff of `derived/connection-points.v3.json` between the
two:

    schema             data-grid-gb.connection-points.v3    UNCHANGED
    connection_points  886 -> 886
    with_location      502 -> 489          13 sites lose their coordinates
    with_fault_current 605 -> 605
    changed fields     join_context_key, location, transformers
    points with at least one changed field   882 of 883 matched by name
    example            ABHAM transformers 4 -> 2

The consumer's defence is `REQUIRED_SCHEMA = 'data-grid-gb.connection-points.v3'`
and it fails closed on mismatch. **That defence guards the wrong axis.** It
catches a change of shape and is blind to a change of values inside the same
shape. On merge, the same shipped cartridge, at the same generation stamp,
will state different transformer counts and drop thirteen pins, and nothing in
the estate will record that it happened.

The remedy is one of three, and any one is enough: bump to
`connection-points.v4` for a semantics change that moves 882 of 886 records;
or carry a `products_generation` / content digest inside the payload that the
cartridge asserts alongside the schema; or pin the ref and move the data cut
and the map cut as one event.

## Contract edges — the strongest, because the consumer refuses on mismatch

26 distinct shipped contract edges. The important ones:

    gridatlas    -> data-grid-gb         connection-points.v3, transmission-network.v1
    gridatlas    -> data-gb-electricity  price-decade-rollup.v2
    gridatlas    -> data-centres-gb      v1
    gridatlas    -> data-gridatlas       v1
    pipelinenews -> data-gb-electricity  v1
    pipelinenews -> gridatlas            v1, v3
    globalgrid2050 -> pipelinenews       v1..v4

Every one of these is a real refusal in code, not a declaration. They are the
part of the estate that already works.

## Cycles

Eleven 2-cycles in the shipped graph:

    companies <-> pipelinenews          data-grid-gb <-> gridatlas
    data-centres-gb <-> data-federation-map    data-gridatlas <-> gridatlas
    data-centres-gb <-> globalgrid2050  globalgrid2050 <-> gridatlas
    data-federation-map <-> globalgrid2050     globalgrid2050 <-> pipelinenews
    data-gb-electricity <-> globalgrid2050     globalgrid2050 <-> spiders
    gridatlas <-> pipelinenews

Most are benign: a data repo names the app that consumes it in prose or in a
contract, and the app names the data repo back. The one worth watching is
`globalgrid2050 <-> gridatlas`, because both directions are live and unpinned —
`globalgrid2050/scripts/verify_published_versions.py` reads
`gridatlas@main/atlas/current.json` to decide whether the homepage is truthful,
while gridatlas publishes into the globalgrid2050 surface. That is a truth check
whose input its own subject controls, and it is the check that is failing right
now (see `01-drift.md`, D1).

## Dangling and orphans

- **Dangling repo references:** one, a UUID-shaped string
  (`f1f11bc1-ba88-…`) matched by the API pattern, not a repository. No edge in
  the graph points at a repository that does not exist. Path-level 404s are NOT
  yet verified — that needs live HTTP and I have deferred it to protect the
  60/hour budget; it is queued for pass 2.
- **Orphans:** `claude`, `codex-chatgpt`, `gemini`, `grid-distance-maths` have
  no shipped in- or out-edges. The first three are agent-notes repositories and
  are correctly orphaned. **`grid-distance-maths` is not**: it exists to unify
  the estate's geodesy, its 446/446 parity gate passes, and no shipped code in
  any repository imports it. It is a solved problem nothing has adopted.

## Coverage limit

15 of 33 repositories have no local clone and were not scanned: Mahabharata,
Solar-PV-Hybrid-and-off-grid, architecture, data_uk_dno_and_tso,
globalgrid2050-hompage, pandapower, pv-arc-protection-circuit,
registry_of_all_content_in_repos_and_dependencies, reports, seed-data,
solar-electrical-topology-analysis-engine-text-based,
solar-repowering-whitepaper, uk-dno-data, v11, youengineer-code-review.

All but one were last pushed before 2026-08-31, so they are cold. The
exception, `registry_of_all_content_in_repos_and_dependencies` (pushed
2026-08-31), overlaps this artefact's purpose and should be read before this
graph is adopted. In-degree for the unscanned set is therefore a floor, not a
count.

## Environmental hazard for anyone rebuilding this graph

`git clone` of `gridatlas` fails on Windows for 12 files under
`nightly/202608310015-gridatlas-overnight-next-versions/runs/` with
"Filename too long". The clone reports success at the top level and leaves an
incomplete tree, and nothing announces it. Any scan of a fresh gridatlas clone
on this platform under-reports by those paths. `core.longpaths=true` plus a
Windows registry `LongPathsEnabled` are both required; neither is set here.

This graph was built from the canonical working copies under
`OneDrive/Documents/GitHub/`, which are complete, so it is unaffected — but a
later instance that clones to scratch to avoid dirty trees will hit it.

## Correction, 2026-09-03T01:45Z — the mutable edge count is now 2, not 5

gridatlas v9.83 (4a17fa3) added `atlas/modules/202609030137-pinned-products.js`
and pinned all three of its runtime fetches to a commit with a SHA-256 and a
byte count:

    data-grid-gb        1c9909d  derived/connection-points.v3.json        11e28859   2,896,561 B
    data-grid-gb        1c9909d  derived/gb-transmission-network.v1.json  fc331cc2  10,069,966 B
    data-gb-electricity d310e3c  derived/price-decade-rollup.json         18da5059       6,873 B

Neither composed cartridge (`202609030137-sld-sandbox-v9-8.js`,
`202609030137-substation-intelligence-v9-63.js`) fetches a branch. Older
cartridge generations in `atlas/cartridges/` still contain `main/` URLs, but
they are historical generations and are not in `atlas/current.json`'s composed
set — a scan that counts them counts retired code.

**Remaining mutable runtime edges, estate-wide: 2.**

    pipelinenews   -> globalgrid2050@main  dist/major_project_news_v9_5_1.json
                      index/202608261927-compile-index.mjs:128
    globalgrid2050 -> gridatlas@main       atlas/current.json
                      scripts/verify_published_versions.py:54

The second is the more interesting of the two: it is the publication-truth gate,
so it reads its own subject's branch to decide whether the homepage is honest.
It cannot distinguish "the homepage is stale" from "gridatlas moved", and it is
currently red in CI (D1). Pinning it would defeat its purpose — it is *supposed*
to follow the live pointer — which makes it a legitimate mutable edge rather
than a defect. Recording the distinction matters: F5 is about edges that should
be pinned and are not, and this one should not be.
