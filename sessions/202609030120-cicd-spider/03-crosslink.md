# 03 — the estate crosslink graph

Regenerated 2026-09-03T02:12Z across **32 of the 33 repositories** (only
`pandapower`, an upstream fork last pushed 2026-04-25, is unmeasured).
Machine-readable companion: `crosslink.json`, in
`federation_contents_cartridge.v1` shape so it can be adopted upstream without
translation. **Nothing was written into
`data-federation-map-for-globalgrid2050-all-repos` — that is not my lane. This
artefact is ready to adopt.**

## What existed before this

The federation map holds a real schema and covers **12 of 33** repositories
under `data/federation_map/cartridges/provenance=declared/`. Four of those
twelve manifests carry `"edgeCount": 0`. The `contents` cartridge for
`globalgrid2050` has 11 edges, all of type `contains` — intra-repo containment.
**Not one inter-repository edge exists in the map.** The covered set omits
`gridatlas`, `pipelinenews`, `data-grid-gb`, `cvaa`, `data-centres-gb`,
`grid-distance-maths`, `spiders`, `companies` and everything created since
2026-07-01.

## Method, and why the tiers decide everything

Static extraction from working copies. Every edge cites a file and a line;
nothing comes from a declaration. Edges are tiered by what the evidence *is*,
and **only `shipped` is a dependency**. Getting this wrong is how a graph
lies — the raw scan found 6,854 cross-repo edges and 336 of them are real.

| tier | edges | what it is |
|---|---:|---|
| **shipped** | **336** | live code, config, workflows, published surfaces |
| catalogue | 6,116 | `registry_of_all_content…` inventory rows (RH7) |
| record | 247 | session logs, threads, governance briefs |
| doc | 79 | README and prose |
| archive | 64 | `archive/`, `workflow-archive/` |
| superseded | 8 | retired gridatlas cartridge generations (RH8) |
| declared | 4 | a URL inside a `.json` — a declaration, never a fetch (RH9) |

Shipped edges by kind: 160 published-surface, 152 contract, 18 repo-ref,
**5 runtime-data**, 1 api.

## Load-bearing repositories

Two different questions, two different answers. **Edges** measures how much
would have to be rewritten; **repos** measures how many teams would notice.

| repo | in-edges | in-repos |
|---|---:|---:|
| `globalgrid2050` | **152** | **14** |
| `pipelinenews` | **80** | 5 |
| `gridatlas` | 56 | 7 |
| `data-federation-map…` | 9 | 5 |
| `data-centres-gb` | 7 | 4 |
| `data-grid-gb` | 7 | 1 |
| `data-gb-electricity` | 6 | 4 |
| `solar-electrical-topology…` | 5 | 1 |
| `registry_of_all_content…` | 4 | 3 |
| `reports`, `spiders`, `globalgrid2050-hompage`, `data-gridatlas`, `gb-electricity-ui` | 1–2 | 1–2 |

`globalgrid2050` is the published surface everything points at. **`pipelinenews`
is second at 80 in-edges — and it is the repository whose deploy has been frozen
for two days (D8).** That pairing is the single most useful line in this file:
the estate's second most depended-on repository cannot publish.

`data-grid-gb` has in-repos 1 and is still the sharpest data risk, because that
one consumer is the map. Degree measures blast radius, not fragility.

## Mutable edges — F5, and there are now two

An unpinned edge is a surface where a product can change under a shipped
consumer with no cut in between. **Shipped tier, executable files only:**

| from | to | ref | path | evidence |
|---|---|---|---|---|
| `pipelinenews` | `globalgrid2050` | `main` | `dist/major_project_news_v9_5_1.json` | `index/202608261927-compile-index.mjs:128` |
| `globalgrid2050` | `gridatlas` | `main` | `atlas/current.json` | `scripts/verify_published_versions.py:54` |

**The second one should stay mutable.** It is the publication-truth gate, and
following the live pointer is its entire job. Pinning it would defeat it. F5 is
about edges that *should* be pinned and are not, and this is not one — recording
the distinction matters more than the count.

So the estate's real remaining exposure is **one edge**: pipelinenews compiling
against `globalgrid2050@main`.

Pinned, for contrast: `gridatlas -> data-grid-gb@1c9909d`,
`pipelinenews -> companies@148335a6`,
`pipelinenews -> data-centres-gb@c5dfdee3`.

