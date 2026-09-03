# 00 — spider log

One block per pass. Drift only. Standing state is in `01-drift.md`; the resume
contract is `spider-state.json`.

---

## Pass 1 — 2026-09-03T01:19Z → 02:20Z — BASELINE

No diff is possible on a first pass. Everything here is the baseline against
which later passes report.

**Enumerated.** 33 repositories from the GitHub API (`users/Ventusltd/repos`).
18 are cloned locally; 15 are not, and all but one of those were last pushed
before 2026-08-31. 3 API calls spent of 60/hour. No `gh` CLI and no token on
this machine, so the Actions API is expensive and git answers HEAD locally.

**Runner liveness proven before any result was trusted.** `inoculate.mjs` takes
an arbitrary repo path (`node inoculate.mjs <path> --json --no-write`) and
returned differentiated verdicts — immune, WARN, FAIL, skip — across 28
vaccines. A uniform wall is the fake-findings signature; this is not one. The
`--permission` / `--experimental-permission` probe is present and selects
correctly on Node v24.19.0, so the historical Node-24 failure is fixed.

**CVAA across 18 repos.** Zero immune, including cvaa itself. 528 findings
total. Top three by incidence, with `disk-is-not-what-ships` excluded as a
proven false positive: `monotonic-utc-generations` 14/18, `chaining-token`
10/18, `pinned-actions` 10/18. Detail in `01-drift.md` D3.

**Gates: 12 discovered and run, 11 pass, 1 fails, 1 not runnable locally.**

    PASS  gridatlas   tools/proofs/run-current.mjs         4 proofs, all composed cartridges
    PASS  data-grid-gb derived/verify_connection_points.py 44/44
    PASS  data-grid-gb derived/verify_phase0_acceptance.py exit 0
    PASS  data-grid-gb chatgpt/verify_product.py           1735 sites, 1392 circuits
    PASS  pipelinenews render_proof.mjs                    26 checks
    PASS  pipelinenews sector_render_proof.mjs             11 checks
    PASS  pipelinenews surface_truth_proof.mjs              8 checks
    PASS  grid-distance-maths test/verify.mjs              34/34
    PASS  grid-distance-maths test/verify_nearest.mjs      54/54, 0 understatements
    PASS  grid-distance-maths test/verify_parity.py        446/446, py and mjs agree
    PASS  data-gb-electricity verify_price_decade_rollup.py
    FAIL  globalgrid2050 scripts/verify_published_versions.py   -> D1
    n/a   data-gb-electricity verify_bounded_growth.py     CI-only, needs an audit artefact

**HEAD moved mid-pass, twice.** `data-grid-gb` 1c9909d → b91e45b at 01:21Z
(branch `codex/20260903-phase0-integrity`, not main). `gridatlas` reached
f1f430d at 01:20Z and `globalgrid2050` 87e6da86 at 01:10Z. Dirty trees at
close: pipelinenews 8, data-grid-gb 0 (was 7, now committed), cvaa 3, claude 1,
codex-chatgpt 1. All expected — three agents are working.

**Crosslink graph built.** 524 cross-repo edges, 274 in shipped code, from 18
local clones, every edge citing a file and a line. `crosslink.json` +
`03-crosslink.md`. Load-bearing: `globalgrid2050` in-degree 10, `gridatlas` 7,
`pipelinenews` 5. Five mutable (`@main`) runtime edges against four pinned ones.
The federation map it is offered to currently holds **zero** inter-repo edges.

**Sent to main:** one message, on D2 — the mutable `gridatlas → data-grid-gb`
edge with a 882-of-886 change loaded behind it.

**Corrected myself three times.** RH1 a cvaa vaccine that cannot fail, RH2 four
gates I mis-invoked and called failures, RH3 an extractor blind to URLs split
across lines, which had hidden the single most important edge in the estate.
All three in `02-runner-health.md`.

**Open drift at close of pass 1:** D1 D2 D3 D4 D5. Next pass due 02:55Z.
