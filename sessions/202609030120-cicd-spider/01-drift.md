# 01 — standing drift

Everything currently wrong, oldest first. Each entry carries when it appeared
and whether anyone has touched it. Cleared entries move to `00-LOG.md`.

Pass 1 is the baseline: every item below is "first seen" and nothing here is a
regression yet.

---

## D3 — CVAA is wired into 1 of 33 repositories, and that one is itself
**First seen** 2026-09-03T01:30Z (pre-existing; the template
`cvaa/consumer-workflow-template.yml` was written 2026-08-30 and has never been
copied). **Touched since:** no.

`.github/workflows/202608301446-inoculate.yml` exists in `cvaa` and nowhere
else. `globalgrid2050` carries **241 workflow files** and no immune system.
`pipelinenews` carries 51, `data-gridatlas` 11, `data-federation-map` 8.

Two repositories have written an integration plan and not executed it:
`gridatlas/_build-plan/cvaa-integration-plan.md:64` and
`chatgpt-audits/202608310033-study/cvaa-integration-plan.md:64` both pin
`uses: Ventusltd/cvaa/.github/workflows/202608301446-inoculate.yml@d2ebc01f`.
Correctly pinned, in a plan, unadopted.

**Coverage complete: 32 of the 33 repositories**, measured 2026-09-03T02:28Z
against the **published** cvaa HEAD `d2893fa`, 25 active vaccines. Only
`pandapower`, an upstream fork last pushed 2026-04-25, is unmeasured.

Everything here was re-measured after RH11: my first three passes ran a local
cvaa two commits ahead of the remote and carrying an untracked vaccine, and
reported "zero repositories immune". That was wrong.

**14 of 32 repositories are already immune. 517 findings across the other 18.**

| vaccine | not immune |
|---|---:|
| `pinned-actions` | **16/32** |
| `monotonic-utc-generations` | **14/32** |
| `chaining-token` | **12/32** |
| `least-permissions` | 11/32 |
| `self-terminating-loops` | 7/32 |
| `no-per-release-workflows` | 6/32 |
| `no-time-based-gates` | 4/32 |
| `pointer-verifies` | 2/32 |
| `rollback-exists`, `rollback-exercised`, `executor-declared`, `loop-exists` | 1/32 each |
| the remaining 13 vaccines | 0 |

Findings by repo: pipelinenews 167, globalgrid2050 92, gridatlas 80,
chatgpt-audits 71, companies 30, data-gridatlas 20, claude 12,
data-centres-gb 12, data-federation-map 8, data-grid-gb 7, data-gb-electricity 5,
**cvaa 4**, data-interconnectors 2, solar-electrical-topology 2, spiders 2,
globalgrid2050-hompage 1, grid-distance-maths 1, registry_of_all_content 1.

**The split is the finding.** Every one of the 14 immune repositories is cold —
`Mahabharata`, `architecture`, `data_uk_dno_and_tso`, `pv-arc-protection-circuit`,
`reports`, `seed-data`, `uk-dno-data`, `v11`, `youengineer-code-review` and
five more. Every finding is in a repository an agent works in.
`monotonic-utc-generations` makes it sharpest: **14 of 18 active, 0 of 14 cold**.
It is not estate hygiene, it is a disease of agent-driven development — only
agent-driven repositories stamp generations at all, and the ones that stamp
them, choose them rather than reading `date -u`. I committed one myself within
the hour (RH4).

`pinned-actions` and `least-permissions` run the other way, 6/14 and 5/14 in
cold repositories nobody has touched in months. Those are old workflows that
predate the discipline, and nothing will trigger them to fix themselves.

**354 workflow files estate-wide.** `globalgrid2050` alone carries 241.

The adoption path this implies: fix D10 first (one line), then inoculate the 14
already-immune repositories, which go green on day one and cost nothing to keep
green. Beginning with pipelinenews at 167 findings produces a wall of red, and
a wall of red gets switched off.

---

