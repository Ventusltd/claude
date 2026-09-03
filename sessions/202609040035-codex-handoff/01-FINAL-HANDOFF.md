# Final Codex overnight handoff

**Frozen 202609040057 BST / 202609032357Z.** The user ordered this window to
stop and hand control to a fresh `codex --yolo` window. All three subagents were
stopped. No further feature, merge, release, or homepage work may be attributed
to this window after this receipt.

The first record, `00-RESUME.md`, explains the estate and the original pause.
This file supersedes its branch-head and completion status where they differ.

## Start the successor

From a new PowerShell window, run `START-NEW-CODEX-WINDOW.cmd` in this directory,
or run the exact command printed at the end of this file. Do not restart the
computer first. The resource governor is live and a reboot would discard its
state without improving the handoff.

The successor is CEO for the overnight shift. It may use subagents, deterministic
local CI, and repository-owned GitHub Actions. It must keep promotion serial:
candidate -> hostile review -> clean integration -> exact-head CI -> public bytes
and browser proof -> next candidate. Never manufacture a release to increase a
count.

## Exact remote state at freeze

### Pipeline News: classifier is on `main`

- Remote `main`: `25f03422d12ed6e5bfca860a825d6273c2e0c296`
- Evidence branch: `codex/202609040002-pages-classifier`
- Evidence head: `2aea6a0ef9dfb27d1f6859b7535bcf6a3d2b618b`
- Material iteration head: `2ae7a6920aa5b7b7cee9cd3cbce894b0ed9dcbe5`
- Frozen base: `937b8c019074e40bebbc7edf5d8ef8d1751e034e`
- Ledger: 34 attempts, iteration 1 explicitly failed/superseded, 33 qualifying
  iterations (2 through 34).

The clean integration passed 26 classifier tests, 15 workflow checks, the
candidate-workflow check, current source-only closure, live-pointer routing,
historical additive-push replay, YAML parsing, and diff hygiene. GitHub run
`33819134539` succeeded on exact commit `25f0342`; receipt artifact digest:
`sha256:a24664d46c22e1b2c99b9ded422865e6baa5538c27df0de7d141361618d30d1d`.
Do not redo or revert this work. Fetch before judging later Pipeline activity.

### CVAA: four vaccines are on `main`

- Remote `main`: `a1678df0eaaddb0cb96b1495dd32ce9a59078915`
- Evidence branch: `codex/20260904-immunisation`
- Evidence head: `6d7e62085993be789fc8bbed6892c5e46073eb85`
- Frozen base: `e696dd5289cf612d690a3d86a44499b22db8909e`

`node tools/selftest.mjs` and `node inoculate.mjs . --no-write --json` passed.
The vaccines cover serial release cutting, source/receipt classification,
separate promotion authority, and data-only observers. The six pinned-action
warnings and two monotonic-generation warnings were pre-existing baselines.

### GridAtlas: candidate only; promotion is stopped

- Remote branch: `codex/20260904-gridatlas-30x`
- Candidate head: `b73247803377233069acfeff415ecad4e8391cb2`
- Frozen base: `7e3bdcbdab58ab22bdcd4d8aedc068baa7d02c6d`
- Remote `main` at freeze: `cef7b8fd8b6e95d81618bd99c8d50017bafaac95`
- Count: 41 attempted iterations; 40 qualifying; iteration 30 (`64320b5`)
  explicitly rejected and superseded by iteration 31.
- Candidate proof: PASS, iteration 41, 226 checks.
- Existing composed-cartridge proof: PASS, four suites including 114/114 and
  746/746, but against the stale v9.98 base.

Hostile review verdict: **PASS as isolated candidate evidence; FAIL/STOP for
promotion or any claim that the live product is fixed.** The branch is one
commit behind v9.99. Everything new lives under
`atlas/codex/20260904-finding-loop-30x`; the served Map, Pipeline and World
surfaces import none of it. There is no real DOM/browser proof and no exact-head
GitHub Actions receipt. One untracked, unexecuted ledger helper remains at
`atlas/codex/20260904-finding-loop-30x/build-ledger.mjs`; it is not product code
and was deliberately not committed after the stop order.

Before promotion, the successor must:

1. Fetch and rebase or merge current `main`, then rerun all candidate, current
   composition, workflow-static, and fixed-base whitespace gates.
2. Wire the accepted core into the actual served composition without changing
   its source predicates or presenting a road/cable route that does not exist.
3. Prove a cold/throttled `393x852` journey and a `1400x900` journey in two real
   browser profiles: MEASURING -> sourced result or explicit reason, time to
   state, accessible announcements, one identity surface, no canonical/fallback
   race, correct history restoration, and no console error.
