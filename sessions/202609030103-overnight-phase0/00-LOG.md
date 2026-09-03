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