## D4 — the cvaa vaccine `disk-is-not-what-ships` is structurally broken
**First seen** 2026-09-03T01:25Z. **Touched since:** no.

Reports "no .gitattributes" on 18 of 18 repositories. The antibody reads
`files['.gitattributes']`; `inoculate.mjs:96` populates `files` with exactly two
keys, `STATE` and `index`. The key is never present, so the branch fires
unconditionally, and the half of the vaccine that hunts for un-normalised
`createHash`/`hashlib.sha256` has never seen a source file. Full working in
`02-runner-health.md` RH1.

This matters beyond one rule: cvaa is the estate's immune system, and one of its
28 vaccines currently asserts a conclusion it has no evidence for. If cvaa is
adopted estate-wide before this is fixed, 33 repositories acquire a permanent
red light that means nothing, and the honest findings around it get discounted.
**Fix this before D3.**

---

## D5 — four repositories lack `* text=auto eol=lf`
**First seen** 2026-09-03T01:26Z, hand-verified. **Touched since:** no.

`chatgpt-audits`, `claude`, `codex-chatgpt`, `gemini` each have a
`.gitattributes` without the LF pin. The other 14 local clones are correct.
Low consequence — all four are agent-notes repositories, not shipping surfaces —
but recorded because it is the true form of what D4 falsely reports, and a later
pass must not confuse the two.

---

## D1 — globalgrid2050 homepage names a Grid Atlas release that is no longer current
**First seen** 2026-09-03T01:52Z. **Touched since:** not yet observed; gridatlas
HEAD moved at 01:20Z, so this is minutes old and may be a normal lag.

    $ python globalgrid2050/scripts/verify_published_versions.py
    PUBLICATION TRUTH: FAIL
      - the homepage names Grid Atlas v9.77 / 202609020018 as the current
        verified release while the live composition is v9.81 / 202609030119

**Confirmed DRIFT, not lag, at 2026-09-03T02:02Z.** I filed this with a note to
watch whether it cleared on its own. It has not, and the gap is widening:

    homepage names     v9.77 / 202609020018
    live composition   v9.86 / 202609030200
    gridatlas versions shipped past the homepage stamp: v9.78 .. v9.86, nine

globalgrid2050's own HEAD moved at 01:10Z (87e6da86) without refreshing the
stamp. This is not a publish that has not caught up; it is nine publishes that
have not. The homepage version is being treated as a field that follows rather
than as the thing being cut.

**And the gate itself degrades silently.** At 02:02Z it printed

    skipped: pipelinenews lineage head: HTTP Error 403: rate limit exceeded

four lines above its verdict, and reported PUBLICATION TRUTH anyway. The 60/hour
unauthenticated budget is per IP and shared by four agents and by the estate's
own gates; I had exhausted it myself (RH15). So this verdict can be produced
from a strictly smaller set of checks than it names, and nothing in the verdict
line says which. It should fail closed, or carry the skip into the verdict.

Note the shape: this gate reads `gridatlas@main/atlas/current.json`
(`verify_published_versions.py:54`) — unpinned — so it is a truth check whose
input the subject controls. It cannot distinguish "the homepage is stale" from
"gridatlas moved". Today those are the same thing; they will not always be.

---

## D2 — three shipped gridatlas cartridges fetch data-grid-gb at `main`, and
## data-grid-gb has a 882-record change loaded on a branch
**First seen** 2026-09-03T01:05Z. **Touched since:** reported to main
2026-09-03T01:08Z; awaiting a decision.

Full working in `03-crosslink.md`. In one paragraph: `b91e45b` on
`codex/20260903-phase0-integrity` changes 882 of 886 connection points and drops
`with_location` 502 → 489, while leaving the schema string
`data-grid-gb.connection-points.v3` unchanged. Three shipped cartridges fetch
that file at `@main` and validate only the schema string. On merge the map
silently states different numbers at the same generation stamp.