4. Push the rebased exact head and require a green exact-head Actions receipt.
5. Only then integrate serially, cut one meaningful release, publish it without
   removing older homepage versions, and test the exact public bytes and links.

Markinch remains the fixed acceptance case: `repd_ref=155`, biomass, 65 MW,
`56.20118,-3.162255`. Preserve the distinct predicates: Pipeline circuit
2.470 km (275 kV); Pipeline all-voltage substation Glenrothes 2.485885849 km;
Atlas nearest >=400 kV source feature 2033 at 28.819562529 km; named >=400 kV
Smeaton at 33.503070342 km. A road route remains `NOT_COMPUTED`.

### Spiders: review branch only

- Remote `main`: `de53761486d2686254843d6a4e4df315a8fc05fe`
- Remote branch: `codex/20260904-60x`
- Branch head: `098a81f635acbb1d2c5c423b14fe6f029f2aed23`
- Frozen base: `de53761486d2686254843d6a4e4df315a8fc05fe`

The branch contains the canonical 60-slot data-only control graph, deterministic
validator/proof workflow, and a bounded pinned Llama advisory workflow. Tests
passed for 60 slots / 30 qualified / zero structural failures, malformed 59-slot
rejection, YAML parsing, workflow static rules, and a disabled Llama
prepare/seal/validate fixture. Actual cloud model inference has not run. Review
before merging; merging to `main` is what enables the path-scoped Actions runs.
The requested bounded estate registry, shard/aggregate matrix, and cloud-vs-local
survey are still unimplemented; the incomplete generated registry was removed.

### Local model governor

- Branch: `codex/20260904-overnight-governor`
- Head: `426f0840645de54f447e8ebacb94354b4a302006`
- Live PID at freeze: `37752`
- Bounded until: `2026-09-04T07:28:23Z`

It permits one serialized Qwen 4B request on the RTX Ollama listener `:11434`
only when system available memory is at least 3,072 MiB. The Intel listener
`:11435` is deliberately down: this iGPU has shared system memory rather than
independent VRAM and was increasing paging. Do not restart it merely to raise
utilisation. Use the SSD for durable queues, receipts, indexes and caches, not as
a substitute for RAM. At freeze PID 37752 was alive; no new Llama work should be
forced when admission is false.

## Counts that must not be conflated

Pipeline produced 33 qualifying classifier iterations and Grid produced 40
qualifying isolated candidate iterations. Those are evidence iterations, not 73
public versions. Pipeline's classifier was promoted once; Grid's candidate has
not been promoted. Continue toward meaningful public releases, but reject no-op,
stamp-only, or count-padding generations.

## Remaining estate work

- Complete Grid integration, exact-head CI, two-browser acceptance, release,
  homepage publication while retaining older versions, and public retest.
- Review and, if accepted, serially merge the Spiders branch; inspect its first
  real Actions receipts before enabling more cloud work.
- Build the bounded estate survey as deterministic repository work with
  max-parallel 4 and artifact receipts. GitHub Actions is not a generic compute
  or GPU farm; standard hosted runners offer no useful GPU lane.
- Keep the authorized 18,148-character Grid stylesheet hoist separate from the
  finding loop and never raise the 368,640-character ceiling.
- Resolve Pipeline's three duplicated identities (47.30 MW) at the source
  boundary; fix release-cutter applicability for repair-only/no-asset
  cartridges; repair the structurally red globalgrid2050 V9.7 exact-commit gate
  by pinning bytes or changing its truthful assertion, never by deleting it.
- Preserve the serial loop: ship -> homepage -> public test -> next change.

## Resume reading order

1. This file, then `00-RESUME.md` for full background.
2. Repository `CLAUDE.md` files and
   `sessions/202609040020-command-log/00-COMMAND-LOG.md`.
3. `sessions/202609032304-codex-cto-control/` and the current coordination boards.
4. Fetch every repository and compare these remote heads to current
   `origin/main`; never assume the laptop's dirty primary checkout is current.

Do not clean, reset, stash, amend, or stage unrelated files in shared primary
working trees. Use isolated worktrees. Retry an exact Git fetch/push if Windows
Schannel transiently returns `SEC_E_NO_CREDENTIALS`.

## Exact manual start command

```powershell
codex --yolo -C "C:\Users\vikra\OneDrive\Documents\GitHub" "Read C:\Users\vikra\OneDrive\Documents\GitHub\.codex-worktrees\claude-cto-handoff\sessions\202609040035-codex-handoff\01-FINAL-HANDOFF.md first. Continue the overnight CEO loop autonomously from the recorded exact heads. Use subagents for bounded work, keep promotions serial, and do not ask for trivial approvals."
```
