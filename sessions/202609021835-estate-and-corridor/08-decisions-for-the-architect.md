# Decisions for the architect — 2026-09-03, 03:00 UTC

Three things stopped tonight because they are not code decisions. Each is stated with what was
measured, the options, and what I would do — but not done, because doing them unilaterally would
be choosing on your behalf.

---

## D1 — the homepage stamp cannot be maintained by hand, and cutting it again buys nine minutes

**Measured.** GridAtlas cut ten versions in three hours. Intervals between consecutive cuts:

```
v9.80  +342 s    v9.83  +587 s    v9.86  +237 s
v9.81  +192 s    v9.84  +829 s    v9.87 +1960 s
v9.82  +506 s    v9.85  +293 s    v9.88   +96 s
```

The homepage stamp was cut twice in the same window. The publication-truth gate went
**FAIL → PASS → FAIL in fifteen minutes**, and will do so again on the next GridAtlas cut.

**The mechanism.** `globalgrid2050/index.html:103` carries `data_gridatlas_release:"…"` as a
hand-authored string, plus a `note` naming the version twice more in prose. The gate compares that
authored string against a derived one — the live pointer at `/gridatlas/atlas/current.json`. Two
values that must agree; only one moves on its own.

**Two further facts that matter.**

The catalogue compiler cannot maintain it either. `compile_root()` requires the catalogue URL to
occur **at most once**, and it has occurred twice since `6afd5dea` on 30 August, when an `os-strip`
banner was added with the same href. So `catalogue_gridatlas_v9.py` has been unable to run on this
file for four days. That is why the drift reached nine versions rather than one.

The vaccine does not catch it. `derived-state-not-authored` reports **immune** on globalgrid2050 —
its antibody looks at state files drifting from git, not at a version string drifting from a live
pointer. The rule names the right class and is blind to this instance.

**The real question, and it is not about the stamp.** The row is titled *"Current Verified
Release"*. The gate treats any lag as FAIL. Those are two different meanings of the same row:

- If **"verified"** means reviewed, then lagging live is correct behaviour and the gate is asking
  the wrong question.
- If it means **newest**, then no hand-authored string can hold at a 96-second cadence.

The row and the gate currently disagree about what the row is for. That is the defect; the stamp is
a symptom.

**Options.**

| | what changes | cost |
|---|---|---|
| **A — derive at publish** | the stamp is computed from `current.json` at publish time, never typed | every GridAtlas cut must also cut the homepage; `homepage_versions/README.md` requires a numbered snapshot with recorded metrics per edit, and that ritual cannot survive a 96-second cadence — it would need rethinking too |
| **B — declare intent** | add a `reviewed_release` field; the gate compares against that and reports drift-from-live as **information**, not FAIL | one gate change; the homepage then deliberately lags and says so |
| **C — stop naming a version** | the row keeps its stable URL, which always routes correctly, and drops the version from name and note | removes information you may want on the public page; breaks the `data_gridatlas_release` field the compiler writes |

**What I would do: B.** The URL `/gridatlas/atlas/` is a stable route and has never been stale — only
the prose has. "Current Verified Release" reads as a deliberate, reviewed pointer, and an estate
this careful about epistemics probably does not want its public directory tracking a cut made
ninety-six seconds ago and not yet looked at. B makes the lag explicit and true rather than an
error, and it costs one change to a gate rather than a change to how the homepage is published.

**A is right only if the homepage is meant to be a mirror rather than a statement.** Then the
snapshot ritual needs redesigning in the same breath, and that is a bigger decision than the stamp.

**I have stopped cutting the stamp.** It stands at v9.86 / `202609030200` against a live
`202609030234`. The gate correctly reports FAIL, exit 1.

---

## D8 — PipelineNews has no route by which an owner could authorise a deploy

**Measured.** Three gates block, in this order. The one everybody has been quoting is the second.

1. `timestamp release schema changed` — 30 of 32 releases carry
   `pipelinenews.additive-cartridge-release.v1`, written by `release_builder.py:494` and read by
   **no consumer**. Every one declares `"deployment": "not-authorised"` in its own bytes. Fires on
   every ordinary push.