**RESOLVED 2026-09-03T01:44Z** in gridatlas v9.83 (4a17fa3), 39 minutes after
it was reported. `atlas/modules/202609030137-pinned-products.js` pins all three
runtime fetches to a commit with a SHA-256 and a byte count, and its own header
records the reasoning: *"a schema string defends SHAPE and is blind to VALUES"*,
with COWLEY 10→5 and ABHAM 4→2 transformers cited as the measured case. Neither
composed cartridge fetches a branch any more.

**Still open on the data side:** `data-grid-gb` b91e45b remains on
`codex/20260903-phase0-integrity`; `origin/main` is 1c9909d, which is exactly
what the new pin names. Moving the pin is now a deliberate, visible cut, which
is the point. The sequencing question stands: the merge and the pin move should
be one event.

**Estate mutable runtime edges: 5 → 2.** Remaining:
`pipelinenews → globalgrid2050@main/dist/major_project_news_v9_5_1.json`
(`index/202608261927-compile-index.mjs:128`) and
`globalgrid2050 → gridatlas@main/atlas/current.json`
(`scripts/verify_published_versions.py:54`).

---

## D6 — three consumers hold a Grid Atlas published-path shape that was retired
**First seen** 2026-09-03T01:30Z, by HTTP against the live surface.
**Touched since:** no. Nobody has recorded this.

gridatlas migrated its published release path. Measured:

    404  https://ventusltd.github.io/gridatlas/202608300453-atlas-v9/
    404  https://ventusltd.github.io/gridatlas/202608292311-atlas-v9/
    404  https://ventusltd.github.io/gridatlas/202608291239-atlas-v9/
    200  https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/
    200  https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/
    200  https://ventusltd.github.io/gridatlas/atlas/releases/202608291239-atlas-v9/
    200  https://ventusltd.github.io/gridatlas/atlas/            (the live app)

gridatlas is healthy and its own `atlas/current.json:8` names the new shape
(`release_route: /gridatlas/atlas/releases/202608300453-atlas-v9/`). Three
consumer artefacts still hold the old one:

1. `companies/state/atlas-v9-link-contract.json` — `base_url`, `golden_url` and
   `url_template` all at `/gridatlas/202608300453-atlas-v9/?repd_ref={repd_ref}`.
   This is the company-to-map deep-link contract and its golden URL 404s. The
   equivalent at the new path works: `/gridatlas/atlas/?repd_ref=13599` → 200.
2. `companies/.github/workflows/202608300312-sync-gridatlas-v9-link-contract.yml:96`
   builds URLs in the dead shape. Its schedule is `cron: '25 4-8 30 8 *'` —
   four hours on 30 August, once a year. It has already passed and will not run
   again until 2027, so it cannot self-heal.
3. `data-gridatlas/.github/workflows/202608291239-verify-live-pointer.yml:123`
   asserts `live_url == 'https://ventusltd.github.io/gridatlas/202608291239-atlas-v9/'`
   and would `SystemExit('app binding mismatch: live_url')` if it ran. It is
   `push`-triggered on three paths, so it is dormant rather than red.

**Why nothing is red.** All three are dormant. A once-a-year cron and a
path-filtered push trigger mean a broken contract produces no signal at all.
This is the failure mode the estate should care about most: not a red light, but
no light. `companies` is not published on Pages (404), so no external user hits
the dead URL today — which is the only reason this ranks below D1 and D2.

Consequence is moderate and rising: `pipelinenews` committed
"the deep-link allow-set" at 01:33Z, so deep links are being worked on right
now against a contract artefact whose golden URL does not resolve.

---

## D7 — gridatlas CI has failed on four consecutive commits while the same
## proof passes locally
**First seen** 2026-09-03T01:43Z, from the Actions API. **Touched since:** no.

    202608312212 GridAtlas cartridge proof
      failure  e9491b6  01:17Z   (v9.80)
      failure  f1f430d  01:20Z   (v9.81)
      failure  52ebabc  01:28Z   (v9.82)
      failure  4a17fa3  01:38Z   (v9.83)

