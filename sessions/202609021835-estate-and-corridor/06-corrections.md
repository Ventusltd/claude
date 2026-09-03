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

---

## C6 — I pushed a cvaa fix whose proof step never ran. Corrects nothing earlier; records a
process failure of my own, 02:00 UTC.

The chain was `set -e` with the proof written as `node block.js && echo PASS`. My `sed` extraction
of the workflow's node heredoc pulled the `node - <<'NODE'` marker line in too, node threw a
SyntaxError, and because the failing command sat on the left of `&&`, `set -e` did not stop the
chain — it committed and pushed `57c19ea`. The disk arithmetic printed correctly (26 − 1 = 25,
results 25), so the logic was right, but the workflow's own block had not executed. I found out
by running it afterwards.

**Lesson.** A proof on the left of `&&` under `set -e` is not a gate. Capture `rc=$?` on its own
line, or the echo after it is the only thing that ran.

## C7 — The spider's D10 root cause was one of two constants, and I accepted it without running
the step. Corrects the acceptance, not the spider's finding.

`202608301447-selftest.yml` has two hard-coded counts in one `run:` block: line 28 asserts
**24** vaccine files on disk; line 41 asserts **23** active results. Both drifted by the same
two vaccines on 31 August. Under `set -euo pipefail` the step aborts at line 28 — before
`selftest.mjs`, before `inoculate`, before the node block. My first fix corrected line 41 only and
could not have turned the runner green. Same step red before and after, which is what said so.

**Lesson.** Reproduce the *step*, not the *assertion*. I verified the number I was told about and
never executed the five lines above it.

## C8 — I replaced a wrong constant with a check that cannot pass, and my proof printed PASS.
02:01 UTC, `67c5e34`.

Line 28 rewritten as `-eq "$(node -e "…require('./vaccines.lock')…")"`. node's `require()`
chooses a parser by extension; `.lock` is not `.json`, so it parsed the file as JavaScript and
threw. The substitution came back empty, `test 26 -eq ""` errored "integer expected" — and the
`echo "PASS"` on the next line ran anyway, because `set -e` was not stopping this shell either.
I read the echo and shipped.

Fixed in `791e24b` with `JSON.parse(readFileSync)`, and the proof rewritten so every check
reports its own `rc` explicitly, including line 28 run verbatim from the file. All three `rc=0`
before the push.

**Lesson, and it is the night's lesson.** Three times in ninety minutes I trusted a green line
that measured nothing: the agent's local proof (F8), the spider's dirty-tree red (C5), and my own
`&&`/`set -e` proofs (C6, C8). The estate's rule — *a skip is not a pass* — is exactly aimed at
this, and it caught me the same way it caught the observer.

---

## Addition to 07-routing-table, 02:15 UTC — D9/D6, from the spider, reproduced in a clean LF clone

| # | finding | owning files — **bound, move together** | class | measured | gate |
|---|---|---|---|---|---|
| D9/D6 | `data-gridatlas` hourly watchdog is **correct**: it has reported a dead gridatlas URL every hour since 1 Sep, and nobody read it | `.github/workflows/202608291239-verify-live-pointer.yml:123` · `releases/current.json:13,:23` · `state/live-set.json:13,:23` · `contracts/202608291507-automation.json` `baseline.pointer_sha256` | 4-file bound cut, no lane tonight | consumer probe 404 at `/gridatlas/202608291239-atlas-v9/release-manifest.json`; **200** under `/gridatlas/atlas/releases/…`. gridatlas moved its release directories; the probe holds the old shape. `current-integrity.py:158-163` requires both pointers byte-identical and their SHA-256 equal to the contract baseline (`08664a2f…`), so one file cannot move alone — an honest red would become a different red. | the watchdog's next hourly run |

Also from the same message, and general to this machine: several working copies were checked out
before their `.gitattributes` gained `* text=auto eol=lf` and have never been renormalised. Disk
holds CRLF, the blob holds LF. **Any digest or byte comparison read off disk here is wrong and
right on the runner.** `git ls-files --eol | grep w/crlf` names them per repo. Compare
`git show HEAD:<path>` bytes, or use a clean clone. The spider nearly misreported D9's cause this
way (RH14); the pipelinenews agent found 10 ledger digests wrong this way; the gridatlas proof
hazard was this shape.
