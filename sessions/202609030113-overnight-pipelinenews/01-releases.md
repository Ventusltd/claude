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

| stamp | commit | what it carries | proof |
|---|---|---|---|
| _(filled in below as each lands)_ | | | |

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