At 4a17fa3, with a clean tree, `node tools/proofs/run-current.mjs` exits 0 with
667/667. So the developer machine and the runner disagree about the same commit.

In this repository that disagreement has a history: `disk-is-not-what-ships`
was written after the cartridge proof "passed on Windows and failed on CI —
where it was right to fail", because it compared the shell adapter's bytes raw
and a Windows working copy holds CRLF where the blob holds LF. gridatlas has a
correct `.gitattributes` now, so that exact cause should be closed; something
else is producing the same signature.

**CAUSE FOUND AND PROVED, 2026-09-03T01:57Z.** Reproduced in a clean
runner-like checkout in scratch, never in anyone's working tree:

    gridatlas + grid-distance-maths                 rc=1   59/60    59 PASS  1 FAIL
    gridatlas + grid-distance-maths + data-grid-gb  rc=0   667/667  735 PASS 0 FAIL

The one failing check is
`tools/proofs/202609030137-substation-intelligence.proof.mjs:302-311`, which
resolves `../data-grid-gb/derived/gb-transmission-network.v1.json` or
`../../`. `.github/workflows/202608312212-cartridge-proof.yml` checks out
`gridatlas` and `Ventusltd/grid-distance-maths` side by side and nothing else.
The workflow's own header explains why grid-distance-maths is there --
*"the first run of this workflow failed for exactly that reason and was right
to"* -- and the same reasoning applies to a second sibling nobody added.

**The red light is the smaller half.** `run-current` exits at the first failing
proof, so the runner stops after proof 1 of 4: **59 checks execute and 675 do
not**. Inside that proof the eight real-data checks sit behind
`if (topologyModule && PRODUCT_FILE)`, so an absent product skips them in
silence rather than failing them. Those are the checks carrying the actual
measurements -- Cowley publishes ten transformer landings, Cowley reports FIVE
transformers not ten, at 400 kV five and at 132 kV five.

So the transformer-identity correction that v9.82 asserts and that data-grid-gb
b91e45b implements has never been verified by CI. It has only ever been verified
on a machine where the estate repositories happen to share a parent folder.
"A skip is not a pass" is standing estate discipline, and this is that failure
inside the guard rail rather than inside a release.

**The cut:** add a third checkout to the workflow, `Ventusltd/data-grid-gb` at
`path: data-grid-gb`, pinned with `ref:` to the same commit
`atlas/modules/202609030137-pinned-products.js` names (1c9909d today) --
otherwise CI validates against a moving product while the shipped app reads a
pinned one, which is F5 reappearing inside the guard rail. Then make a null
`PRODUCT_FILE` fail those eight checks rather than skip them.

`/actions/runs/<id>/logs` returns 403 unauthenticated, so the runner's own
output was never available; the cause was found by reproducing the environment
instead, which is better evidence than a log.

---

## D8 — pipelinenews has not deployed for two days
**First seen** 2026-09-03T01:43Z, from the Actions API. **Touched since:** no.

`Deploy PipelineNews Pages` has failed on nine consecutive heads since
2026-09-01, most recently 47a99b0 at 00:11Z. Meanwhile every local proof passes
(`render_proof` 26 checks, `sector_render_proof` 11, `surface_truth_proof` 8).

So what is being proven is not what is being published. The release directory
`202609030009-pipelinenews` verifies on disk and has never reached the surface.
`Claude-Codex board continuity` is also failing, since 2026-09-01T22:50Z.

---

## D9 — the data-gridatlas hourly watchdog has been red for two days
**First seen** 2026-09-03T01:43Z, from the Actions API. **Touched since:** no.

`Hourly watchdog 5484218a99a1cfde60c84daaa5aba001ebfcd697` has failed every
roughly three hours since at least 2026-09-01T10:04Z, always at head 5484218,
most recently 2026-09-03T00:13Z. `202608301931 Layer fidelity, V8 origin vs V9
delivery` also failed at 2026-09-02T08:19Z.