2. `pointer_commit == HEAD` — the line named in the circulating spec. The repository already answers
   ancestor-vs-equal in its own source, at `validate_current_or_predecessor_pointer()` (`aeb8827`,
   30 Aug), using `merge-base --is-ancestor`. Aligning them is a consistency repair, proven locally
   — and **it unjams nothing**, because gate 3 then fires.
3. `changed_public_paths ⊆ allowed_public_changes` against a hard-coded
   `ATLAS_V9_SOURCE_PARENT = 693ccda8` (29 Aug). **1,796 diverging paths, all `A`, zero `M`, zero
   `D`** — nothing published has been modified or deleted. The allowance covers at most 42.

Gate 3 is **working as designed**. The README says every deployment requires explicit owner
approval; the owner authorised one exact tree, and nothing since has been authorised.

**The defect is the absence of a route.** The only authorisation record the gate reads binds a
v8-fast candidate, and the freeze is a constant in source. `workflow_dispatch` fails on the same
three gates. There is no action an owner can take, short of editing a constant, that means
"I authorise this wider closure."

**The artefact is not the blocker.** Release `202609030009-pipelinenews` verifies on disk, its three
local proofs pass 26/11/8, it contains zero mutable refs, and PipelineNews is second only to
globalgrid2050 in in-degree at 80 shipped edges from 5 repositories. Only the authorisation route
stands between it and the surface.

**Two agents declined to force this and I agree with both.** Advancing the constant redefines the
authorised public closure for 1,796 paths by fiat. Narrowing the trigger turns 27 red runs green by
ensuring the workflow never runs — a green light over a question nobody asked.

---

## D6/D9 — a watchdog that has been right for two days and unread

`data-gridatlas`'s hourly watchdog has correctly reported a dead GridAtlas URL every hour since
1 September:

```
404  https://ventusltd.github.io/gridatlas/202608291239-atlas-v9/release-manifest.json
200  https://ventusltd.github.io/gridatlas/atlas/releases/202608291239-atlas-v9/release-manifest.json
```

GridAtlas moved its published release directories under `/atlas/releases/`; the consumer probe holds
the pre-migration shape. It is a **bound four-file cut** — the workflow, both pointer files, and the
contract baseline SHA must move together, because `current-integrity.py:158-163` requires the two
pointers byte-identical and their hash equal to the baseline. A one-line fix turns an honest red into
a different red.

Assigned to an agent at 02:50 UTC. If it lands, this is closed; if not, it is yours.

---

## Not decisions, but you should know

**`touchstart` was bound, and my brief said it was not.** I told the UI lane both gesture slots were
free. `contextmenu` genuinely is. `touchstart` is bound at
`atlas/parts/202609012045-sld-sandbox-body.js:493` for dragging the SLD array, its rotate handle and
its route pins. The lane measured this, contradicted me, and built the long press to stand down for
all of it — single finger, cancels above 10 px, checks for an SLD drag twice because a drag can begin
inside the 500 ms. The engine-level statement was true; the conclusion I drew from it was not.

**The sandbox cartridge has 136 characters of headroom**, at 339,864 against a 340,000 guard. v9.85
bought 13,036 by moving the version ledger to a sibling; v9.88 spent almost all of it. The next
card-facing change needs headroom made first, and the guard was not raised at any point, on v9.76's
explicit precedent.

**That guard's name does not match its assertion.** It reads *"the sandbox cartridge is back under
the 400 kB boundary with room to spare"* and asserts `cartridgeSource.length < 340000` — JavaScript
string length, in characters. The same file is **342,851 bytes** on disk, because multi-byte
characters in the prose. Under the guard by 136 characters; over 340,000 by 2,851 bytes. Neither the
threshold nor the unit matches the name. Not a defect — the assertion is self-consistent — but on a
cartridge 99.96% full, the gap between the two units is larger than the remaining headroom.

**The long press has never been touched by a finger.** Every assertion about it is structural, read
from served bytes. Whether 500 ms and 10 px are right, and whether the sheet clears an iPhone home
indicator, are judgements someone makes holding the phone.
