# The red board re-graded on a real denominator, and the finding my own instrument invented

`00-LOG.md` graded `logs/red-board.md` when it held **3 rows**, of which one had been
classified. Between 22:51:55Z and 23:10:57Z the triage lane rewrote it with **48 rows, 44
classified**. That is a denominator worth grading, so it was graded again. This entry
corrects and supersedes nothing in `00-LOG.md` — it measures a different, later artefact.

## The lane fixed the defects before anyone told it to

Both boards, side by side, from `logs/red-board.json`:

| | 22:51:55Z | 23:10:57Z |
|---|---|---|
| red runs enumerated | 44 | 44 |
| **classified** | **3** | **44** |
| grounded | 1 | 42 |
| **UNGROUNDED** | **0** | **2** |
| no evidence | 2 | 4 |
| **retries** | **0** | **22** |
| rows with `attempts: 0` | 2 of 3 | **0 of 48** |
| slots | 1× gpu, 1× igpu | 2× gpu, 2× igpu |

Every criticism in `00-LOG.md` section 2 was answered by the lane on its own: the retry
exists, no row is now filed without the model having been asked, coverage went from 6.8% to
100% of enumerated reds, and the endpoint-down rows are gone. **This lane takes no credit —
the peer message was never delivered, because no peer was addressable by name from this
session.** It is recorded because a correction that arrives independently is stronger
evidence that the defect was real than one that arrives on request.

**And "0 UNGROUNDED" is no longer a check that cannot fail.** It fired twice. A model claim
that could not be verified is now displayed as a claim beside the log's own first error
line, which is the behaviour the header promises.

## Grading the quotes: 12 sampled, 12 verified

Twelve rows marked `grounded` were sampled (seeded, from a snapshot taken before the board
rewrote itself again), each job log re-fetched from the Actions API, and each quote checked
against the fetched bytes.

    sampled 12 rows marked grounded
    quote verified verbatim in the log      12
    quote NOT found (triage overstated)      0
    quote present ONLY in echoed script src  3   <- real string, false role

**12/12. The board's literal claim — "quotes a line this script verified is present in that
job's log, character for character" — is true on every row sampled.** Verified examples,
each read from its own job log:

| repo | job | quote |
|---|---|---|
| data-gridatlas | 99625351535 | `public fetch failed after 4 attempts: https://ventusltd.github.io/gridatlas/...` |
| pipelinenews | 99706327165 | `AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:` |
| companies | 98828080023 | `RuntimeError: Compact candidate byte gate failed: total=46716059, oversized=[...]` |
| companies | 98654939642 | `Sealed candidate failed independent verification` |
| globalgrid2050-hompage | 100234087376 | `Input required and not supplied: token` |
| data-centres-gb | 98901064333 | `RuntimeError: Bounded Overpass fetch failed after 3 attempts; retained evidence: ...` |

## The finding I nearly reported, which was my own bug

The first pass reported **1 of 8 quotes MISSING** — `companies` job `98776486203`, the jq
assertion beginning `(.errors[0] | startswith("candidate total byte ceiling: total=413085198"))`.
Before writing that down as an overstatement it was checked by hand, and it is not one.

The quote spans **two** log lines, 478 and 479. In the raw log a per-line timestamp and an
ANSI colour code sit between them:

    478: 2026-08-28T07:30:54.0064374Z [36;1m  (.errors[0] | startswith("candidate total byte ceiling: total=413085198")) and[0m
    479: 2026-08-28T07:30:54.0065253Z [36;1m  (.errors[1] | startswith("seal: Direct sharded candidate verification failed:")) and[0m

`triage.py` strips timestamps and ANSI before matching. My verifier flattened whitespace but
kept both, so a multi-line quote could never match. **The instrument was wrong, not the
subject.** Stripping them as triage does, the row verifies — and the 8-row sample's "1
overstatement" became 0 in the corrected 12-row run.

This is the whole assignment turned on the auditor: a plausible finding, in the right shape,
about a real row, that never happened. It is recorded because the auditor is not exempt from
the failure class it was sent to find, and because *"a sweep that returns the same answer for
every repository is a broken instrument, not a finding"* has a sibling — **a sweep that
returns one anomaly should be suspected of being one too, until the anomaly is read by hand.**

## The weakness that survives, now measured

**3 of 12 grounded quotes (25%) appear ONLY inside the echoed `##[group]Run ...` workflow
source, never in the step's real output.** Discriminator: GitHub prefixes echoed script
lines with the `36;1m` colour code; removing those lines and re-matching leaves the quote
with nowhere to be found.

- `data-centres-gb` 98907496991 — `diff -u <(printf '%s\n' "${expected_sorted[@]}") ...`
- `companies` 98736832916 — `seal process exceeded the explicit 150-minute ceiling or terminated before emitting its report`
- `companies` 98776486203 — the jq assertion above

Each is a real string in the log, so the grounding rule passes it. None is evidence of what
the job *did* — the first is the script's own diff command, the second and third are branch
text and an assertion the run may never have reached. `companies` 98776486203 is the sharp
case: the same substring also occurs at line 660 as genuine output, so the row's conclusion
is right, but the quote backing it was taken from the script rather than the result.

**A quote from an unexecuted branch is grounded and worthless.** The rule tests presence; it
cannot test role. Excluding `36;1m` lines from the grounding corpus, or requiring the quote
to fall after the step's `##[endgroup]`, would close it — and would have cost 3 of these 12
rows a quote, which is the correct outcome, not a regression.

## Standing at 23:15Z

- generation **202609032246** live; world, atlas and homepage all 200; proof `746/746` at
  `7e3bdcb`, tree clean
- **sld-sandbox 368,605 / 368,640 — 35 characters left**, and the proof still prints
  "40995 characters clear"
- globalgrid2050 `d62d512` RED (V9.7, now ten of ten); pipelinenews `9ffb4f3` RED (by design,
  and still honestly red — no step reports success over an unpublished release)