**CAUSE FOUND 2026-09-03T02:10Z, and it is D6. The watchdog is not broken — it
has been right for two days.** Reproduced in a clean LF clone at 5484218, each
step as CI runs it:

    resolve              rc=0   RESOLVED_VERIFIED_LIVE_POINTER, 65 parquet files
    probe data-pointer   rc=0   VERIFIED_WATCHDOG_PROBE
    probe data-release   rc=0   VERIFIED_WATCHDOG_PROBE
    probe consumer       rc=1   public fetch failed after 4 attempts:
                                .../gridatlas/202608291239-atlas-v9/release-manifest.json
                                HTTPError 404

    404  https://ventusltd.github.io/gridatlas/202608291239-atlas-v9/release-manifest.json
    200  https://ventusltd.github.io/gridatlas/atlas/releases/202608291239-atlas-v9/release-manifest.json

**D9 and D6 are one defect.** I had filed D6 as "nothing is red, there is simply
no light". That was wrong: one thing was red, hourly, since 2026-09-01, and I
had it filed separately as unexplained.

**The cut is not one line.** The old shape appears in
`.github/workflows/202608291239-verify-live-pointer.yml:123`,
`releases/current.json:13,23` and `state/live-set.json:13,23` — and
`atman/202608291507-current-integrity.py:158-163` requires those two pointer
files to be byte-identical AND their SHA-256 to equal
`contracts/202608291507-automation.json` `baseline.pointer_sha256`
(`08664a2f…`). Both pointers and the contract baseline must move together, or
the watchdog fails on the pointer check instead of the probe and an honest red
becomes a different red.

A watchdog that has barked continuously for two days is indistinguishable from
one that is not barking — which is why it took a reproduction rather than a
glance to find that it was telling the truth.

---

## D10 — cvaa's own CI is red
**First seen** 2026-09-03T01:43Z, from the Actions API. **Touched since:** no.

`202608301447 Self-test and full-history fleet audit` has failed since
2026-08-31, most recently at b725155 on 2026-09-01T22:49Z.

This compounds D3 and D4. The estate is being asked to adopt cvaa into 32 more
repositories; cvaa is not immune to its own vaccines (5 findings), one of its
vaccines is structurally broken (D4), and its self-test does not pass. Fix the
immune system before injecting it.

---

## D10 — cause found: cvaa's self-test asserts a vaccine count that drifted
**Updated 2026-09-03T02:28Z.**

`.github/workflows/202608301447-selftest.yml:41`

    if (run.results.length !== 23) throw new Error(`expected 23 active results, got ${run.results.length}`);

Measured against the published HEAD `d2893fa` in a clean clone:

    status      : immune       <- every vaccine passes
    results len : 25           <- the assertion demands exactly 23
    vaccine .md : 26 files, one superseded, so 25 active

The self-test was last edited 2026-08-30T18:26Z, when 23 was true.
`202608311458-release-name-convention` was added 2026-08-31T15:59Z and
`202608312045-page-data-block-parses` at 21:46Z, and CI went red that day.
**23 + 2 = 25.**

So cvaa is not failing its own vaccines — it is immune to all of them, and its
build fails on a hard-coded number that drifted away from the thing it
describes. That is `derived-state-not-authored`, one of cvaa's own vaccines,
inside cvaa's own self-test.

**The cut:** derive the count from the vaccine files on disk minus superseded,
or assert a floor rather than equality. One line, and it is the only thing
keeping the estate's immune system red.

---

## D10 — update: fixed at cvaa 791e24b; verified, not assumed
**2026-09-03T02:28Z.** The coordinator cut three commits; the first two were
their own broken gates (`57c19ea` fixed the second of two constants, `67c5e34`
used `require()` on a `.lock`, which reads it as JavaScript). `791e24b` is the
real one. Verified against a clean clone of it, with no working copy involved:

    line 28  md files 26 == lock keys 26                        MATCH
    line 41  active = 25   (readdir minus /^superseded_by:/m)
    line 43  run.results.length = 25                            MATCH
    inoculate . --no-write  rc=0, final line exactly
             "repo is immune to all vaccines on file"           MATCH
    run.status = immune, shallow = false                        MATCH

