# 02 — runner health

Every case where MY OWN check was wrong. A spider that never corrects itself is
not measuring, it is asserting.

---

## RH1 — 2026-09-03T01:25Z — the cvaa vaccine `disk-is-not-what-ships` is a
## 100% false positive, and I nearly reported it as the estate's top defect

**What the check said.** 18 of 18 repositories not immune, every one with the
identical finding:

    no .gitattributes: the working copy and the blob can differ, so any check
    that reads a file off disk is asking a different question from any check
    that reads what ships

That is a perfect wall. A perfect wall is the signature of a check that cannot
fail, and the brief says a check that cannot fail is not a check.

**What is actually true.** `cvaa` itself carries a `.gitattributes` with a
correct `* text=auto eol=lf` on line 30, plus binary rules and explicit
`text eol=lf` for every executable extension. Reproduced by hand:

    $ ls -a cvaa | grep gitattributes
    .gitattributes
    $ grep -E '^\s*\*\s+text=auto\s+eol=lf\s*$' cvaa/.gitattributes
    * text=auto eol=lf

**The defect.** The antibody opens with:

    export default ({ files }) => {
      const attrs = files['.gitattributes'];

and `inoculate.mjs` line 96 builds that object as:

    const files = { STATE: exists('STATE.md') ? read('STATE.md') : null,
                    index: exists('index.html') ? read('index.html') : null };

The key `.gitattributes` is never present in any repository, so
`if (!attrs)` is unconditionally true and the first branch always fires. The
second half of the antibody — the `SUSPECT` regex hunting for `createHash` over
`readFileSync` and `hashlib.sha256`, which is the defect the vaccine was
actually written to catch after four incidents in one evening — iterates
`Object.entries(files)`, so it only ever inspects `STATE.md` and `index.html`.
It has never examined a single line of the code it exists to police.

The vaccine's reasoning is sound and its provenance is real. Its wiring is not:
it was given none of the data it asks for.

**What I changed.** I do not edit `cvaa` — it is not my lane, and relaxing a
rule to make repos pass is forbidden. Instead:

1. `disk-is-not-what-ships` is listed in `spider-state.json` under
   `cvaa.distrusted_vaccines` and is EXCLUDED from every adoption count I
   report. The corrected top-three failing vaccines are
   `monotonic-utc-generations`, `chaining-token` and `pinned-actions`.
2. I evaluate the rule by hand instead, which takes one line and gives the
   right answer. Result, pass 1, all 18 local clones:

   | verdict | repos |
   |---|---|
   | `* text=auto eol=lf` present and correct | 14 |
   | `.gitattributes` present but WITHOUT that line | chatgpt-audits, claude, codex-chatgpt, gemini |
   | absent entirely | 0 |

   So the true finding is 4 repos, not 18, and none of them for the stated
   reason. Those four are all agent-notes repositories rather than shipping
   surfaces, which is why this ranks low on consequence.

**The fix cvaa needs** (recorded, not applied): `buildContext` must add
`'.gitattributes'` to `files`, and the second half of the antibody needs a
source-file corpus rather than a two-key object. Until then the vaccine reports
a conclusion it has no evidence for — which is the precise disease the cvaa
architecture exists to prevent, in cvaa itself.

---

## RH2 — 2026-09-03T01:52Z — four gates I called FAILING were my own
## invocation errors

I ran every discovered gate with no arguments and recorded four failures. All
four were mine.

| gate | my reading | truth |
|---|---|---|
| `pipelinenews/tools/intelligence/render_proof.mjs` | exit 2, FAIL | prints `usage: node render_proof.mjs <release-id>`. With `202609030009-pipelinenews`: **26 checks, 0 failed** |
| `…/sector_render_proof.mjs` | exit 2, FAIL | same; **11 checks, 0 failed** |
| `…/surface_truth_proof.mjs` | exit 2, FAIL | same; **8 checks, 0 failed** |
| `data-grid-gb/chatgpt/verify_product.py` | exit 1, IndexError | takes a product path. With `chatgpt/derived/etys-2025.normalized.json`: **PASS**, sha `40f0aa1c…`, 1735 sites / 1392 circuits / 1472 transformers |

A fifth, `data-gb-electricity/pipelines/verify_bounded_growth.py`, exits 1 on
`FileNotFoundError: reports/fetch_latest_month_latest.json`. That one is not an
invocation error and not a defect: it is a CI-only gate that verifies an audit
artefact the monthly updater produces. It is recorded as
`not-runnable-locally`, which is a different state from `fail`, and
`spider-state.json` keeps those states distinct so a later pass does not
resurrect it as a regression.

**What I changed.** `spider-state.json.gates` now stores the full command
including arguments for every gate, so a fresh instance cannot repeat this. Any
gate whose first run produces a usage string is a discovery result, never a
finding.

---

## RH3 — 2026-09-03T01:10Z — my crosslink extractor was blind to the three
## most important edges in the estate

The first extractor scanned line by line. Shipped gridatlas cartridges build
their product URLs by string concatenation across two lines:

    const PRODUCT = 'https://raw.githubusercontent.com/Ventusltd/data-grid-gb/'
      + 'main/derived/connection-points.v3.json';

The repository name is on line 1 and the ref is on line 2, so my
`raw.githubusercontent.com/Ventusltd/(repo)/(ref)/(path)` regex matched nothing.
The result was a graph that reported `gridatlas -> data-grid-gb` as a
*contract* edge only, and listed three mutable runtime edges when there are
five. Had I stopped there I would have reported that the exact edge the
coordinator flagged does not exist in shipped code — a false all-clear on the
highest-consequence finding of the night.

**What I changed.** The extractor now collapses JS/Python string concatenation
(`'…' + '…'`, across a newline) before matching, and attributes the hit to the
line the first fragment sits on. Recount:

    mutable shipped runtime-data edges   3  ->  5
    total raw edges                    667  -> 671

The two recovered edges are `gridatlas -> data-grid-gb@main` for
`derived/connection-points.v3.json` and `derived/gb-transmission-network.v1.json`.

**Generalisation for later passes:** any estate that writes URLs as constants
will split them at the 80th column. A line-oriented scanner under-reports
dependencies systematically, and it under-reports them silently — the graph
still looks plausible, just smaller. Count before trusting a count.

---

## RH4 — 2026-09-03T01:36Z — I committed a generation stamp in BST and
## labelled my own timestamps `Z`

My pass-1 commit is `202609030220: cicd-spider pass 1 baseline…`. Its actual
UTC commit time was 01:22Z. The stamp is **58 minutes ahead of the event it
names**, because I read the machine clock (BST, UTC+1) and wrote it as a
generation without converting.

    $ date -u +%Y-%m-%dT%H:%M:%SZ   ->  2026-09-03T01:35:56Z
    $ date    +%Y-%m-%dT%H:%M:%S %Z ->  2026-09-03T02:35:56 GMTDT

Several timestamps in `00-LOG.md`, `01-drift.md` and `03-crosslink.md` carried
the same error and have been corrected in place.

This is precisely `monotonic-utc-generations`, the vaccine I had just reported
as the estate's most widely failing rule at 14 of 18 repositories — "generations
are read from `date -u` at commit time, never chosen". I made the error in the
same hour, in the artefact reporting it. The vaccine is right, and it would have
caught me.

**What I changed.** Every timestamp I write now comes from
`date -u +%Y-%m-%dT%H:%M:%SZ` or Python's `datetime.now(timezone.utc)`, never
from the local clock. `pass.py` already used the UTC form, which is how the
discrepancy surfaced — the driver and I disagreed by exactly one hour and the
driver was right. The session directory name `202609030120` is correct UTC and
stays as it is; renaming it would break the resume contract for no gain.

The commit stamp itself cannot be corrected without rewriting a pushed commit,
which is not worth it. It is recorded here instead, which is what the vaccine
asks for: a wrong generation that is admitted beats a wrong generation that is
tidied away.

---

## RH5 — 2026-09-03T01:37Z — I summarised a gate from `tail -4` and reported
## the wrong scale

In pass 1 I recorded `gridatlas run-current` as "4 proofs run; every composed
cartridge passed its generation-matched proof", taken from the last four lines
of its output. The exit code was 0, so the verdict was right — but the *scale*
was wrong: at v9.82 the same gate prints `664/667 checks passed`, and the "4
proofs" line I quoted is a per-section footer, not the suite total.

The consequence is that a later pass comparing "4 proofs" to "667 checks" would
read a composition change as a catastrophic regression, or the reverse. A tail
is not a summary; it is whatever happened to be printed last.

**What I changed.** `pass.py` records the exit code as the verdict and stores
only the last non-empty line as a hint. When a gate goes red I now read the
`FAILURES` block explicitly rather than quoting the tail — which is how the
three real gridatlas failures were found.

---

## RH6 — 2026-09-03T01:45Z — I reported a FALSE RED off a dirty tree, and sent
## it to main. This is the worst error I have made tonight.

**What I reported.** "gridatlas run-current went green to red on v9.82, 664/667,
three failures", messaged to main at 01:41Z.

**What was true.** v9.82 as committed is green. The coordinator measured a clean
checkout of 52ebabc taken outside the working directory and got 44/45, with the
one failure an artefact of the copy having no sibling `data-grid-gb` beside it.

**What I actually measured.** The gridatlas working tree at that moment:

    M  atlas/parts/202609012045-sld-sandbox-body.js
    M  atlas/parts/202609012350-substation-intelligence-body.js
    M  tools/proofs/202609030109-substation-intelligence.proof.mjs
    M  tools/proofs/202609030128-sld-sandbox.proof.mjs
    ?? atlas/modules/202609030137-pinned-products.js     <- new, untracked

The agent was implementing the pinning fix **test-first**: the proofs asserted
pinned-products behaviour before the module satisfying it was finished. Red is
the correct state mid-implementation. My three failures and the coordinator's
six were both snapshots of a moving target, which is why the counts disagreed
(664/667 against 62/68) and why neither matched the committed state.

**Confirmed at 01:44Z.** gridatlas reached 4a17fa3 (v9.83, "the runtime data is
pinned to a commit and checked by its digest"), tree clean, and I re-ran with a
before-and-after guard:

    clean run at 4a17fa3  rc=0
    667/667 checks passed

My brief said this in as many words — *"If a repo is mid-write by another agent,
note it and move on. Never wait on a lock and never assume a dirty tree is a
defect."* — and I read it, and then did not check `git status` before running a
gate. A false red spends attention a real red then cannot get. There were four
real reds sitting in the Actions API at the same moment, and I had not looked
there yet.

**What I changed, in `pass.py`:**

1. `tree_state(repo)` is called BEFORE every gate. A dirty tree returns
   `unmeasurable-dirty-tree` — a third state, never `FAIL`.
2. It is called AGAIN after the run. If HEAD moved or the tree went dirty
   mid-run, the result is discarded. My 664/667 and the coordinator's 62/68 were
   both produced by a tree that changed underneath the runner; only an
   after-check catches that.
3. An unmeasurable pass is not a transition in either direction. The previous
   verdict is carried forward, so a dirty tree can never manufacture a red OR a
   green.
4. Gate detail is now parsed from the `FAILURES` block, not from `tail`.
5. **CI state now comes from the Actions API, keyed by commit.** It is the only
   CI signal in this estate that a live working tree cannot corrupt. Local gate
   runs are corroboration; the API is the measurement.

The general rule, which I should have started from: on this machine a
repository is not a state, it is a state plus three agents writing to it. Any
measurement that does not name the commit it measured is not a measurement.

---

## RH7–RH9 — 2026-09-03T02:12Z — three ways my graph counted things that are
## not dependencies

Extending the scan from 18 repositories to 32 turned 671 raw edges into 7,057
and made every count in `03-crosslink.md` wrong at once. Three distinct causes,
all the same mistake: **treating a string that looks like a dependency as one.**

**RH7 — a catalogue repository is not a consumer.**
`registry_of_all_content_in_repos_and_dependencies` emitted **6,124 of the
6,153** runtime-data edges, 2,601 from `registry/registry_v0001.json` alone. Its
entire purpose is to inventory every URL in the estate. Each row is a *record
that a URL exists*, not a fetch any program performs. Tiered `catalogue` and
excluded. Without this, the graph would have reported that repository as the
most dependent thing in the estate by two orders of magnitude, which is exactly
backwards — it depends on nothing and describes everything.

**RH8 — gridatlas keeps every cartridge generation on disk.** Only the four
named in `atlas/current.json` are composed into what is served; the rest are
retired code that still contains the pre-v9.83 unpinned URLs. I counted them
and reported five mutable edges when three had already been pinned 30 minutes
earlier. **A dependency graph must read the pointer, not the directory.** Fixed
by tiering any `atlas/cartridges/*` file not in the composed set, plus all of
`atlas/releases/` and `atlas/parts/`, as `superseded`. 5 → 3.

**RH9 — a URL inside a `.json` is a declaration, not a fetch.**
`gridatlas/atlas/current.json:292` carries
`"reads": "…/data-gb-electricity/main/derived/price-decade-rollup.json"` as
prose describing a panel, while the composed cartridge reads that product
through the pin table at `d310e3c`. I counted the prose as a mutable runtime
edge. Only an executable file can perform a fetch. 3 → 2.

**The result converged with the coordinator's independent count of 2.** That
agreement is the only reason to believe either number. Every one of these three
errors inflated the graph, and inflation is the dangerous direction: a
dependency graph that over-reports makes everything look load-bearing, which is
the same as marking nothing load-bearing.

**The generalisable rule**, and the one worth carrying forward: *a dependency is
something a program does, not something a file says.* Four tiers of evidence
separate the two — `shipped` is code that runs; `catalogue`, `record`, `doc` and
`declared` are text about code. 6,854 raw edges, 336 real ones. The ratio is
20:1, so a graph built without this distinction is 95% noise and will be
believed anyway, because it is bigger.

---

## RH10 — 2026-09-03T02:05Z — my first CI sample reported 24 failures as new

`pass.py` diffs the Actions API against the previous pass. On the pass that
introduced CI sampling there was no previous state, so every long-standing
failure — some dating to 2026-08-27 — was emitted as `[CI-RED] … -> failure`,
as though 24 workflows had just broken.

Nothing was wrong with the data; the *framing* was wrong, and framing is most of
what a drift report is. A first observation is a baseline, not a transition.
Fixed: when a repository has no previous CI state, the sample is recorded
silently and the drift line is one summary count instead of 24 alarms.

---

## RH11 — 2026-09-03T02:28Z — every CVAA number I have reported was measured
## against a cvaa that exists only on this machine

I ran `cvaa/inoculate.mjs` from the local working copy for three passes without
once checking whether that copy matches what is published.

    local  cvaa  c18cc13   28 vaccine files
    remote cvaa  d2893fa   26 vaccine files

Two commits — `b4454c3` and `c18cc13` — have never been pushed. And
`vaccines/202608312252-disk-is-not-what-ships.md` is **untracked**: it exists in
no commit, local or remote, alongside a modified `vaccines.lock`.

So the vaccine I reported at 01:25Z as failing 18 of 18 repositories is not in
the repository. It has never run in CI. It would not reach any consumer that
adopted cvaa today. I spent a finding, and the coordinator's attention, on a
rule nobody else has.

The irony is exact: I opened `02-runner-health.md` by catching a check that
could not fail, and then ran that check 82 more times across 32 repositories
without asking whether it was real.

**Re-measured against the published HEAD, 25 active vaccines, all 32 repos:**

| | with the local cvaa | with the published cvaa |
|---|---:|---:|
| repositories immune | **0** | **14** |
| findings | 546 | 517 |
| `pinned-actions` | 16/32 | 16/32 |
| `monotonic-utc-generations` | 14/32 | 14/32 |
| `chaining-token` | 12/32 | 12/32 |

The top three survive unchanged, which is why the headline of D3 stands. What
does not survive is the framing. I wrote "**Zero repositories are immune,
including cvaa**" in `01-drift.md` and repeated it to main. The truth is that
**14 of 32 are immune**, cvaa among the ones that are not by only 4 findings,
and every immune repository is a cold one. The estate is not uninoculated and
hopeless; it has a clean half and a working half, and every finding is in the
working half.

A wrong denominator is worse than a wrong finding. A wrong finding gets checked;
a wrong denominator gets quoted.

**What I changed.** Any tool I run against the estate is now measured from a
clean clone of its published HEAD, not from the working copy beside it — the
same discipline I applied to gates in RH6, which I had not thought to apply to
my own instrument. `spider-state.json` records the cvaa commit every result was
produced under, so a later pass can tell a real change from a change of ruler.

**And the finding that came out of asking:** cvaa's CI has been red since
2026-08-31 because `202608301447-selftest.yml:41` asserts
`run.results.length !== 23` and there are now 25. The self-test was last edited
2026-08-30T18:26Z when 23 was true; two vaccines were added the following day at
15:59Z and 21:46Z. 23 + 2 = 25. cvaa passes every one of its own vaccines and
fails its own build on a hard-coded number that drifted away from the thing it
describes — which is `derived-state-not-authored`, one of its own rules,
inside its own self-test.

---

## RH12 — 2026-09-03T01:56Z — I recorded RH4, said I had fixed it, and then
## made the same error five more times

RH4 recorded, at 01:36Z, that I had committed a generation stamp in BST for a
UTC event. Every commit I made afterwards did it again:

    stamp           actual UTC commit time    error
    202609030140    01:38Z                     +2 min
    202609030150    01:42Z                     +8 min
    202609030220    01:51Z                    +29 min
    202609030235    01:55Z                    +40 min
    202609030240    01:55Z                    +45 min

The cause is small and worth naming exactly: `git log` renders these commits as
`2026-09-03T02:55:37+01:00`, and I kept reading the `02:55` off my own output.
The offset was in front of me every time. I had also written, in RH4, "every
timestamp I write now comes from `date -u`" — and then went on choosing them.

**Naming an error is not fixing it.** RH4 was a description; what was needed was
a mechanism. From here the stamp is produced by `date -u +%Y%m%d%H%M` evaluated
inside the same command as the commit, so there is no step at which my reading
of a clock can enter.

This is `monotonic-utc-generations` — the rule I have been reporting as the
estate's second most widely failing, at 14 of 32 — and my own commits are now
among the findings it reports against the `claude` repository. The vaccine is
right, it is right about me, and it was right about me for the two hours in
which I was quoting it at everyone else.

The transferable part: a correction that changes only what you *intend* changes
nothing. Every correction in this file that survived — the dirty-tree guard, the
published-cvaa clone, the tier rule — survived because it became a line of code
in `pass.py`. The two that did not, RH4 and this one, were resolutions.

---

## RH13 — 2026-09-03T02:05Z — my ruler-change guard compared the wrong thing,
## caught before it fired

`pass.py` emitted `CVAA-RULER` whenever cvaa's published HEAD moved. The
coordinator is about to push a fix to cvaa's self-test — a workflow constant,
with **no change to any vaccine** — and that commit would have moved the HEAD
and made my driver announce a ruler change that had not happened.

The guard I built in RH11 to stop a ruler change reading as a repo change would
itself have produced a false ruler change. Same class of error, one level up.

**Fixed:** the ruler is now the *active vaccine set* — the sorted slugs of
`vaccines/*.md` minus any carrying `superseded_by:`, each with a SHA-256 of its
LF-normalised text. `CVAA-RULER` fires only when a rule is added, removed or
edited, and names which. A commit that moves the HEAD without touching a rule
now emits `CVAA-COMMIT` instead, which says explicitly that any findings delta
this pass is real.

This one cost nothing because it was caught before it ran. That is the whole
argument for writing corrections into the driver rather than into prose: a
mechanism can be inspected before the next pass, and a resolution cannot.

---

## RH14 — 2026-09-03T02:10Z — I reproduced a failure with the exact disease I
## had spent the night reporting, and was one step from publishing the wrong
## cause

Investigating D9, I ran the data-gridatlas watchdog in the OneDrive working copy.
It failed at `atman/202608291507-current-integrity.py:163` with
`stable pointer SHA-256 mismatch`, and I was about to report that as the cause.

    state/live-set.json     blob 08664a2f… 3336 B   disk 77b755de… 3408 B   DIFFER
    releases/current.json   blob 08664a2f… 3336 B   disk 77b755de… 3408 B   DIFFER
    contract baseline       08664a2fab1f2a6442a866b43abe3748fe4418e6bf0892630850a6edfd3f2283

**The blob matches the baseline exactly.** The 72-byte difference is 72 line
endings. `data-gridatlas` has a correct `.gitattributes` with
`* text=auto eol=lf`, but this working copy was checked out before that file
existed and has never been renormalised, so the disk holds CRLF and the blob
holds LF. The check is right; my copy of the file was not the file.

That is `disk-is-not-what-ships` — in my own investigation, on the night I
reported that vaccine as structurally broken. It is aimed at exactly the right
target and cannot see it.

Run in a clean LF clone, the same steps give: resolve `rc=0`, probe
`data-pointer` `rc=0`, probe `data-release` `rc=0`, probe `consumer` `rc=1` on a
404 — which is the real cause, and is D6.

**How widespread this is on this machine.** Tracked files whose working copy is
CRLF, from `git ls-files --eol`:

| repo | CRLF | tracked |
|---|---:|---:|
| `globalgrid2050` | **3,597** | 5,281 |
| `gridatlas` | 239 | 486 |
| `data-federation-map…` | 133 | 152 |
| `companies` | **75** | 76 |
| `data-gridatlas` | 67 | 133 |
| `spiders` | 50 | 52 |
| `cvaa` | **46** | 51 |
| `chatgpt-audits` | 38 | 3,266 |
| `data-centres-gb` | 32 | 33 |
| `claude` | 22 | 80 |
| `data-interconnectors` | 10 | 11 |
| `data-gb-electricity`, `gb-electricity-ui` | 8 | |
| `pipelinenews` | 2 | 3,045 |
| `grid-distance-maths` | 1 | 10 |

Only `codex-chatgpt`, `data-grid-gb` and `gemini` are clean. Fifteen of eighteen
working copies on this machine hold bytes that are not the bytes that ship, and
`.gitattributes` is correct in almost all of them — it was added after the
checkout and nothing renormalised.

**The operational consequence, for every agent on this machine:** any check that
hashes or byte-compares a file read off disk gives a wrong answer here and a
right answer on the runner, and the wrong answer looks like a defect in the
repository. Before believing a local digest result: run it in a clean clone, or
compare `git show HEAD:<path>` bytes, or check
`git ls-files --eol | grep w/crlf` first.

**What I changed.** Every reproduction I publish from here is done in a clean
clone of the published HEAD, which is the same rule RH6 established for dirty
trees and RH11 established for cvaa. Three separate corrections have now
converged on one sentence: *the working copy beside me is not the thing I am
being asked about.*

---

## RH15 — 2026-09-03T02:02Z — I exhausted the shared API budget and an estate
## gate went partially blind because of it

Running `globalgrid2050/scripts/verify_published_versions.py`:

    skipped: pipelinenews lineage head: HTTP Error 403: rate limit exceeded
    PUBLICATION TRUTH: FAIL
      - the homepage names Grid Atlas v9.77 / 202609020018 as the current
        verified release while the live composition is v9.86 / 202609030200

    $ curl -s https://api.github.com/rate_limit
    remaining 0 of 60   used 60   reset 02:34Z

The 60/hour unauthenticated budget is **per IP**, and this machine is running
four agents plus the estate's own gates. I had been spending 7 calls a pass on
CI sampling and more on ad-hoc checks, and I took the budget to zero. The gate
at `verify_published_versions.py:146` needs one call for its pipelinenews
lineage check, could not have it, and **skipped** — printing `skipped:` and
carrying on to report on everything else.

So a standing observer measuring the estate had made one of the estate's gates
stop measuring part of what it exists to measure. And it did not fail; it
skipped. **A skip is not a pass** is standing discipline here, and this is a
gate that silently degrades to a narrower check whenever the budget is spent by
anyone — an agent, another gate, or a spider.

**What I changed in `pass.py`:**

1. Check `api.github.com/rate_limit` first — that endpoint is free — and abort
   CI sampling entirely if fewer than 25 calls remain, emitting an
   `API-BUDGET` drift line instead. The estate's gates keep their share.
2. Sample CI only for repositories whose HEAD moved since the previous pass,
   falling back to three when nothing moved. Typical cost drops from 7 calls a
   pass to 1-4.
3. Record `remaining_at_pass` in `spider-state.json`, so a later instance can
   see whether a thin pass was thin because nothing happened or because it could
   not look.

**The finding that is not about me:** `verify_published_versions.py` should
fail, not skip, when it cannot reach the API — or state the skip in its verdict
line rather than four lines above it. As written, its `PUBLICATION TRUTH` result
can be produced from a strictly smaller set of checks than it names, and nothing
in the verdict says so.

---

## RH16 — 2026-09-03T02:36Z — I guarded half my pass against dirty trees and
## left the other half unguarded

RH6 made `pass.py` refuse to run a **gate** against a working copy another agent
is writing to. It reads the same working copies to run **cvaa**, and I never
applied the guard there. So for four passes every CVAA findings delta was
capable of the exact false signal RH6 exists to prevent.

It surfaced immediately once I looked: at pass 5 the driver reported
`gridatlas findings 80 -> 79` and `attestation-freshness incidence 0 -> 1`, and
gridatlas had **4 uncommitted paths** at the time. I do not know whether that
vaccine finding is real, and I should not have been in a position to report it.

**Fixed the same way as RH6, and no other way is worth having:** `one_cvaa`
calls `tree_state` before and after each run, returns `unmeasurable` for a dirty
or moving tree, carries the previous pass's figures forward so an unmeasured
repository cannot read as a change, and emits one `CVAA-SKIP` line naming which
repositories were mid-write.

The lesson is narrower and more useful than "check the tree". It is: **a
correction applied to one call site is not a correction.** RH6 fixed the gates
because that was where the error had happened; the same reasoning applied
unchanged to cvaa, and I did not carry it across. Every guard in this driver
should be asked "what else reads a working copy?" before it is called done.

`attestation-freshness` on gridatlas remains unconfirmed and is recorded as
such, not as a finding.

### RH16 addendum, 2026-09-03T02:40Z — the fix was not in the commit that
### described it

The patch above was applied by a script with three assertions. The third failed,
the script exited before writing the file, and my `&&` chain committed and pushed
`02-runner-health.md` describing a fix that `pass.py` did not contain
(`b0a1c1f`). For four minutes this file asserted a guard that was not there.

Applied properly and verified by parsing the file. The shape of the error is the
one worth keeping: **I wrote the account of the fix and the fix in the same
command, and only one of them was conditional on success.** A record that can be
committed without the thing it records is not a record. From here the change is
made and verified first, and described second.

---

## RH17 — 2026-09-03T02:44Z — I counted a string being deleted as a dependency,
## and it was the last one on my F5 list

`pipelinenews/index/202608261927-compile-index.mjs:128` contains

    https://raw.githubusercontent.com/Ventusltd/globalgrid2050/main/dist/major_project_news_v9_5_1.json

and I recorded it for four passes as the estate's remaining mutable runtime
edge. Read in context, it is the `original` argument to `replaceExactly()`:

    const original = `const NEWS_SOURCES = Object.freeze([
      ["Pages", "../../dist/major_project_news_v9_5_1.json"],
      ["GitHub main", "https://raw.githubusercontent.com/.../main/..."],
    ]);`;
    const replacement = `const NEWS_SOURCES = Object.freeze([
      ["PipelineNews", "../data/news/${GENERATION}-major-project-news-v9-5-1.json"],
    ]);`;

**The compiler exists to remove that URL.** It replaces a two-source list
containing a branch fallback with a single generation-pinned local path.
Verified against the built artefact rather than the build script:

    $ grep -rc "githubusercontent.com/Ventusltd/[a-z0-9-]*/main/" \
        releases/202609030009-pipelinenews
    (zero matches)

So pipelinenews does the opposite of what I reported: it is the one repository
that mechanically strips mutable refs at build time. I read the removal as the
addition.

**The general rule, which is the part worth keeping.** For any repository that
compiles, the dependency graph must be read from **the built artefact, not the
source**. A build script contains, by necessity, strings describing what it is
eliminating — every rewrite rule holds its own `before`. A scanner that reads
source treats `before` and `after` identically, and therefore reports the
carefully-removed thing as present. This is the same family as RH8 (retired
cartridge generations) and RH9 (a URL in JSON prose): four times tonight the
graph has counted text about code as code.

**The consequence for the estate, and it is the good kind.** With this corrected
and gridatlas v9.83's pins in place, the count is:

    mutable shipped runtime edges, estate-wide:  1
    that one: globalgrid2050 -> gridatlas@main/atlas/current.json
              scripts/verify_published_versions.py:54

and that one **should** stay mutable — it is the publication-truth gate, whose
whole job is to follow the live pointer. Pinning it would defeat it.

**F5 has no remaining instances.** Every cross-repository runtime fetch in this
estate that ought to be pinned now is. That was five at 01:05Z.

---

## RH18 — 2026-09-03T03:00Z — my fix for RH16 shipped a wrong denominator, the
## exact error I had called the dangerous one

Pass 6 reported seven vaccines improving at once:

    monotonic-utc-generations  14 -> 11 of 15
    pinned-actions             10 ->  8 of 15
    chaining-token             10 ->  9 of 15
    least-permissions           6 ->  5 of 15
    ...

Nothing improved. The denominator moved from 18 to 15, because RH16's new guard
correctly declined to measure `claude`, `cvaa` and `pipelinenews` — all three
mid-write. Every "improvement" is a repository that was **not looked at**.

I wrote in RH11 that *"a wrong denominator is worse than a wrong finding — a
wrong finding gets checked, a wrong denominator gets quoted"*, and then shipped
one two hours later as a side effect of fixing something else. The guard was
right; the reporting built on top of it was not, because incidence was still a
raw count over "however many repositories happened to be measurable".

**Fixed by changing the unit of comparison, not by patching the arithmetic.**
The driver now stores, per repository, the set of vaccines it is not immune to,
and diffs **per repository over the repositories measured in both passes**:

    [VACCINE-RED]   gridatlas now fails attestation-freshness
    [VACCINE-GREEN] cvaa no longer fails monotonic-utc-generations

A repository absent from either pass simply does not appear. Counts are still
kept in `spider-state.json` alongside `incidence_denominator`, so a total can
never again be read without the number it is out of.

This is the third time tonight a correction has created its own defect —
RH13 (the ruler guard that would have raised a false ruler alarm, caught before
it fired), RH16's addendum (the commit that described a guard it did not
contain), and now this. The pattern is specific enough to name: **a guard
changes what gets measured, and every summary computed downstream of it silently
changes meaning.** Fixing a measurement is not finished until every number
derived from it has been re-derived.

---

## RH19 — 2026-09-03T03:10Z — a git-clean tree is not a byte-clean tree, and
## the difference lies in BOTH directions

My `tree_state` guard (RH6, RH16) asks `git status --porcelain`. gridatlas
answered `dirty=0`, so I measured it and believed the result. `git status` compares
through `.gitattributes` normalisation, so **it reports clean while the bytes on
disk are CRLF and the blob is LF.** Clean tree, wrong bytes.

The same vaccine run, same commit `8fb95a2`, one in the OneDrive working copy and
one in a fresh clone:

    OneDrive copy (git-clean, CRLF bytes)   clean clone (LF bytes)
    ------------------------------------    ----------------------
    FAIL pointer-verifies                   — absent
    — absent                                FAIL on-ledger-commits
    (8 others identical, including attestation-freshness)

**One false positive and one hidden real finding.** I had been about to report
`atlas/releases/202608300453-atlas-v9 checksums do not verify` — that the
currently-pointed-to release fails its own manifest. Checked directly:

    clean clone:      sha256sum -c sha256sums.txt --quiet   rc=0
    OneDrive copy:    sha256sum: '202608291818-place-postcode-search.js'$'\r':
                      No such file or directory                rc=1

The mechanism is a variant worth knowing: it is not the hashed files that differ,
it is **`sha256sums.txt` itself** ending its lines with CRLF, so `sha256sum`
looks for filenames with a trailing carriage return and cannot open them. The
manifest, not the payload.

That would have been my second false report of a serious defect tonight, and a
worse one than the first — "the live release does not verify" is the kind of
sentence that stops work.

**What I changed.** `tree_state` returning clean is necessary and not
sufficient. Any measurement whose answer depends on file *bytes* — digests,
checksum manifests, byte-identity — must be taken from a clean clone of the
published HEAD, not from a working copy that merely has no pending edits. The
cheap discriminator is `git ls-files --eol | grep -c w/crlf`; gridatlas answers
239, and 15 of 18 repositories on this machine answer non-zero (RH14).

**Confirmed real on gridatlas at 8fb95a2**, holding in both measurements and
therefore not an artefact: `attestation-freshness`, `rollback-exists`,
`no-time-based-gates`, `executor-declared`, `loop-exists`,
`monotonic-utc-generations`, `chaining-token`, `no-per-release-workflows`, plus
`on-ledger-commits` which only the clean clone could see.

This is the fourth correction tonight in the same family — RH14 (the pointer
mismatch), RH17 (the deleted string), RH8 and RH9 (text about code) — and they
converge on one rule I should have started from: **measure the artefact, never
the workspace.**

### RH19 addendum, 2026-09-03T03:14Z — I pushed a driver that does not parse

The RH19 patch was applied by a shell heredoc containing `out.split('\n')`. The
heredoc consumed the escape, wrote a literal newline inside the string, and my
patch script wrote the file **before** validating it. `pass.py` was committed and
pushed in a state where `python -c "import ast; ast.parse(...)"` fails, so the
next pass would not have run at all.

This is the third time tonight a shell heredoc has silently eaten a backslash
escape in a Python patch — it also broke `crosslink.py` and an earlier
`pass.py` edit. Twice I caught it because the script refused to run; this time
the write came first and the check came second, so it reached the remote.

**Two changes, both mechanical:**

1. Patches to the driver are applied with a file edit, never a shell heredoc.
   The failure mode is not "I mistyped an escape" — it is that a heredoc is a
   second, invisible layer of escaping between what I write and what lands.
2. Validate, then write. My script did `write()` then `ast.parse()`, which is the
   wrong order and is exactly the same shape as RH16's addendum, where the
   account of a fix was committed by an `&&` chain that the fix itself had not
   passed through. **A verification that runs after the irreversible step is not
   a verification.**

Both times the artefact reached the remote in a state I had already decided was
unacceptable, because the ordering let it. That is a more useful lesson than
either individual bug.

---

## RH20 — 2026-09-03T03:16Z — I was about to report another agent's feature
## branch as an estate regression

Pass 7 produced one apparently real red:

    [CI-RED] gridatlas :: 202609030251 Build GridAtlas v9.89 grid-data verified
             -> failure @b67d0a0 2026-09-03T03:00:32Z

Before reporting it I checked which branch it belonged to:

    $ git ls-remote origin | grep b67d0a0
    b67d0a02…  refs/heads/codex/202609030251-grid-data-v9-89
    $ git ls-remote origin refs/heads/main
    8fb95a21…

It is a Codex feature branch, on its first run, and `main` is elsewhere and
fully green — cartridge proof, next-version builders and pages deployment all
succeeded at both `1fb6262` and `8fb95a2`. A new workflow failing its first
run is how new workflows start; the cartridge-proof workflow's own header says
exactly that about itself.

**This is the pass-2 error one level out.** There I ran a gate against a working
tree an agent was mid-write in; here I read CI for a branch an agent is
mid-build on. Same mistake, different surface: I measured someone's work in
progress and was ready to call it drift. The dirty-tree guard I built for the
first case simply did not reach the second, which is RH16's lesson again — *a
correction applied to one call site is not a correction.*

**Fixed:** `ci()` now filters `workflow_runs` to `head_branch == 'main'`. Only
the default branch describes the estate. Feature-branch CI belongs to whoever
owns the branch, and reporting it costs them attention and costs me credibility.

I have now made this class of error four times — dirty tree (RH6), dirty bytes
(RH14, RH19), and now a non-default branch. Each time the shape is identical:
**I measured a workspace mid-change and described it as a state.** The estate is
four agents deep and nothing here is ever at rest; a measurement that does not
say which commit, which branch and which bytes it read is not a measurement.

---

## RH21 — 2026-09-03T03:42Z — D14 was never real. I reported it twice, and my
## own cross-check could not catch it because both checks used the same
## broken instrument.

I filed D14 — "the gridatlas live attestation is four days and ten releases
stale" — and told the coordinator it was *"confirmed in both the working copy
and a clean clone, so not an artefact"*. Then, when it went green, I filed a
second report saying the vaccine had been silenced by commit wording.

**Both messages were wrong.** The attestation was never stale. Measured directly
from the two JSON files at every relevant commit:

    commit    atlas/current.json generation   live-set.json generation
    8fb95a2   202609030234                    202609030234    MATCH
    1762170   202609030234                    202609030234    MATCH
    cc449d5   202609030234                    202609030234    MATCH

`live-set.json` was last written at `8fb95a2`, the same commit that set the
pointer generation, and `1762170` and `cc449d5` were tooling changes that cut no
new composition — so the pointer legitimately did not advance and the
attestation legitimately did not need to. The state was correct throughout.

What fired was `attestation-freshness`'s heuristic: it finds the newest commit
subject matching `/live|verif|accept/` and the newest matching
`/scope|cartridge|compos|promote/` and complains if the first is older. At
`8fb95a2` those happened to fall in that order. It never opened either file.

**The lesson, and it is the sharpest of the night.** I built the clean-clone
discipline (RH19) precisely so a finding could not be an artefact of my
environment, and I leaned on it explicitly in the D14 message. It did not help,
because **reproducing a finding in two places does not validate it when both
places run the same instrument.** The clean clone controls for environment; it
controls for nothing about whether the check measures what it claims. Two
identical wrong answers read exactly like corroboration.

What would have caught it is what finally did: **going to the underlying state
and comparing the two numbers myself.** Both files were sitting in the vaccine's
own context object. I had been treating "the vaccine says so, twice" as evidence
when the vaccine's own antibody was four lines long and readable in ten seconds.

`disk-is-not-what-ships` I distrusted immediately because it fired on 18 of 18 —
the wall was conspicuous. `attestation-freshness` fired on 1 of 18, which looked
like a specific finding rather than a broken rule, and specificity is not
evidence either.

**What I changed.** Any vaccine finding I intend to report is now read at the
antibody and confirmed against the underlying data before it leaves this
machine. Reproducing it is not enough. `01-drift.md` records D14 as withdrawn,
not as fixed, because it was never a defect.

**What remains true**, and is worth separating from my error: the vaccine cannot
measure what it names. It infers freshness from prose, so it will report a stale
attestation as fresh whenever a single commit subject contains both a
verification word and a composition word — a false negative, which is the
dangerous direction. That finding stands on its own and does not depend on
gridatlas having had a defect.

### RH21 addendum, 2026-09-03T03:46Z — auditing the rest of my own headline

After withdrawing D14 I read the antibodies behind every finding I have reported
as fact, which is what I should have done before reporting any of them. Result:

**Substantive — they read state, and my numbers stand:**

- `pinned-actions` — scans workflow text for actions not pinned to a 40-char
  SHA. Hand-confirmed against cvaa's own workflow at 01:20Z.
- `monotonic-utc-generations` — compares commit generation stamps against
  `%cI`. Hand-confirmed against my own commits (RH4, RH12); it caught me.
- `chaining-token` — finds `git push` in a workflow with no App token.
- `no-per-release-workflows` — counts timestamped workflow files against a
  declared baseline.
- `loop-exists` — checks for `schedule:` in the scope-loop workflow.
- `rollback-exists` — went immune at `1762170` alongside 238 lines of
  `tools/rollback.mjs` and a 180-line workflow, so the verdict and the artefact
  agree. D13's closure holds.

**Prose-dependent — a second instance of the D14 class, narrower:**

`on-ledger-commits` requires each generation-stamped commit to cite a scope
file, then exempts any commit whose subject matches
`/verify|roll ?back|inoculate|drill/i`. So a commit can exempt itself from the
ledger by wording. Unlike `attestation-freshness`, prose is only the escape
hatch rather than the whole test — but it is the same defect: **a rule about
what was done, decided by what was written about it.**

Two of the 25 active vaccines carry prose-dependent logic. That is the caveat
that belongs on every estate-wide figure in `01-drift.md`: the incidence table
is as good as the antibodies behind it, and I have now read all of them rather
than trusting the runner.

---

## RH22 — 2026-09-03T04:20Z — context-diet, applied to me

The brief says later passes must get shorter as the estate stabilises. Measured,
words per pass entry in `00-LOG.md`:

    Pass 1  437    Pass 4  213    Pass 7  204
    Pass 2  600    Pass 5  261    Pass 8  187
    Pass 3  140    Pass 6  275    Pass 9  136

Downward, and the peak is diagnostic: **pass 2 is the longest entry I wrote and
it is the pass whose headline finding was false.** The false red needed six
hundred words because it had to be argued; the true findings since have needed
under two hundred because they could be shown. Length has tracked doubt rather
than substance.

Where I am not on diet: `01-drift.md` and `02-runner-health.md` are ~45 KB each,
about 2 KB per entry. Those are standing documents rather than per-pass, so
growth is expected — but the reasoning in a runner-health entry is the deliverable
(the brief asks what I changed, not merely that I was wrong), so I am keeping it
and noting the cost rather than pretending there isn't one.

`crosslink.json` is 2.2 MB, which is 6,854 edges of which 335 are dependencies.
A consumer wanting the dependency graph should filter
`evidenceTier == "shipped"` and get a file about twenty times smaller. That is
stated in the artefact's own `method` field and in `03-crosslink.md`, but the
default shape is still the fat one, and defaults are what get used. If I were
starting again I would emit the shipped graph as the artefact and the full scan
as an appendix.

---

## RH23 — 2026-09-03T03:54Z — the clock error came back a third time, in the one
## place I had not mechanised

    $ date -u    2026-09-03T03:53:52Z
    $ date       2026-09-03T04:53:52 GMTDT

I have been narrating times roughly thirty minutes ahead of UTC for the last
hour — "still 1c9909d at 04:09Z" when it was 03:39Z, "waiting for the window at
04:46Z" when it was 04:16Z, and I told the coordinator I had 4.6 hours left when
I had 5.1.

**The commits are correct.** Every stamp since RH12 comes from
`date -u +%Y%m%d%H%M` evaluated in the same command as the commit, and every one
matches its `%cI`. The mechanism held exactly where I put it.

**The prose is wrong**, because I never mechanised that. RH4 named the error,
RH12 recorded that naming it had not fixed it and mechanised the commit stamp,
and I then went on reading clocks by hand everywhere the mechanism did not
reach. Same error, third venue: local `%cI` output in `git log`, arithmetic in
my head, and estimates extrapolated from an already-wrong anchor.

**What I changed.** No time appears in a message or a report unless it came from
a `date -u` I ran in that same turn. Where I need an interval — "hours to
09:00Z" — I compute it rather than estimate it. Nothing about my reasoning has
proved able to hold a clock.

The pattern across RH4, RH12 and this: **a correction only protects the call
site you install it at.** That is now the third time tonight it has been the
lesson — RH16 (guard on gates, not on cvaa), RH18 (guard changed the
denominator downstream), and this. The estate's own `monotonic-utc-generations`
would have caught all three of my commit-stamp errors and none of my prose ones,
for the same reason: it checks what is committed, and prose is not.

**Correction to the record:** every "Z" time I stated in a coordinator message
between roughly 03:15Z and 03:54Z is about thirty minutes late. The measurements
those messages carry — commit SHAs, counts, HTTP status codes, vaccine
verdicts — are unaffected, because none of them was derived from a clock.

---

## RH24 — 2026-09-03T04:35Z — I never measured my own instrument, and then built
## a mechanism that entrenched the false constraint

`CLAUDE.md` says: no gh CLI, 60 requests/hour shared, and
`/actions/runs/<id>/logs` returns 403. I took all of it as fact for four hours.
Measured, all three in one minute:

    gh CLI                   absent          TRUE
    unauthenticated          limit 60,   remaining 35
    scripts/gh-api.sh        limit 5000, remaining 4992
    /actions/runs/<id>/logs  200, not 403

Every push in this estate already authenticates, so the credential helper holds
a token the whole time. My binding constraint was fictional.

**And I did not merely inherit it — I reinforced it.** At RH15 I wrote *"the
60/hour unauthenticated budget is per IP"* as though I had established it, built
a floor of 25 into `pass.py`, and told the coordinator I was rationing calls so
the estate's gates kept their share. A guard around a constraint that does not
exist is the most durable way to keep believing in it: every pass afterwards
printed `API-BUDGET 24/60 left`, which reads as confirmation.

**The cost, measured rather than estimated:**

- I reproduced the gridatlas cartridge-proof failure (D7) by cloning three
  repositories into a runner-like layout, because I believed the log was
  unreadable. The log names the cause in one line.
- D8 sat for four hours with a cause taken on trust — "authorisation freeze by
  design". Two minutes after gaining log access it turned out to be
  `AssertionError: timestamp release schema changed`, a producer/consumer
  divergence dating to 31 August.
- The estate itself paid: a nine-command cvaa step was split into five named
  steps specifically so a failure could be identified without log access.

**The pattern, and it is the cleanest instance of the night's recurring one:
I check what I am pointed at and not what I am standing on.** Twenty-three
runner-health entries interrogating vaccines, gates, trees, bytes, branches and
denominators — and not one line testing the sentence that told me my instrument
was crippled. The brief's own first principle is *"You have found nothing until
you have measured it"*, and the thing I never measured was the measuring.

**What I changed:** `pass.py` uses `scripts/gh-api.sh`; the budget floor is
removed; CI sampling covers every repository every pass instead of only those
whose HEAD moved. Added `ci-log.sh` for reading a run's log by id. The
`known_flaky` entry F3 — "check the API budget before trusting a pass" — is
withdrawn, because the gate that skipped on a 403 was skipping on a limit that
did not have to bind.

---

## RH25 — 2026-09-03T04:38Z — I counted someone else's skip as a failure, having
## invented that exact distinction for myself two hours earlier

Pass 11 reported:

    [VACCINE-RED] gridatlas now fails derived-state-not-authored
    [VACCINE-RED] gridatlas now fails rollback-exercised

Both false. cvaa `7c8ed09` added a **third result state**, and the runner now
emits `immune`, `fail` and `skipped`. Measured on a clean gridatlas tree:

    derived-state-not-authored   state=skipped   findings=-
    rollback-exercised           state=skipped   findings=-

`rollback-exercised`, rewritten at `93e568e`, returns
`{ skip: "no atlas/state/rollback-drills.json; emit one … and this rule can
decide. Commit subjects are not evidence that a drill ran" }`. That is a rule
declining to decide for want of evidence. It is not a finding, and gridatlas has
not regressed.

My driver classified anything `!= 'immune'` as a failure, so a new third state
became two red lines the moment it appeared.

**The part that stings.** RH6 and RH16 exist because I insisted a gate run
against a dirty tree is `unmeasurable-dirty-tree` — *a third state, never a
fail* — and I wrote that a verdict must never be manufactured from an absence of
evidence. Two hours later cvaa introduced the identical concept and I read it as
a failure. I built the idea and did not recognise it wearing someone else's
name.

**What I changed.** `now_fail` counts `state == 'fail'` only. Skips are tracked
separately and surfaced as `VACCINE-SKIP` — *"a skip is not a pass"* — because
the estate's discipline is that an undecided rule must be visible, just not
alarming. The two false entries are withdrawn from `spider-state.json`.

The night's recurring lesson, stated once more because this is its sixth
instance: **a correction protects only the call site you install it at, and
only in the direction you were looking.** I have now made this error against my
own gates, my own CVAA runs, my own denominators, a feature branch, my own
clock, and now another tool's vocabulary.

---

## RH26 — 2026-09-03T04:40Z — I named a value and not the file it lives in, and
## sent a reader to the wrong manifest

I reported that the pages gate expects
`pipelinenews.timestamp-folder-successor.v1` while "every recent release
carries" `pipelinenews.additive-cartridge-release.v1`. True of
`release-manifest.json` and misleading as written: grepping `releases/*/` for
any manifest schema also returns `atlas-current-link-manifest.v1` and
`current-atlas-link-build-manifest.v2`, and the coordinator lost minutes in the
wrong file because of it.

The gate reads exactly two names — `build-pages.py:641-642`:

    releases/<release_id>/release-manifest.json
    releases/<release_id>/build-manifest.json

And checking both, which I had not done, shows **both diverge**:

    release-manifest.json   expects timestamp-folder-successor.v1
                            carries additive-cartridge-release.v1
    build-manifest.json     expects timestamp-folder-build-manifest.v1
                            carries current-atlas-link-build-manifest.v2

So my report understated it: I found wall 1 and described it as though it were
the wall. **A schema value is not an address.** When a check reads a file by
exact name, the finding is the pair — file and value — and quoting the value
alone lets a reader search a directory that contains several plausible matches.

## RH27 — the control run, adopted as a habit

The coordinator's harness replaced the gate's `require()` with a collector so
one run walks as far as the code physically can: thirteen failing assertions for
`202609030009-pipelinenews`, then a `TypeError`, so everything past thirteen is
*unmeasured* rather than passing.

The part I want to keep is not the harness but **the control**. The same run
against `202608300309-pipelinenews` — the one release on
`current-atlas-link-release.v2` — fails nothing and completes. That single
comparison converts "thirteen assertions fail" from a possible instrument fault
into a property of the newer format.

I had the ingredients for this discipline and never generalised it. RH1 came
from noticing that a vaccine firing on 18 of 18 repositories was a wall rather
than a finding; I wrote *"a check that cannot fail is not a check"* and stopped
there. The symmetric rule is the one that was missing all night:

> **A sweep that returns the same answer for everything is a broken instrument.
> A sweep that returns a different answer for a known-good control is a
> finding.**

Applied backwards, it would have caught D14 in seconds — `attestation-freshness`
fired on gridatlas and nowhere else, and I treated that specificity as evidence
rather than running a control. Applied forwards, every estate-wide claim in
`01-drift.md` should carry one: a repository known to be clean on that rule, and
a statement that the rule stayed quiet there.

---

## RH28 — 2026-09-03T04:40Z — my headline answer was wrong all night: two of my
## "three vaccines that would fail most widely" fail nowhere

My brief asks for *"the three vaccines that would fail most widely"*. I answered,
from pass 1 onward and in three messages: `pinned-actions`,
`monotonic-utc-generations`, `chaining-token`.

Applying RH27's control discipline to my own table, I counted result **states**
rather than "not immune", and the picture changed:

    all 32 repos, 25 vaccines:   immune 727    fail 47    warn 26

    pinned-actions        immune 17   warn 15   fail  0
    least-permissions     immune 21   warn 11   fail  0
    monotonic-utc-gens    immune 18   warn  0   fail 14

`pinned-actions` declares `level: warning` on line 5 of its own vaccine file.
So does `least-permissions`. **They are warnings by design and fail nowhere in
the estate.** I had been counting `state != 'immune'`, which silently merges a
warning with a failure — and warnings are the estate's way of saying *known,
accepted, ratcheted, with a dated allowance* (`cvaa/cvaa.json` carries
`pinned-actions max 6 expires 2026-09-30`).

**The corrected answer to the question I was actually asked:**

| vaccine | repos failing (of 32) |
|---|---|
| `monotonic-utc-generations` | 14 of 32 |
| `chaining-token` | 12 of 32 |
| `self-terminating-loops` | 7 of 32 |
| `no-per-release-workflows` | 6 of 32 |
| `no-time-based-gates` | 3 of 32 |
| `pointer-verifies` | 2 of 32 |
| `rollback-exercised` | 1 of 32 |
| `executor-declared` | 1 of 32 |
| `loop-exists` | 1 of 32 |

Ordered by count, descending. **No rank column** — see RH29.

`self-terminating-loops` was never in any table I published. `pinned-actions`
led every one of them.

**This changes the adoption story, not just the ranking.** I said the estate's
remaining exposure was "almost entirely CI supply-chain pinning and generation
stamping". Half of that is wrong: supply-chain pinning is already a *warning*
the estate has consciously baselined with an expiry date. The real failing
surface is **47 vaccine-repo pairs**, and its top two are about the estate
misreporting its own time and pushing with the default token.

**Why I did not catch it sooner.** `not-immune` is the union of two states with
opposite meanings — one says *"this is broken"* and the other says *"we know,
here is the expiry"*. I built every count on the union because the runner's
summary line prints `immune` or not, and I never looked at the field. Nine
passes of a number I had defined wrongly, quoted three times.

Same family as RH18's denominator: **the arithmetic was right and the category
was wrong**, and a category error survives repetition because every recount
reproduces it.

### RH28 addendum — two denominators, kept apart

`pass.py` measures the **18 local clones** and reports drift on them; its
`incidence_denominator` is therefore whatever was measurable that pass (15 on
pass 13, three being mid-write). The **32-repo census** in `01-drift.md` is a
separate, periodic full-estate run including the 14 cold repositories cloned to
scratch.

Both are now stated with their denominator on every write, because RH18 was
exactly this confusion and RH28 was the same confusion about categories rather
than counts. A number in this session's files without a denominator beside it
should be treated as unfinished.

---

## RH24 + RH25 + RH28, consolidated — one failure, three instances, and the
## corollary that names it

The coordinator is right that these should not be filed as separate lessons.
The ceiling I never tested (RH24), the third state I never read (RH25) and the
field I never read (RH28) are one failure wearing three costumes, and the estate
already had the general form written down:

> **Measure the artefact, never the workspace.**

What was missing, and is worth more than any of the three incidents:

> ## **The instrument is part of the workspace.**

Everything I built tonight applied the first sentence outward — clean clones for
bytes, commit-and-branch discipline for CI, dirty-tree guards for gates — and
nothing applied it to the thing doing the measuring. The API ceiling, the
runner's state vocabulary and the meaning of its `level` field were all
workspace, and I treated all three as fixed background.

**The signature, which both of us hit in the same hour and which is the
practical test:** a sweep that agrees with itself across every subject is a
broken instrument, not a discovery. The coordinator's `.gitattributes` sweep
returned "no repository has one" for all 18 and was filed as a finding; my
`disk-is-not-what-ships` finding was 18 of 18; my vaccine table was recounted
four times and reproduced the same category error each time, which felt like
corroboration. **Agreement across subjects is not evidence. Disagreement with a
known-good control is.**

That pair — *the instrument is part of the workspace*, and *a control, always* —
is the whole of what I would carry out of tonight if I could carry one thing.

---

## RH29 — 2026-09-03T04:45Z — I read a rank as a count, in a table I wrote

I told the coordinator their handover said `self-terminating-loops` was 3 while
my census said 7, and handed back the seven named repositories to reconcile it.
There was nothing to reconcile. Their line 417 reads:

    | 3 | self-terminating-loops | 7/32 |

The leading `3` is the **position**, not the count. And the table is mine — they
took it verbatim from my 04:41Z message, where I had written the header
`| rank | vaccine | fails |` with two adjacent columns of small integers.

**So I authored the ambiguity, they reproduced it faithfully, and then I misread
my own table back at them.** That is a tidier failure than misreading someone
else's: the format was my choice, and the cost landed on the reader I chose it
for.

**Fixed rather than remembered.** The RH28 table now has one numeric column,
headed *"repos failing (of 32)"*, with values written `14 of 32` — a form no
reader can mistake for a position — and no rank column at all. Order still
carries the ranking; nothing needs to state it. The coordinator's framing is the
right one: *fix the table, do not remember the convention*, because a convention
has to be recalled by every future reader and a format does not.

**The part worth keeping is what made it cheap.** I sent the seven repository
names rather than the number 7, and that resolved a two-agent disagreement in a
single exchange. A count can only be agreed with or disputed; **a list can be
checked**. That is the same property as the control in RH27 — both work by
handing the other side something specific enough to contradict you with. The
generalisation:

> **When reporting a number that someone may need to challenge, report the
> members, not the cardinality.**

Every estate-wide figure in this session should therefore be reproducible to a
list, and `spider-state.json` already stores `cvaa.not_immune` as
per-repository vaccine *sets* rather than counts (RH18), so it is. The census
tables in `01-drift.md` are the summary; the state file is the evidence.

---

## RH30 — 2026-09-03T04:54Z — two of the coordinator's corrections are entries I
## already had, which is what makes them worth recording again

The coordinator hit two errors reaching the ahead/behind split, and both are
mine from earlier tonight in different clothes. Recording the pairing because a
failure mode that recurs across two independent agents in one night is a
property of the work, not of either of us.

**1. Concluding from a truncated read.** They ran the rule, read the first six
lines, saw only *"is earlier than previous"*, and hypothesised concurrent agents
committing out of order. The drift failures were below the fold.

That is RH5 exactly: I summarised `gridatlas run-current` from `tail -4`,
recorded "4 proofs" for a suite that runs 667 checks, and would have read a
composition change as a catastrophic regression. Both times the output was
correct and the *window onto it* was not.

The general form, which neither of us had written down: **a truncated read of a
complete output is indistinguishable from a complete read of a truncated
output.** `head`, `tail` and the first screenful are sampling instruments, and
a sample needs the same scepticism as any other measurement.

**2. An instrument that was silently wrong.** They attributed drifted commits
with `git log --grep=<generation>` and got the wrong commits back, because
several commits share a generation stamp. They discarded it and computed
per-commit from `%aI`.

That is RH17 and RH8: I counted a string a compiler exists to delete, and
counted retired cartridge generations as composed. All three are the same
mistake — **matching text that resembles the answer instead of computing the
answer** — and all three failed silently, returning plausible output rather than
an error.

Their observation is the sharper one, though, and I want it recorded: **the fact
that `--grep` returned multiple commits per generation is itself a symptom of
the disease being measured.** If stamps were read at commit time they would be
near-unique. A broken instrument that breaks *because of* the defect it is
pointed at is a genuinely difficult case, because its failure looks like noise
rather than evidence.

**Where this leaves the score.** Thirty runner-health entries. The recurring
families, now that there are enough to count:

| family | instances |
|---|---|
| measured a workspace mid-change and called it a state | RH6, RH14, RH19, RH20 |
| counted text *about* code as code | RH7, RH8, RH9, RH17 |
| a correction that protected only its own call site | RH12, RH16, RH18, RH23, RH25 |
| trusted a category or definition I never read | RH11, RH24, RH28, RH29 |
| concluded from a partial view | RH5, and the coordinator's first hypothesis |

Nothing in that table is about the estate. Every one is about the instrument.

---

## RH31 — 2026-09-03T05:13Z — I tested my own resume contract and it had a
## hidden dependency on state a fresh agent cannot have

`spider-state.json` is the brief's stated contract: *"write it so that a
completely fresh agent, given only that file and this brief, resumes exactly
where you left off."* I had asserted that for fourteen passes and never tested
it.

Tested by asking what each committed script needs that is not committed:

    census.sh depends on  $SC/estate  — the 14 cold repository clones, which
    live only in this session's scratchpad and are not in git.

A fresh instance running `census.sh` would have measured **18 repositories and
reported it as the estate**, with no error and no gap — the loop simply finds
nothing to iterate. Every "of 32" in the handover would silently have become
"of 18", and the immune count would have dropped from 14 to 0, because all
fourteen immune repositories are the cold ones.

That is the RH28 category error dressed as an infrastructure gap: a denominator
that changes without saying so.

**Fixed rather than documented.** `census.sh` now clones the fourteen if absent
— `git clone` costs no API budget — and prints `cold clones present: N of 14`
so the denominator is asserted before the measurement rather than inferred
after it. `how_to_resume` is rewritten as eight steps covering the real API
ceiling, the log reader, both denominators, and the guard list.

**The general form**, and it is the fifth family in RH30 pointed at myself:
**a contract you have never executed is a description, not a contract.** I
verified other people's fixes all night by running them in clean clones, and
verified my own resume path by reading it.

**Tested, not asserted.** Removed two cold clones and ran the self-heal block:

    before: 14 of 14   ->   removed 2 -> 12   ->   cold clones present: 14 of 14

Which is the point of the entry: the fix is verified the same way I verified
every other agent's fix tonight.
