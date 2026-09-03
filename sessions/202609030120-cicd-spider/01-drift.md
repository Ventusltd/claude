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

**Coverage completed 2026-09-03T02:02Z: 32 of the 33 repositories.** The 14
that had no local clone were cloned to scratch and measured. Only `pandapower`
is unmeasured — an upstream fork, last pushed 2026-04-25, cold.

**354 workflow files across the estate. 546 findings. Zero repositories immune,
cvaa included.**

`disk-is-not-what-ships` is excluded from every row below as a proven false
positive (RH1); it reports 32/32 and means nothing.

| vaccine | all 32 | the 18 active | the 14 cold |
|---|---|---|---|
| `pinned-actions` | **16/32** | 10/18 | 6/14 |
| `monotonic-utc-generations` | **14/32** | **14/18** | **0/14** |
| `chaining-token` | **12/32** | 10/18 | 2/14 |
| `least-permissions` | 11/32 | 6/18 | 5/14 |
| `self-terminating-loops` | 7/32 | 6/18 | 1/14 |
| `no-per-release-workflows` | 6/32 | 6/18 | 0/14 |
| `no-time-based-gates` | 4/32 | 4/18 | 0/14 |
| `pointer-verifies` | 2/32 | 2/18 | 0/14 |
| `rollback-exists`, `rollback-exercised`, `executor-declared`, `loop-exists`, `derived-state-not-authored` | 1/32 each | 1/18 | 0/14 |
| the remaining 13 vaccines | 0 | 0 | 0 |

**The three that would fail most widely are `pinned-actions`, `monotonic-utc-generations`
and `chaining-token`** — two of the three are the CI supply chain going unpinned,
and the third is the estate misreporting its own time.

Splitting active from cold is the finding the totals hide.
`monotonic-utc-generations` is **14 of 18 in the repositories agents work in and
0 of 14 everywhere else**. It is not an estate-wide hygiene problem; it is a
disease of agent-driven development specifically, because only agent-driven
repositories stamp generations at all — and the ones that stamp them, choose
them. I committed one myself within the hour (RH4), which is the cleanest
possible corroboration.

`pinned-actions` and `least-permissions` run the other way: 6/14 and 5/14 in
cold repositories nobody has touched in months. Those are old workflows that
predate the discipline, and they will not fix themselves because nothing
triggers them.

Findings by repo, active: pipelinenews 172, globalgrid2050 93, gridatlas 83,
chatgpt-audits 72, companies 31, data-gridatlas 21, data-centres-gb 13,
data-federation-map 9, data-grid-gb 8, data-gb-electricity 6, cvaa 5, claude 4,
spiders 3, data-interconnectors 3, grid-distance-maths 2, gb-electricity-ui 1,
gemini 1, codex-chatgpt 1. Cold repos carry 1-3 findings each, most of which is
the false positive.

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

This is the estate's own gate, working. gridatlas advanced past the homepage's
stamp and the homepage has not caught up. Watch for it to clear on its own; if
it is still failing at 06:00Z it is not lag, it is drift.

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

A watchdog that has barked continuously for two days is indistinguishable from
one that is not barking. Consequence is low today and rises the longer it runs,
because it is the alarm that would tell the estate a data layer had drifted.

---

## D10 — cvaa's own CI is red
**First seen** 2026-09-03T01:43Z, from the Actions API. **Touched since:** no.

`202608301447 Self-test and full-history fleet audit` has failed since
2026-08-31, most recently at b725155 on 2026-09-01T22:49Z.

This compounds D3 and D4. The estate is being asked to adopt cvaa into 32 more
repositories; cvaa is not immune to its own vaccines (5 findings), one of its
vaccines is structurally broken (D4), and its self-test does not pass. Fix the
immune system before injecting it.