The hard-coded 23 is gone and the count is now derived from the vaccine files,
which is the cure rather than a new constant. Closing on the runner's
conclusion, not on this.

---

## D11 — cvaa's own self-test cannot run on a Windows machine
**First seen** 2026-09-03T02:27Z. **Touched since:** no. Low consequence,
recorded because of what it is rather than what it costs.

    $ node tools/selftest.mjs
    Error: ENOENT: scandir 'C:\C:\Users\...\cvaa-v\vaccines'

`tools/selftest.mjs:6`

    const here = new URL('..', import.meta.url).pathname;

On Linux `.pathname` yields `/home/runner/work/cvaa/cvaa/` and this is correct.
On Windows it yields `/C:/Users/…` — a leading slash before the drive letter —
and `join()` produces `C:\C:\Users\…`. **So this step passes on every runner and
cannot pass on any Windows laptop.** It is not a CI blocker.

`inoculate.mjs:12` does it correctly:

    const here = dirname(fileURLToPath(import.meta.url));

and that file carries an explicit comment about normalising CRLF so that "cvaa
cannot run on a developer machine at all" is avoided. The runner got that care;
the self-test did not.

Worth recording because cvaa is the estate's instrument for exactly this class
of defect — a check that answers differently depending on whose machine it runs
on — and it has one in its own tooling. One line: use `fileURLToPath`, never
`.pathname`.

---

## D1 — CLOSED 2026-09-03T02:31Z
globalgrid2050 `687d03f` — "the homepage names v9.86, in both places it names a
version". Re-ran the gate against the clean tree:

    PUBLICATION TRUTH: PASS - 25 published snapshots, all reachable,
                              newest is 202609030009

Nine versions of drift closed by treating the stamp as the thing being cut
rather than a field that follows.

---

## D12 — the publication gate now PASSES while omitting a check
**First seen** 2026-09-03T02:31Z. Owned by the globalgrid2050 lane; recorded
because the severity has changed direction, not because it is unowned.

The same run that cleared D1 printed:

    skipped: pipelinenews lineage head: HTTP Error 403: rate limit exceeded
    PUBLICATION TRUTH: PASS - 25 published snapshots, all reachable

`verify_published_versions.py:199` computes
`status = "PASS" if not failures else "FAIL"`, and `check_network` files its
rate-limit exception into `report["skipped"]`, which never joins `failures`.

While the gate was failing, the skip was cosmetic — the verdict was FAIL either
way. **Now that it passes, the skip is load-bearing.** A PASS computed over 24
of 25 checks, with the omission stated four lines above the verdict and nowhere
inside it, is the exact shape of "a skip is not a pass". It is strictly more
dangerous than it was an hour ago, and the trigger is a shared 60/hour budget
that any of four agents can exhaust at any moment — I did, at 02:02Z (RH15).

The fix is already in hand in that lane: carry the skip into the verdict. Noting
only that it is now urgent in a way it was not while the gate was red.

---

## Unconfirmed — gridatlas `attestation-freshness`
Pass 5 reported `attestation-freshness incidence 0 -> 1 of 18`, gridatlas,
"pointer changed after the last live attestation; re-verify". gridatlas had
**4 uncommitted paths** at the time, so this is not a measurement (RH16). It is
plausible on its face — gridatlas cut v9.80 through v9.86 in roughly two hours —
but it is recorded as unconfirmed and will be re-measured on a clean tree.

`no-time-based-gates` on gridatlas IS committed and does hold: three crons
pinned to 30–31 August 2026 in `202608310015-gridatlas-overnight-next-versions.yml`
and `202608310050-gridatlas-next-version-builders.yml`. Same class as the
`companies` once-a-year cron in D6 — schedules that have already passed and
cannot fire again until next year.

