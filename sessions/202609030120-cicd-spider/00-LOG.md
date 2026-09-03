# 00 — spider log

One block per pass. Drift only. Standing state is in `01-drift.md`; the resume
contract is `spider-state.json`.

---

## Pass 1 — 2026-09-03T01:19Z → 01:22Z — BASELINE

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

---

## Pass 2 — 2026-09-03T01:35Z — one gate went red, one new defect

**RETRACTED — see the pass 2 correction below.** `gridatlas
tools/proofs/run-current.mjs` pass → FAIL. Green at 01:20Z
on f1f430d (v9.81, exit 0); red at 01:35Z on 52ebabc (v9.82, committed 01:28Z),
664/667 checks, three failures:

    it reads the repository that owns the data, not a copy
    the product is named once, at data-grid-gb main, and is the v1 schema
    the sandbox cartridge is back under the 400 kB boundary...  340171 bytes

The first two are the D2 edge. The third disagrees with its own printed
evidence — 340,171 bytes is under 400 kB. Reported to main.

**HEAD moves.** gridatlas f1f430d → 52ebabc (v9.82). pipelinenews 78fbd42 →
1a9868e ("the deep-link allow-set"). claude 3e9aaa0 → f23d76c (mine).
data-grid-gb unchanged at b91e45b, still on `codex/20260903-phase0-integrity`;
`origin/main` verified by `ls-remote` at 01:34Z as still 1c9909d. **D2 has not
fired.** A 90-second poll is armed on it.

**CVAA.** pipelinenews 172 → 169 findings, claude 4 → 5 (mine). No vaccine
changed incidence.

**New:** D6 — three consumers hold a Grid Atlas published path that now 404s.
Found by HTTP against the live surface, not by any gate, because none of the
three triggers can fire. Nothing is red; there is simply no light.

**Corrected myself twice more.** RH4: I committed the pass-1 generation stamp in
BST — `202609030220` for an 01:22Z commit, 58 minutes ahead — which is the exact
disease of `monotonic-utc-generations`, the vaccine I had just called the
estate's most widely failing rule. RH5: I summarised a gate from `tail -4` and
recorded "4 proofs" for a suite that runs 667 checks.

### Pass 2 correction — 2026-09-03T01:45Z

**The pass 2 red was false.** I ran the gate against a tree another agent was
mid-write in, which my brief explicitly told me not to treat as a defect. Full
account in `02-runner-health.md` RH6. Measured again once the tree was clean:

    gridatlas 4a17fa3 (v9.83), tree clean, run-current rc=0, 667/667

**D2 is remediated, and I can confirm it from the bytes.** v9.83 added
`atlas/modules/202609030137-pinned-products.js`, which pins all three runtime
fetches to a commit with a SHA-256 and a byte count
(`data-grid-gb@1c9909d` ×2, `data-gb-electricity@d310e3c`). Neither composed
cartridge fetches a branch. **Estate mutable runtime edges: 5 → 2.** The two
that remain are `pipelinenews → globalgrid2050@main` and
`globalgrid2050 → gridatlas@main`.

**The real reds were in the Actions API, which I had not yet queried.** Keyed by
commit, so no working tree can corrupt them:

| repo | workflow | failing since | heads |
|---|---|---|---|
| `gridatlas` | 202608312212 GridAtlas cartridge proof | 01:17Z | e9491b6, f1f430d, 52ebabc, 4a17fa3 — four in a row |
| `pipelinenews` | Deploy PipelineNews Pages | 2026-09-01 | nine consecutive heads |
| `data-gridatlas` | Hourly watchdog 5484218 | 2026-09-01 | every ~3h, same head |
| `cvaa` | 202608301447 Self-test and full-history fleet audit | 2026-08-31 | b725155 |
| `globalgrid2050` | Verify published versions are reachable | 00:11Z | 864b92e, 87e6da8 — corroborates D1 |
| `companies` | 13 of 19 workflows | 2026-08-27..30 | dormant since |

