# Releases

One row per generation shipped: stamp, what it carries, gate counts before and
after, live SHA match.

---

## No generations were shipped, and the reason is structural

See `03-blocked.md` B2. A PipelineNews generation is only live once its release
directory is published to `globalgrid2050.com/pipelinenews_intelligence/<stamp>/`,
which lives in the `globalgrid2050` repository — out of bounds for this lane by
instruction. The other route, GitHub Pages, is jammed on an owner-authorisation
boundary I declined to move (B1). So no cut made tonight could have been
verified live, and the brief's own rule is that a cut which does not verify live
is not a generation.

Ten release directories pushed and published to nothing would have taken the
count of unpublished releases from 30 to 40 and told the architect nothing true.
Nine real cuts beat ten with one hollow; zero real cuts beat ten hollow ones.

---

## What did ship: tooling and proof, pushed to `Ventusltd/pipelinenews` `main`

These are not generations and are not counted as such. They are real changes,
each verifiable by running it. None of them touches a path in the `pages.yml`
trigger set (`releases/*-pipelinenews/**`, `releases/current-v*.json`,
`state/**`, `machine-learning/proofs/**`), so none of them provokes another red
deploy.

| commit | what it carries | proof |
|---|---|---|
| `78fbd42` | a release's digests describe the bytes it ships, not the bytes on disk. `sha256_published` existed and `cmd_check` used it; the four places that RECORD a digest did not (sidecars, build manifest, registry re-derivation, `sha256sums.txt`). Byte counts go through `published_size` so a recorded size and a recorded digest describe the same bytes. | `--check` census over all 32 release folders before and after: 6 failing, the same 6, unchanged. A no-op on a current checkout, which is the point: the recorded answer can no longer depend on whose machine ran the build. |
| `733cc5f` | a build proves the release against itself before declaring it built. Step 7 of `cmd_build` runs the release's own `cmd_check` and refuses on failure, before `build_ok["done"] = True`, so the existing atexit handler discards it. | end to end against `202608312037-pipelinenews` + `no-grading`. happy: exit 0, directory PRESENT. inject (one phantom ledger line naming a file never built): `FAIL: ... does not pass its own --check. Nothing shipped.`, exit 1, directory DISCARDED. Nine cartridges build cleanly onto that parent and all nine passed step 7, so the guard is not simply refusing everything. |
| `bc9de57` | `--applicable PARENT` answers whether a cartridge can actually be built, and `--list` marks each `[applied]` / `[new    ]`. | against `202609030009`: ALREADY APPLIED 15, CANNOT APPLY 4, **APPLIES 0**. Cross-checked against `202608312037`: APPLIES 9, ALREADY APPLIED 7, CANNOT APPLY 3, each reason named. |
| `b4c446a` | `202609030132-verify-wider-fleet-deep-link.mjs` — the wider fleet's own MAP link (a second emitter, which no contract check read) and the *values* it carries, against the allow-set in the composed GridAtlas. | 9/11 on `202609030009` against composition `202609030128` (v9.82). Two real failures, both named with counts. Refuses to skip: pointed at a path that does not exist it reports 6/8 and says so. |
| `1a9868e` | `docs/coordination/BOARD.md` — the three facts the GridAtlas lane needs before it widens `allowedTechnologies`, and the corrected Pages diagnosis. | n/a |

None of these paths is in the `pages.yml` trigger set, and the Pages workflow
run list confirms it: the newest run is still `47a99b0` at 2026-09-03T00:10:51Z.
My five pushes added no red run.

---

## Baseline gate counts, `origin/main` = `47a99b0`

| harness | checks | failed |
|---|---|---|
| `tools/intelligence/render_proof.mjs 202609030009-pipelinenews` | 26 | 0 |
| `tools/intelligence/surface_truth_proof.mjs 202609030009-pipelinenews` | 8 | 0 |
| `tools/intelligence/sector_render_proof.mjs 202609030009-pipelinenews` | 11 | 0 |
| `tools/intelligence/202609012300-verify-atlas-deep-link-contract.mjs 202609030009-pipelinenews` | 11 | 0 |

Verbatim output in `02-gates.md`.

## Live surfaces, measured 2026-09-03

| code | URL |
|---|---|
| 404 | `https://ventusltd.github.io/pipelinenews/` |
| 200 | `https://ventusltd.github.io/pipelinenews/releases/202608291447-pipelinenews/` |
| 404 | `https://ventusltd.github.io/pipelinenews/releases/202609030009-pipelinenews/` |
| 200 | `https://globalgrid2050.com/pipelinenews_intelligence/202609030009/` |

`202609030009-pipelinenews/index.html` is byte-identical between the repository
and the surface that serves it:
`dbd7df2f185bb5e9dd98b8885ca08a882c42e72ac2f5c6c073eda21664266b4d`.

On the root 404 (`F6`, and item 4 of the brief): it is not a routing gap that a
working deploy would close. `stage_site()` builds the Pages artifact from an
archived public closure plus the release trees, and the list of paths it
*requires* to exist —
`newsv1/index.html`, `newsv7/index.html`, `202608260159-pipelinenews/index.html`,
`releases/current.json`, the release path — contains no `index.html` at the site
root, and nothing in the staging code writes one. The root has never been
published, on any run, including the ones that succeeded. So a reader who trims
the URL gets nothing by construction, and closing it is a decision to author a
landing page, not a deploy repair.