---

## D12 — CLOSED 2026-09-03T02:50Z, and correctly
globalgrid2050 `fafa4d2` — "the publication-truth gate stops saying PASS over a
check it did not run". Verified at the line:

    report["status"] = "FAIL" if failures else ("INCOMPLETE" if skipped else "PASS")

A skip now yields INCOMPLETE. That is the cure rather than a patch: the verdict
can no longer be computed over a smaller set of checks than it names. Open for
19 minutes.

---

## D1 — REOPENED 2026-09-03T02:50Z, and the second opening is the finding
The same run that closed D12:

    PUBLICATION TRUTH: FAIL
      - the homepage names Grid Atlas v9.86 / 202609030200 while the live
        composition is v9.88 / 202609030234

**This is not an oversight. gridatlas ships faster than the homepage can be cut
by hand.** Ten version cuts in three hours:

    v9.79 02:11  v9.80 02:16  v9.81 02:20  v9.82 02:28  v9.83 02:38
    v9.84 02:52  v9.85 02:56  v9.86 03:00  v9.87 03:33  v9.88 03:35   (local)

v9.87 → v9.88 was **ninety-six seconds**. The homepage stamp was cut twice in
the same window. The gate went FAIL → PASS → FAIL in fifteen minutes and will do
it again on the next cut.

The stamp is hand-authored at `globalgrid2050/index.html:103` —
`data_gridatlas_release:"202609030200-gridatlas-v9.86"`, plus a prose `note`
field carrying the version twice more in readable text. The gate compares that
authored string against a derived one, the live pointer. Two values required to
be equal; one written by a person, one computed by a machine; only the machine's
half moves on its own.

That is the disease `derived-state-not-authored` names. **The vaccine does not
catch it** — globalgrid2050 measures `immune` to it at `fafa4d2`, because the
antibody looks for state files drifting from git, not for a version string
drifting from a live pointer. Right about the class, blind to this instance.
Worth recording as a gap in the rule rather than a gap in the repository.

**The choice, which is the owner's:** derive the stamp at publish time from
`gridatlas/atlas/current.json` so the two halves cannot disagree; or, if
"current verified" is deliberately meant to lag the newest build, compare
against a declared `reviewed_release` and report drift from live as information
rather than FAIL. Cutting the stamp by hand again buys roughly nine minutes at
tonight's cadence.

---

## D6/D9 — still open at data-gridatlas `4dd5c2d`. The commit is adjacent, not
## the fix.
**Re-measured 2026-09-03T02:56Z.**

data-gridatlas moved 5484218 → 4dd5c2d, "the automation boundary names the file
that pins its line endings". The whole diff is one line:

    contracts/202608291507-automation.json
    +    ".gitattributes",

That is a good change and it addresses the neighbouring concern — the automation
boundary now declares the file its byte-level checks depend on, which is the
right response to RH14. **It does not touch the defect.** Re-run in a clean
clone at the new HEAD:

    resolve              rc=0
    probe data-pointer   rc=0   VERIFIED_WATCHDOG_PROBE
    probe data-release   rc=0   VERIFIED_WATCHDOG_PROBE
    probe consumer       rc=1   404 on
                                .../gridatlas/202608291239-atlas-v9/release-manifest.json

The hourly watchdog will keep failing. Recorded explicitly because **a HEAD move
in the right repository looks like a fix and is not one** — the cheapest possible
way for this to be marked handled and carried red into the 10:00 handoff.

Unchanged from the original entry: the cut binds four files —
`.github/workflows/202608291239-verify-live-pointer.yml:123`,
`releases/current.json:13,23`, `state/live-set.json:13,23` — and
`atman/202608291507-current-integrity.py:158-163` requires the two pointer files
to be byte-identical *and* to hash to `contracts/…-automation.json`
`baseline.pointer_sha256`. Both pointers and the baseline move together, or the
watchdog fails on the pointer check instead of the probe.
