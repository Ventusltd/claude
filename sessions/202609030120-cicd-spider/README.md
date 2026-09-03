# cicd-spider — file map

This session follows the spider brief's file names, not the estate default in
`claude/CLAUDE.md`. The mapping:

| CLAUDE.md expects | here |
|---|---|
| `01-findings.md` | **`01-drift.md`** — open defects, oldest first, each with when it appeared and whether anyone has touched it |
| `02-measurements.md` | **`02-runner-health.md`** — every case where MY OWN check was wrong, and what I changed |

Also here:

- **`spider-state.json`** — the resume contract. A fresh instance given only
  this file and the spider brief resumes exactly where the last one stopped:
  pass number, per-repo HEAD, gate commands *with their arguments*, CVAA results
  and the cvaa commit they were measured under, CI state keyed by commit,
  known-flaky classes, open drift, next pass due.
- **`pass.py`** — the driver. One pass, prints drift only. Every correction in
  `02-runner-health.md` that held is a line in this file; the two that did not
  hold were the two written only as prose.
- **`crosslink-shipped.json`** — **the one to adopt.** The estate dependency
  graph, `federation_contents_cartridge.v1` shape, 335 edges, every one live
  code citing a file and a line.
- `crosslink.json` — the full scan behind it, 6,854 edges and 2.2 MB. Only
  `evidenceTier: "shipped"` is a dependency; the other seven tiers are text
  *about* code. Kept for audit, not for use (RH22).
- **`00-LOG.md`** — one block per pass, drift only.
- `.cvaa-clean/` — gitignored working clone of published cvaa (RH11).

Read `02-runner-health.md` before trusting any number in the others.