The first is the sharpest: gridatlas CI is red on four consecutive commits while
the same proof passes 667/667 locally at the newest of them. Local and CI
disagree, which in this repository has meant `disk-is-not-what-ships` four times
before.

**Lesson, and it is the pass's real output.** On this machine a repository is
not a state — it is a state plus three agents writing to it. A measurement that
does not name the commit it measured is not a measurement. `pass.py` now guards
before and after every gate, and takes CI state from the API rather than from a
local run.

---

## Pass 3 — 2026-09-03T01:50Z — coverage completed, the graph corrected

Cloned the 14 unscanned repositories and measured **32 of 33** (only
`pandapower`, a cold upstream fork, remains). 354 workflow files estate-wide.

Regenerated the crosslink graph and had to correct it three ways before any
number was usable (RH7–RH9): a catalogue repository emitted 6,124 of 6,153
runtime-data "edges"; retired gridatlas cartridge generations were counted as
composed; and a URL inside a `.json` was counted as a fetch. **6,854 raw
cross-repo edges, 336 real ones.** Mutable shipped runtime edges **5 → 2**,
converging with the coordinator's independent count. One of the two should stay
mutable by design.

D7 cause proved in a clean runner-like checkout: the cartridge-proof workflow
never checks out `data-grid-gb`, `run-current` exits at the first failing proof,
and **675 of 735 checks had never run on a runner.** The eight real-data checks
were skipped in silence rather than failed.

---

## Pass 4 — 2026-09-03T01:56Z — one green, one retraction, no real movement

**GREEN.** `gridatlas 202608312212 cartridge proof` failure → success at
5a59e71 (v9.84). First green across five commits, taken from the runner's
conclusion. **D7 closed.**

**Every CVAA count fell by exactly one, and none of it was real.** The driver
now measures with the published cvaa rather than the working copy beside it, so
the untracked vaccine stopped firing. `pass.py` emitted the `CVAA-RULER` line it
exists to emit. Genuine movement this pass: none.

**Retracted the estate's headline number.** RH11: three passes of CVAA results
were produced by a local cvaa two commits ahead of origin carrying an untracked
28th vaccine. Re-measured against published HEAD `d2893fa`: **14 of 32
repositories are immune**, not zero. The top three survive unchanged.

**D10 cause found**, one line: the self-test asserts `results.length !== 23` and
there are now 25. cvaa passes every one of its own vaccines and fails its build
on a stale constant.

**RH12.** I recorded RH4, said I had fixed my BST-for-UTC stamps, and made the
same error five more times, drifting +2 → +45 minutes. A correction that changes
only what you intend changes nothing; the ones that held all became lines in
`pass.py`.

**Open drift:** D1 D3 D5 D6 D8 D9 D10. Closed: D2 (v9.83), D4 (not in the
repository — RH11), D7 (v9.84).

---

## Pass 5 — 2026-09-03T02:30Z — two guards fired correctly, one was missing

**Closed: D1** (globalgrid2050 687d03f, PUBLICATION TRUTH: PASS — nine versions
of drift) and **D10** (cvaa 791e24b; every assertion of the rewritten self-test
verified against a clean clone — 26 files = 26 lock keys, active 25 =
results.length 25, inoculate exit 0 with the exact expected final line).

**Both of my new guards were exercised and both held.** `CVAA-COMMIT` fired
rather than `CVAA-RULER` across cvaa's three commits — vaccine set unchanged at
25 rules, so a findings delta would have been real (RH13). `API-BUDGET 0/60
left, floor 25` withheld CI sampling so the estate's gates keep their share
(RH15).

**New: D11** — cvaa's own self-test cannot run on Windows
(`new URL('..', import.meta.url).pathname` → `C:\C:\...`). Passes on every
runner; not a CI blocker. Recorded because cvaa is the estate's instrument for
checks that answer differently per machine.

