# The coaching watch — grading the local model, and three checks that misreport themselves

A standing watch over `logs/board.md` and `logs/red-board.md` from 2026-09-03 22:50Z to
23:15Z. Nothing here was fixed by this lane. Everything here is a measurement with the
commit, file or run id it was read from.

---

## 1. The local model was graded, and it did not invent anything

The peer figure of 98.3% precision was corroborated, on a larger sample and against the
raw source bytes rather than against a re-parse.

`familiars/harvest.py` asks `qwen3:4b-instruct-2507-q4_K_M` for the settlement inside a UK
energy project name. An independent auditor re-ran the identical prompt over the same
loader and scored each answer three ways: harvest's own substring-grounding rule, a
stricter whole-word rule, and a check of the abstentions harvest never scores.

| | 50 rows | 60 rows | combined |
|---|---|---|---|
| rows put to the model | 50 | 60 | 110 |
| request failures (dropped by harvest) | 7 | 13 | **20** |
| volunteered an answer | 34 | 42 | 76 |
| abstained (said NONE) | 9 | 5 | 14 |
| **invented — harvest's substring rule** | 0 | 0 | **0 / 76** |
| **invented — strict whole-word rule** | 0 | 0 | **0 / 76** |
| echoed the planning authority | 0 | 1 | 1 |
| precision, harvest's denominator | 100.0% | 97.6% | **98.7% (75/76)** |
| precision over all rows put to the model | 79.1% | 87.2% | 84.4% (75/89) |

Then every answered row was checked against the **raw bytes of the release JSON**, not
against my loader:

    answered rows checked            42
    project name verbatim in source  42 confirmed / 0 absent
    answer verbatim inside the name  42 confirmed / 0 absent

read from `pipelinenews/releases/202609032159-pipelinenews/data/202609030009-wider-fleet.json`
(220,400 bytes) and `202608311610-grid-proximity.json` (5,508,320 bytes).

Sampled rows, verbatim: `Birmingham <- Birmingham Bio-Power Plant` (authority *West
Midlands*), `Glensaugh <- HydroGlen Project - Glensaugh Farm` (authority *Aberdeenshire*),
`Carnwath <- Carlindean Farm, Carnwath - Anaerobic Digestion Plant` (authority
*Lanarkshire*), `Mop End <- Mop End Farm, Mop End Lane - Battery Energy Storage`
(authority *Buckinghamshire*). Every one of these is the settlement and not the authority,
which is the defect the field exists to fix.

### The theory I had, which the measurement refuted

I predicted harvest's grounding test would be too loose. `grounded = low in name.lower()`
is a plain substring test, so it catches an INSERTION (`Rampton -> Rampson` is not a
substring of the name) but cannot catch a TRUNCATION — `Kintor` is a substring of
`Kintore` and would score a hit. I wrote a whole-word-anchored rule to find those.

**It found zero.** In 76 volunteered answers the strict rule and the loose rule agree
exactly. The weakness is real in principle and cost nothing in practice, and saying so is
the point: a hypothesis that measures out at zero is a result, not a non-event.

I also flagged that `is_auth` compares only exact equality, so a truncated authority would
pass. One row hit it: answer `Avonmouth`, authority `Avon`. **Harvest is right and my
stricter rule would have been wrong** — Avonmouth is a real settlement in the authority of
Avon. Exact equality is the correct test here. Recorded as a correction to my own reading.

### The defect that is real: 31% of the sample never reaches the printed number

`harvest.py` line 113: a failed request is caught, printed, and `continue`d — it enters no
counter. Abstentions are counted but excluded from the precision denominator, and nothing
ever checks whether an abstention was correct.

Across 110 rows, **20 request failures (18.2%) and 14 abstentions were invisible to the
headline**: 76 of 110 rows reached it. The failures were real and diagnosable —

    [WinError 10054] An existing connection was forcibly closed by the remote host
    [WinError 10061] No connection could be made because the target machine actively refused it

A model that times out on the hard rows and answers the easy ones scores beautifully. This
is CLAUDE.md's own rule — *a missing input must FAIL, never skip* — and the wrong-denominator
warning: a number that gets quoted rather than checked. 98.3% was quoted to me.

Contention is the other half: **14.2 s/row** against a design that costs about 1 s/row,
because three lanes share one ollama endpoint and one of them was restarting it.