### What changed tonight

At 01:05Z this file recorded **five** mutable shipped edges, three of them
`gridatlas -> data-grid-gb` / `data-gb-electricity`. gridatlas v9.83 (4a17fa3,
01:38Z) added `atlas/modules/202609030137-pinned-products.js`, which pins all
three by commit, SHA-256 and byte length:

    data-grid-gb        1c9909d  derived/connection-points.v3.json        11e28859   2,896,561 B
    data-grid-gb        1c9909d  derived/gb-transmission-network.v1.json  fc331cc2  10,069,966 B
    data-gb-electricity d310e3c  derived/price-decade-rollup.json         18da5059       6,873 B

Its header states the reasoning better than I did: *"a schema string defends
SHAPE and is blind to VALUES"*, with COWLEY 10→5 and ABHAM 4→2 transformers as
the measured case. **5 → 2 in 33 minutes.**

One residue: `gridatlas/atlas/current.json:292` still carries
`"reads": "…/data-gb-electricity/main/derived/price-decade-rollup.json"` as
prose describing the panel, while the composed cartridge reads that product
through the pin. Stale documentation of a fixed defect — worth a line, not a
cut.

## Contract edges — the part that already works

152 shipped contract edges, each a real refusal in code:

    gridatlas    -> data-grid-gb         connection-points.v3, transmission-network.v1
    gridatlas    -> data-gb-electricity  price-decade-rollup.v2
    gridatlas    -> data-centres-gb, data-gridatlas        v1
    pipelinenews -> data-gb-electricity  v1
    pipelinenews -> gridatlas            v1, v3
    globalgrid2050 -> pipelinenews       v1..v4

The night's lesson sits exactly here: a schema pin defends shape and is blind to
values. These edges are strong against a v3→v4 change and were, until v9.83,
defenceless against 882 records moving inside v3.

## Dangling, orphans, cycles

- **Dangling:** no edge points at a repository that does not exist. Path-level,
  8 of 41 probed shipped URLs return 404. Three are template placeholders
  (`{release_id}`, `$release_id`) and are my extractor's noise; **four are
  real** and are recorded as D6 — consumers holding a Grid Atlas published path
  that was retired. A further 19 are trailing-slash 301s that resolve 200.
- **Orphans**, 13 of 32: `Mahabharata`, `Solar-PV-Hybrid-and-off-grid`,
  `architecture`, `claude`, `codex-chatgpt`, `data_uk_dno_and_tso`, `gemini`,
  `grid-distance-maths`, `pv-arc-protection-circuit`, `seed-data`,
  `solar-repowering-whitepaper`, `uk-dno-data`, `youengineer-code-review`.
  Most are cold or agent-notes repositories and are correctly orphaned.
  **`grid-distance-maths` is the exception, and it is a real finding**: it
  exists to unify the estate's geodesy, its parity gate passes 446/446 with
  `geodesy.py` and `geodesy.mjs` agreeing, and **no shipped code in any
  repository imports it**. The only thing consuming it is a CI checkout in
  `gridatlas`'s cartridge-proof workflow. A solved problem nothing has adopted.
- **Cycles:** eleven 2-cycles. Most are benign — a data repo names its consumer
  in a contract and is named back. The one to watch is
  `globalgrid2050 <-> gridatlas`, because the publication-truth gate reads its
  own subject's branch to decide whether the homepage is honest. It cannot
  distinguish "the homepage is stale" from "gridatlas moved", and it is red in
  CI right now (D1).

## Two environmental hazards for anyone rebuilding this

1. **A Windows clone of `gridatlas` is silently incomplete.** It needs
   `-c core.longpaths=true`, and even then 12 files under
   `nightly/202608310015-gridatlas-overnight-next-versions/runs/` are left
   absent from the working tree while git reports the clone succeeded. They show
   as ` M` with `w/` empty in `git ls-files --eol`. Anyone scanning a fresh
   clone on this platform is scanning a tree that is missing files and is not
   told so.
2. **The canonical copies under `OneDrive/Documents/GitHub/` are complete**, and
   this graph was built from them — but three agents write to them
   continuously, so a scan must record the commit it scanned. There are also 13
   `.claude-worktrees/` directories under that folder whose contents duplicate
   repository files; they are excluded by scanning only names that appear in the
   GitHub API repo list.
