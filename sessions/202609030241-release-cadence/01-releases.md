# 01 — releases

Repositories: `Ventusltd/data-gridatlas` (cycles 1-2) and `Ventusltd/gridatlas`
(cycles 4-5). The lane was moved twice by the coordinator; `02-blocked.md`
records both moves and what was left behind at each.

The gate is the runner's conclusion for the pushed commit, from
`https://api.github.com/repos/Ventusltd/data-gridatlas/actions/runs?head_sha=<sha>`.
Local runs are recorded as evidence, never as the gate.

| stamp | commit | what it carries | proof before | proof after | CI run | conclusion |
|---|---|---|---|---|---|---|
| 202609030241 | `4dd5c2d` | `.gitattributes` declared in `first_checkpoint_files`, so the automation contract guard's exact-set boundary matches reality again | guard `rc=1`, boundary mismatch, clean LF clone at 5484218 | guard `rc=0`, `VERIFIED_READ_ONLY_AUTOMATION_CONTRACT`, clean clone at 4dd5c2d | `33708576547` Automation contract guard | **success** |
| 202609030243 | `8bf88da` | consumer probe reads `atlas/releases/<id>/`; prefix declared as `public.app_release_prefix`; `live_url` and `release_route` each bound to what they now are | consumer probe `rc=1`, 404 on `.../gridatlas/202608291239-atlas-v9/release-manifest.json` | resolve `rc=0`, all three probes `rc=0`, guard `rc=0`, clean clone at 8bf88da | `33708715190` Hourly watchdog · `33708715223` Current integrity · `33708715205` guard | **success** (all three) |
| 202609030316 | `1762170` | `gridatlas` — `tools/rollback.mjs` + `rollback-composition.yml` + workflow-budget entry: the live composition can be moved back, and the tool refuses a target it cannot verify | `rollback-exists` FAIL, cvaa 791e24b on a clean clone of 8fb95a2; 85 findings | `rollback-exists` immune, 83 findings; lint PASS, composition PASS, 702/702 across 4 proofs | `33710776859` cartridge proof | **success** |
| 202609030319 | `cc449d5` | `gridatlas` — `tools/scope/verify-live.mjs` reads the expected composition from `atlas/current.json` instead of a 2026-08-30 literal | live predicate `false`, and false for every cut since 202608301624 | live predicate `true` against the served 202609030234 / v9.88 | `33710958571` cartridge proof | **success** |

## Baseline observations

`gridatlas` at `8fb95a2` (v9.88), 02:36Z, one API call:

    33708191973  202608312212 GridAtlas cartridge proof        success
    33708191948  202608310050 GridAtlas next-version builders  success
    33708190975  pages build and deployment                    success

Local at the same commit: `run-current.mjs` 702/702 across 4 proofs, rc=0;
`loop.mjs lint` scope-ledger=PASS.

`data-gridatlas` at `5484218`, before either cut:

    33698585358  Hourly watchdog 5484218…   2026-09-03T00:13Z  failure
    33606380156  202608301931 Layer fidelity 2026-09-02T07:59Z failure
    Automation contract guard — last run 2026-08-30 on b335aca, success;
      has not fired since, because .gitattributes is not in its push paths

## Rate-limit discipline

Polled `https://api.github.com/rate_limit` before each sample. Observed
remaining: 54 (02:36Z), 47 (02:39Z). Floor is 25; never approached. Four
API calls total across both cuts.
