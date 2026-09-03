# Corrections to this session's findings

Per the repository rule: nothing earlier is amended. Each entry names what it corrects and why
the original was wrong. The original stays in place so the next session can see how the error
was made, not only that it was.

---

## C1 — F1 named the wrong gate. Corrects `01-findings.md` §F1.

**Original claim.** The PipelineNews deploy fails because `build-pages.py:904` requires the
live-pointer commit to *be* HEAD, while the trigger fires on `releases/**`.

**What was wrong with the reproduction.** I ran the gate with
`--timestamp-folder-release 202608291447-pipelinenews` — the *old* pointer's release — chosen by
me. CI does not choose; it derives the release from the pushed commit's diff. For every push
since 31 August that selects the *newly pushed* release. Forcing the old one bypassed the gate
CI actually hits first.

**Reproduced faithfully** (overnight PipelineNews agent, and re-run by me at 02:50 UTC against
`gh/main` at `1a9868e` with the release CI would select, `202609030009-pipelinenews`):

```
PAGES BUILD GATE FAILED: timestamp release schema changed
```

**Three gates block, in this order:**

| # | gate | status |
|---|---|---|
| 1 | `timestamp release schema changed` — 30 of 32 releases carry `pipelinenews.additive-cartridge-release.v1`, written by `release_builder.py:494` and read by **no consumer**; every one declares `"deployment": "not-authorised"` in its own bytes | fires first, on every push |
| 2 | `pointer_commit == HEAD` — the F1 line | fires second; the repo already answers ancestor-vs-equal in `validate_current_or_predecessor_pointer()` (`aeb8827`, 30 Aug) using `merge-base --is-ancestor`; aligning them is a consistency repair, proven locally, and **unjams nothing** |
| 3 | `changed_public_paths ⊆ allowed_public_changes` against hard-coded `ATLAS_V9_SOURCE_PARENT = 693ccda8` (29 Aug) — **1,796 diverging paths, all `A`, zero `M`, zero `D`**; the allowance covers at most 42 | fires third; **working as designed** |

**The dates agree.** Last Pages success 30 Aug 11:13. First additive-cartridge release 31 Aug 13:43.

**The actual defect, restated.** Gate 3 is an authorisation freeze: the README says every
deployment requires explicit owner approval, and the owner authorised one exact tree. Nothing since
has been authorised. **There is no route by which an owner could authorise a wider closure** — the
only authorisation record the gate reads binds a v8-fast candidate, and the freeze is a constant in
source. `workflow_dispatch` fails on the same three gates.

**Why the agent declined to unjam, and I agree.** Advancing the constant redefines the authorised
public closure for 1,796 paths by fiat. Narrowing the trigger turns 27 red runs green by ensuring
the workflow never runs, leaving the site on its 30 August build — a green light over a question
nobody asked, the exact failure this estate keeps recording. Neither is a code decision.

**Lesson.** When reproducing a CI failure, reproduce the *selection logic*, not only the check. A
check reached by a path CI never takes is a different check.

---

## C2 — "138 commits unpublished" overstated the surface. Corrects `00-LOG.md` §2 and the
first agent brief.

The jam affects only `ventusltd.github.io/pipelinenews/`. The `globalgrid2050.com/
pipelinenews_intelligence/<stamp>/` route is a separate publication surface, not jammed, and was
already serving current releases throughout. Unjamming would not have dumped a backlog on a
user-facing surface. I corrected this to the user at the time; recording it here so it is not
re-learned.

---

## C3 — Reg3 was diagnosed against a URL parameter Pipeline News never emits. Corrects the
inherited spec, not this session's own finding.

The circulating spec said a deep link carries `technology=Landfill Gas` and the whitelist throws.
Measured by the PipelineNews agent: **no release has ever emitted `technology=Landfill Gas`** — all
three builders emit `row.t`, e.g. `biomass`. The parallel session's live journey confirmed
`technology=biomass` arriving RESOLVED. What actually happens: the four-type
`allowedTechnologies` set is exactly what the wider fleet excludes, so **all 1,104 wider-fleet
links lose their technology *layer*** — not the arrival. GridAtlas v9.82, "an unknown technology
costs one layer, not the arrival", is the correct fix for the correct defect.

---

## C4 — The auditor's own baseline was wrong, and it said so. Recorded because self-correction
is the point.

Its baseline claimed all five retained `*OFFSHORE*` sites sit on land. Measured against the
overhead-line network: only `HUMW` (0.00 km) and `HOWW` (0.22 km) do; `WERO`/`WERW` (14.56 km)
and `RAMW` (15.83 km) are genuinely offshore. It also retracted "nothing changed in three hours"
as overstated — the first watch ran five minutes before Codex's commit. Both corrections were
volunteered, unprompted.

---

## C5 — The spider raised a false red. Recorded because a standing observer that is wrong once
must be seen to have been corrected.

It reported `run-current.mjs` going green to red on v9.82. It had measured a **dirty working
tree** while the gridatlas agent was mid-implementation of the pinning fix, test-first — proof
written, module (`atlas/modules/202609030137-pinned-products.js`) not yet finished. A clean
checkout of committed `52ebabc` passes 44/45, the one failure being a sibling-repo path absent
from the scratch copy. Its brief said never to treat a dirty tree as a defect; it has been told to
check `git status --porcelain` before reporting any gate result.

What was right in the same message, and verified: the unpinned `@main` edges are real, and the
sequencing argument — `data-grid-gb b91e45b` and a gridatlas pin should land as one event — is the
most valuable thing said tonight.
