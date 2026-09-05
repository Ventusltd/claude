# Overnight lane board — 2026-09-05

**This file is how Codex, and anyone reviewing by morning, sees what the lanes
did.** It is written to GitHub, not held on the laptop: anything unpushed is
invisible. Every lane appends one row per shipped unit of work and pushes it in
the same commit as the work, or immediately after.

Times are UTC. Vikram's clock is BST, +1.

## Lanes tonight

| lane | owns | must not touch |
|---|---|---|
| **A** — main session `184379c4` (vikra-11) | `globalgrid2050`, `gridatlas`, `claude` | `pipelinenews` |
| **B** — subagent, Pipeline News | `pipelinenews` | `gridatlas` |
| **Codex** | its own `codex/*` branches | any lane's `main` commits |

`gridatlas/atlas/current.json` and `globalgrid2050/index.html` are single files
every generation must touch and git cannot merge meaningfully. One lane each.

## Log

| UTC | lane | repo | commit | what | verified |
|---|---|---|---|---|---|
| 01:25 | A | claude | `31bc1a2` | carry-on handover filed in the repo, where it can be found | github 200 |
| 01:31 | A | claude | `6e85062` | renamed it `00-LOG.md`, the entry point CLAUDE.md already documents | github 200 |
| 01:39 | A | globalgrid2050 | `a4faffc1` | front page shows only what is being built now; old page archived byte-identical at `/historical_builds.html`; search wired for the first time; `catalogue-gridatlas-v9.yml` retired with its reasoning | live 5,934 bytes, was 111,836 |
| 01:45 | A | globalgrid2050 | `6ecc0dc0` | carried the 15 published-version labels the exact-commit gates require, read from the archive rather than retyped; corrected v9.7/v9.6.2 to the estate's own CANDIDATE / LIVE VALIDATED labels | gates re-running |

## Open at the time of writing

- Six exact-commit gates (V9.3–V9.7) went red on `a4faffc1` and are re-running on
  `6ecc0dc0`. They were green on `5260db10`, so the red was lane A's change, read
  from the run log, not guessed.
- `Verify published versions are reachable` was already failing before tonight.
  Pre-existing; not touched yet.
- Two Pages deploy workflows run on every push to `globalgrid2050`
  (`Deploy GlobalGrid2050 Pages` and `Deploy Jekyll…`). Noted, not changed.

## Defects named by Vikram tonight, 2026-09-05

Verbatim, so nothing is softened in the retelling:

1. *"other technologies sort also brings up solar"* — Pipeline News technology
   filter leaks. **Lane B, priority.**
2. *"the UI via deeplink into gridatlas can be awkward as the cards get in the
   way"* — arrival from a deep link is obstructed by cards. **Lane A.**
3. *"the scoping menu has nothing it seems"* — SCOPE menu appears empty. **Lane A.**
4. *"the polyzone undergrid doesnt work"* — **Lane A.**
5. Attribution must move out of the menus, into the ABOUT panel. **Lane A.**
6. The MAP button must be fixed. **Lane A.**
7. As many REPD deep links tested as possible. **Lane A.**

The engine graph is the map for several of these:
https://ventusltd.github.io/ventus-grid-engine/?graph=engine-graph
It shows five separate deep-link/bucket implementations and marks them
DUPLICATES of one another. Where a fix has to be made in five places, it has
been made in one — that is the shape of defects 1, 2 and 7.
