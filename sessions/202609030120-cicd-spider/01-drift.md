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

Measured state if the estate were inoculated today — 18 repos, 28 vaccines,
`disk-is-not-what-ships` excluded as a proven false positive (RH1):

| vaccine | repos not immune |
|---|---:|
| `monotonic-utc-generations` | **14 / 18** |
| `chaining-token` | **10 / 18** |
| `pinned-actions` | **10 / 18** |
| `no-per-release-workflows` | 6 |
| `least-permissions` | 6 |
| `self-terminating-loops` | 6 |
| `no-time-based-gates` | 4 |
| `pointer-verifies` | 2 |
| `derived-state-not-authored`, `rollback-exists`, `rollback-exercised`, `executor-declared`, `loop-exists` | 1 each |
| the remaining 14 vaccines | 0 |

Findings by repo: pipelinenews 172, globalgrid2050 93, gridatlas 83,
chatgpt-audits 72, companies 31, data-gridatlas 21, data-centres-gb 13,
data-federation-map 9, data-grid-gb 8, data-gb-electricity 6, cvaa 5, claude 4,
spiders 3, data-interconnectors 3, grid-distance-maths 2, gb-electricity-ui 1,
gemini 1, codex-chatgpt 1. **Zero repositories are immune, including cvaa.**

The three that would fail most widely are worth reading as one sentence each:
`monotonic-utc-generations` says generations were chosen rather than read from
`date -u` at commit time; `chaining-token` and `pinned-actions` say the CI
supply chain is not pinned. Two of the three are about the estate lying to
itself about time and provenance, which is the same failure the spider exists
to catch.

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

Highest consequence item on this list, and the only one with a deadline —
it resolves the moment someone merges.

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