**New: D12** — the publication gate now PASSES while omitting a check. While it
was failing the skip was cosmetic; now it is load-bearing.

**RH16, and its addendum.** I had guarded gates against dirty trees and not the
cvaa half of the same pass. It showed at once — `gridatlas 80 → 79` and
`attestation-freshness 0 → 1` against a tree with 4 uncommitted paths, both
recorded as unconfirmed. Then the patch script's third assertion failed, it
exited before writing, and my `&&` chain committed a runner-health entry
describing a guard the driver did not contain. A record that can be committed
without the thing it records is not a record.

**Open:** D3 D5 D6/D9 D8 D11 D12. **Closed:** D1 D2 D4 D7 D10.

---

## Pass 6 — 2026-09-03T02:58Z — two closures, one denominator of my own

**Closed: D9.** data-gridatlas `8bf88da` — "the consumer probe reads the release
directory that is served". Verified in a clean clone: resolve and all three
probes green. An hourly watchdog red since 2026-09-01 is green, **and it was
right the whole time.** The commit before it (`4dd5c2d`) added `.gitattributes`
to the automation boundary — adjacent, not the fix — and I recorded that
explicitly, because a HEAD move in the right repository looks like a fix.

**Closed: D12**, correctly — a skip now yields `INCOMPLETE`, so a verdict can no
longer be computed over fewer checks than it names.

**Reopened: D1**, fifteen minutes after it closed, and the second opening is the
finding. Ten gridatlas version cuts in three hours, v9.87→v9.88 ninety-six
seconds apart, against a hand-authored stamp cut twice in the same window. Two
values required to be equal; one authored, one derived; only the derived half
moves on its own.

**Still open: D6's `companies` half.** HEAD untouched since 31 August, golden
deep link still 404, regenerating cron fires once a year.

**RH18.** Pass 6 reported seven vaccines improving at once. Nothing improved —
RH16's guard had correctly declined to measure three mid-write repositories and
the denominator moved 18→15. I called a wrong denominator the dangerous kind two
hours ago and then shipped one while fixing something else. Now diffed per
repository over repositories measured in both passes.

**F5 has no remaining instances** (RH17): five mutable shipped runtime edges at
01:05Z, two after v9.83, one after I found I had been counting a string the
pipelinenews compiler exists to delete.

**Open:** D1 D3 D5 D6 D8 D11. **Closed:** D2 D4 D7 D9 D10 D12.

---

## Pass 7 — 2026-09-03T03:04Z — no estate drift; three guards fired, one more built

All three guards added since pass 5 did their job on this pass: `CVAA-SKIP`
(claude, cvaa, pipelinenews mid-write), `BYTE-UNSAFE` (gridatlas and
data-gridatlas have CRLF drift, so byte-dependent vaccines are not reportable
from the workspace), and `VACCINE-BASE` (15 repositories baselined silently
rather than announced as 15 changes).

**One apparent red, withdrawn before reporting.** `gridatlas :: Build GridAtlas
v9.89 grid-data verified -> failure @b67d0a0` is on
`refs/heads/codex/202609030251-grid-data-v9-89`, a feature branch on its first
run. `main` is at `8fb95a2` with cartridge proof, next-version builders and
pages deployment all green. RH20: CI sampling now reads only the default branch.

**Genuine estate drift this pass: none.**

**New, confirmed in both a workspace and a clean clone:** D13 — gridatlas can
move its live pointer ten times in three hours and has no workflow that can move
it back. D14 — `atlas/state/live-set.json` still attests
`202608292311-atlas-v9` while the pointer has reached v9.88; the vaccine's own
Symptom section names that exact file.

**Withdrawn:** `pointer-verifies` on gridatlas. "checksums do not verify" was a
CRLF artefact — `sha256sums.txt` itself has CRLF lines, so `sha256sum` looked
for filenames ending in a carriage return. Clean clone returns 0 (RH19).

