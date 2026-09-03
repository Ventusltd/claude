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