---

## 2. `logs/red-board.md` contradicts its own JSON

The triage lane's board is honest in structure — it separates a model's claim from a
verified quote, and it sources repo, run id, job and failing step from the API. The one
row that was classified is genuinely sound. The rest is misreported.

**The one grounded quote is verbatim. I checked it.** `"PAGES CANNOT PUBLISH THIS RELEASE
CLASS"` occurs twice in job `100833659830`. Precision on quotes I verified: **1/1, and the
denominator is 1** — that is the honest statement, and it is not a measurement of a model.

**But the grounding rule cannot see role, only presence.** Of the two occurrences, line 259
is inside the echoed `##[group]Run ...` script source (13 of 13 lines in that block carry
the `36;1m` colour code) and line 288 is the real output. A quote drawn only from the
echoed source would score grounded even if that branch never executed. Not an invented
string — a real string in a false role, which is the `Rampton -> Rampson` failure one
level up. Excluding the echoed block, or requiring the quote to fall after `##[endgroup]`,
closes it.

**Two of three reds were dropped at a dead endpoint while a live one sat idle.** From
`logs/red-board.json`:

| row | device | attempts | log_chars | excerpt_chars | focused | filed as |
|---|---|---|---|---|---|---|
| globalgrid2050 V9.7 | gpu | **0** | 54,400 | 10,835 | true | *the log could not be read at all* |
| pipelinenews | igpu (qwen3:0.6b) | 1 | 28,129 | 7,588 | true | grounded |
| data-gridatlas | gpu | **0** | 49,746 | 6,117 | true | *the log could not be read at all* |

`meta.retries: 0`. `meta.per_device.igpu.n: 1` — the igpu was up and answering. The board
was written 22:51:55Z, which is exactly the window in which another lane was cycling ollama
servers; both endpoints returned 200 when I curled them at 23:12Z. **A transient endpoint
outage should cost a retry, not a row.**

The section heading is false about its own data. The logs *were* read and the excerpts
*were* built; the model was never asked. "Endpoint down" and "log unreadable" are different
failures and must not share a bucket — this describes a local infrastructure fault as a
property of a CI log.

**The evidence was inside the excerpt it built.** I fetched job `100839327538` myself: 585
lines, `##[error]` at line 555, and the cause five lines above it at 550-551, well inside
the 161-line window —

    -    "input_sha256": "cea104c3e9cfc07971680afdf5f64073e1d4825b63bfaf4e969266df8386ebbd",
    +    "input_sha256": "e6c42cd886bb340ca4d9887954cd090adfcc22bbf59621289bb48ae548ff5b8b",

The V9.7 gate rebuilds `regional_manifest.json` and diffs it against the committed copy;
the committed `input_sha256` no longer matches the input the build reads. A real, quotable
cause, in hand and discarded.

**Denominator.** The headline reads *3 red jobs across 8 repositories · 1 grounded · 0
UNGROUNDED*. `meta.red_runs: 44`, `meta.classified: 3` — **3 of 44, 6.8%**. And "0
UNGROUNDED" is a check that ran on a sample of one; it could not have failed.

**It is also stale.** Header says *sweep 10s*; the file had not been rewritten in 16
minutes at 23:07Z, and its rows are pinned to `d5aafef` when head had moved to `d62d512`.

---

## 3. The ceiling check prints a number 1,171× larger than the one it gates

`gridatlas/tools/proofs/202609032246-sld-sandbox.proof.mjs:3578`

    const CARTRIDGE_BOUNDARY = 409600;
    const CARTRIDGE_CEILING  = Math.floor(CARTRIDGE_BOUNDARY * 0.9);   // 368,640
    check('the sandbox cartridge is under the 400 kB composer boundary with a '
      + 'tenth of it still in hand',
      cartridgeSource.length < CARTRIDGE_CEILING,
      `${cartridgeSource.length} of ${CARTRIDGE_BOUNDARY}, `
      + `${CARTRIDGE_BOUNDARY - cartridgeSource.length} characters clear`);

The assertion is against `CARTRIDGE_CEILING`. The evidence string reports headroom against
`CARTRIDGE_BOUNDARY`. Measured on both cartridges:

| cartridge | length | real headroom vs the gate | what the proof prints |
|---|---|---|---|
| `202609032222-sld-sandbox-v9-8.js` | 368,343 | **297** | 41,257 characters clear |
| `202609032246-sld-sandbox-v9-8.js` | 368,605 | **35** | 40,995 characters clear |

The comment directly above it says the ceiling *"prints the headroom so a reader can watch
it close rather than discover it closed."* It does the opposite: at 35 characters from a
hard failure it reports forty-one thousand clear. The one-line correction is to subtract
from `CARTRIDGE_CEILING` — **and it must not be fixed by raising the ceiling**, which the
same comment already forbids ("if this needs raising again the answer is to move
computation out ... not to raise it a third time").

**Nobody raised it.** `CARTRIDGE_CEILING` is still `Math.floor(409600 * 0.9)` at `7e3bdcb`.
The shared check is intact. But generation 202609032246 spent 262 of the 297 characters
that were left — **88% of the remaining headroom in one cut** — and the runners board is
the only place that number is stated truthfully.

---

## 4. A cancelled workflow is counted as nothing

`familiars/runners.py:226-237`

    if r.get('status') != 'completed':          waiting += 1
    elif r.get('conclusion') == 'success':      green += 1
    elif r.get('conclusion') in ('failure', 'timed_out', 'startup_failure'):
        ... reds ...

`cancelled` matches no branch, and neither do `neutral`, `stale`, `action_required` or
`skipped`. Such a run is counted in `workflows` but in none of green, waiting or reds.
Measured from `logs/board.json` at 22:52:44Z:

| repo | workflows | green | waiting | reds | accounted | **dropped** |
|---|---|---|---|---|---|---|
| gridatlas | 4 | 4 | 0 | 0 | 4 | 0 |
| **globalgrid2050** | 10 | 8 | 0 | 1 | 9 | **1** |
| pipelinenews | 20 | 9 | 0 | 11 | 20 | 0 |
| claude | 1 | 1 | 0 | 0 | 1 | 0 |
| cvaa | 4 | 4 | 0 | 0 | 4 | 0 |

The dropped one is `V9.4 Exact Commit Validation`, conclusion `cancelled`, at head
`d5aafef`. Today it is harmless because `V9.7` is red anyway. **The day V9.7 is fixed,
globalgrid2050 reports `green` while V9.4 has never concluded at that head** — a green
that skipped its input. The state ladder needs a fourth rung; a gate that did not conclude
is neither a red nor a green, which is the discipline this daemon already applies correctly
to a dirty tree.

---

## 5. A second always-red, which nobody had named

The pipelinenews red is by design and was known. **`V9.7 Exact Commit Validation` is the
same shape and was not.** Conclusions on `main`, read from the Actions API:

    V9.7 runs found: 9        Counter({'failure': 9})
    2026-09-03T22:27:34Z d5aafef failure     2026-09-02T19:53:23Z 1f03e4d failure
    2026-09-03T13:17:31Z 9c4a0df failure     2026-09-02T19:37:49Z 685ce84 failure
    2026-09-03T03:17:38Z a0f93e8 failure     2026-09-02T19:25:44Z 9c36d53 failure
    2026-09-03T02:29:34Z 687d03f failure     2026-09-02T19:02:39Z 9f1a7b9 failure
    2026-09-03T01:10:58Z 87e6da8 failure

Nine of nine, every distinct sha, back to 2026-09-02 19:02Z — and a tenth at `d62d512` at
23:05Z during this watch. Its siblings at the same sha are green (V9.3, V9.5, V9.5.1,
V9.6.1, Pages deploy), so it discriminates *between workflows* and carries a real diagnosis.
But it has never once been green, so **a genuine new break in V9.7 would look identical to
tonight**, which is the same argument already made for pipelinenews. Two always-reds, not one.

And pipelinenews was checked for the thing worth checking: **nobody turned it green.**
Eight of eight failures on `main` back to 2026-09-02T00:25Z, and in run `33811350589` the
two downstream jobs are `skipped`, not `success`. No step reported success over a release
it did not publish. The check is intact.

---

## What this lane did not do

Shipped nothing. Edited no other lane's files. Did not touch `gridatlas/atlas/`,
`globalgrid2050/index.html`, or anything under `pipelinenews/`. Peer lanes were not
reachable by name from this session, so the corrections are in this file and in the report
to the architect rather than delivered by message.