**Open:** D1 D3 D5 D6 D8 D11 D13 D14. **Closed:** D2 D4 D7 D9 D10 D12.

---

## Pass 8 — 2026-09-03T03:23Z — one real green, no new drift

`[VACCINE-GREEN] gridatlas no longer fails rollback-exists` — D13 closed, and
the verdict agrees with the artefact (238 lines of `tools/rollback.mjs`, a
180-line workflow, and `[COUNT] gridatlas workflow files 5 -> 6`).

`globalgrid2050` a0f93e8 fixed its dead Grid Atlas link. Verified against the
file rather than the diff — the diff shows an added line still carrying the 404
and the file does not. Every gridatlas URL in `index.html` now returns 200.

`API-BUDGET 24/60, floor 25` withheld CI sampling by one call. `CVAA-SKIP` and
`BYTE-UNSAFE` both fired correctly.

**Withdrawn: D14.** It was never a defect. `atlas/current.json` and
`atlas/state/live-set.json` both carry generation `202609030234` at every commit
I examined. I reported it twice, and told the coordinator it was *"confirmed in
both the working copy and a clean clone"* — which is where I went wrong.
Reproducing a finding in two places does not validate it when both run the same
instrument. See RH21; I have since read the antibody behind every finding I have
reported as fact, and the rest hold.

**Open:** D1 D3 D5 D6 D8 D11. **Closed:** D2 D7 D9 D10 D12 D13. **Withdrawn:**
D4 D14.

---

## Pass 9 — 2026-09-03T03:36Z — no estate drift; the only movement is repair

`CVAA-COMMIT` fired correctly on cvaa `77dcb28` — vaccine set unchanged at 25
rules, so any findings delta would have been real. `CVAA-SKIP` withheld four
mid-write repositories; `BYTE-UNSAFE` withheld byte-dependent verdicts for
data-gridatlas.

**D16 opened and closed inside six minutes.** I found that the word "cvaa" in a
comment had pulled `202608312212-cartridge-proof.yml` into
`full-history-checkout`'s scope; gridatlas fixed it without adding a spurious
`fetch-depth: 0` and without deleting the explanation — *"rewritten because the
finding was false, not because it was inconvenient"*.

**D15 recorded**: four of the 25 active antibodies decide from prose, proved by
`rollback-exercised` reporting gridatlas immune throughout the period
`rollback-exists` showed it had no rollback mechanism at all.

**Open:** D1 D3 D5 D6 D8 D11 D15. **Closed:** D2 D7 D9 D10 D12 D13 D16 + dead
schedules + the gg2050 dead link. **Withdrawn:** D4 D14.

---

## Pass 10 — 2026-09-03T04:06Z — the edge fired, the pin held, two rules rewritten

**`data-grid-gb` origin/main 1c9909d → 5181de3 at 04:02:57Z.** Watched since
01:05Z. The pinned URL still serves `11e28859a6d1` / 2,896,561 B; main now
serves `8db7171d9476` / 2,934,509 B. The shipped map is unaffected. Schema
string identical on both sides while 882 of 886 records changed — the diagnosis
confirmed in production. `gb-transmission-network.v1.json` changed content at
identical byte length, so only a digest catches it.

**`CVAA-RULER` fired on a real change** for the first time: 25 → 25 rules but two
antibodies rewritten. `attestation-freshness` and `full-history-checkout` now
read the artefact instead of commit prose. D15 half closed;
`rollback-exercised` and `on-ledger-commits` remain, and they are the false
negatives.

**`VACCINE-GREEN` ×2** on gridatlas: `no-time-based-gates`, `pinned-actions`.
Findings 74 → 66.

**Open:** D1 D3 D5 D6 D8 D11 D15. **Closed:** D2 D7 D9 D10 D12 D13 D16 + dead
schedules + gg2050 dead link. **Withdrawn:** D4 D14.
