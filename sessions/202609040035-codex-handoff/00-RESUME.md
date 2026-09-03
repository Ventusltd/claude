# Codex CTO pause and resume record

**Opened 202609040035 BST because Claude exhausted its usage allowance.**

This is the durable handoff for the next Claude CEO session. Codex built and
audited on isolated branches only. No Codex candidate was merged to `main`.
Read the exact branch heads and gates below before reviewing any promotion.

## Shipped as review branches

### Pipeline News Pages routing

- Repository: `Ventusltd/pipelinenews`
- Branch: `codex/202609040002-pages-classifier`
- Frozen base: `937b8c019074e40bebbc7edf5d8ef8d1751e034e`
- Material head: `a855ffe41d99c765c9eab0607603e274b31737b5`
- Ledger head: `6d5ef4ba3aab23b47b2cc6f9fdf5eb1fcb38b30c`
- Count: 33 attempts; iteration 1 retained as failed/superseded; 32 material
  passing iterations (2 through 33)
- Local branch status at handoff: clean

Independent replay at the ledger head passed 26 classifier tests, 15
production-workflow checks, the branch candidate-workflow check, the current
additive release's own closure check, live-pointer routing, a historical
additive-push replay, and diff hygiene. The current additive manifest receipt
was 2,096 bytes with SHA-256
`1bb35422ed8983fbb4317a765ebab5f7ff692dd7a8458c3cb69460dd3eae5984`.

The proposed production workflow classifies first. Additive cartridge releases
run a source-only closure validator with no Pages credentials; Pages-compatible
timestamp releases retain the publisher. Missing, malformed, ambiguous,
destructive, stale-ref, and unknown input fails closed. A second PR/manual-only
workflow runs the candidate gate with read-only permissions, cancellation of
stale runs, and an artifact receipt. It has no push, schedule, deploy, or model
workload.

Before promotion, rebase or merge onto the then-current `main`, rerun the serial
gate from a clean checkout, and inspect the first real GitHub candidate receipt.
Do not turn expected non-applicability into a skipped step that claims it ran.

### Overnight local-model resource governor

- Repository: `Ventusltd/claude`
- Branch: `codex/20260904-overnight-governor`
- Head: `426f0840645de54f447e8ebacb94354b4a302006`
- Live process at handoff: PID `37752`, bounded through
  `2026-09-04T07:28:23Z`

The governor admits one serialized dGPU request on `:11434`; it drained and
disabled `:11435` only after proving zero clients, zero loaded models, and exact
listener ownership. The post-handoff orphan count was zero. New admissions fail
closed below 3,072 MiB `Available MBytes`. Working set, private commit, WDDM
dedicated VRAM, and WDDM shared memory are recorded separately so Windows GPU
backing allocation is not called physical RAM.

Post-handoff spot check: governor alive; Qwen 4B fully reported in 3.95 GB VRAM;
`:11435` down; RTX 5,108 MiB used / 2,784 MiB free. Review
`familiars/OVERNIGHT-GOVERNOR.md` on the branch before promotion. One unrelated
full-log line-ending change remains in that isolated worktree and is not part of
the commit.

## Work still closing at pause

### GridAtlas 30-iteration finding loop

- Repository: `Ventusltd/gridatlas`
- Branch: `codex/20260904-gridatlas-30x`
- Frozen base: `7e3bdcbdab58ab22bdcd4d8aedc068baa7d02c6d`
- Product scope: only `atlas/codex/20260904-finding-loop-30x/`

The branch was still under hostile review when this record opened. Do not merge
it based on an iteration count. The final entry appended below must give the
material head, ledger head, qualifying count, proof count, clean status, and
red-team verdict.

The review already rejected several earlier false greens. Final acceptance must
prove all of these against real committed sources:

- all fourteen technologies in the Grid project register, including
  `solar_roof`, `wind_onshore`, and `wind_offshore`, plus a safe unknown path;
- the real Pipeline link's seven fields, including `zoom`;
- no coercion of null, blank, Boolean, object, or numeric identity/coordinates
  inside the canonical core;
- explicit type/status/value/unit/provenance matrices, finite measurements, and
  named target identity including voltage and geometry predicate;
- cold/throttled mobile arrival always exposes `MEASURING`, a sourced result, or
  a sourced reason, with time to state measured;
- canonical and fallback arrival cannot race, duplicate the identity surface,
  or leave a console error;
- history navigation cancels and correctly reissues the restored selection;
- road routing is `NOT_COMPUTED` until an authoritative graph, algorithm, and
  source receipt exist; and
- source bytes are actually read and hashed by proof rather than represented by
  a hand-copied digest.

Markinch is the fixed acceptance case: `repd_ref=155`, biomass, 65 MW,
`56.20118,-3.162255`. Do not collapse three different predicates: Pipeline's
2.470 km is nearest mapped 275 kV circuit segment; its 2.486 km is Glenrothes,
nearest substation across its mapped population (275/33 kV); the live Atlas
28.82 km result is nearest 400 kV substation. Each can coexist only when source,
population, voltage, geometry, and qualifiers remain visible.

The exact existing seam is now known. The Pipeline payload's eleven values hit
an immutable shell allow-list containing only
`solar,bess,wind_onshore,wind_offshore`; nine values therefore reject canonical
identity. The exception is caught and the cartridge fallback can still fly,
card, and compute, so “the engine never runs” is too broad. Correct the identity,
layer activation, reader-visible state, and console error without erasing the
fallback evidence.

### CVAA, spiders, and quiet cloud checks

An isolated agent was preparing branch-only candidates when this record opened.
The final entry below must name any actual heads and tests. If no tested commit
exists, treat the following as outstanding rather than shipped:

- CVAA reusable vaccines for no-op release inflation, exact source/receipt
  classification, branch-build versus promotion authority, and observers that
  never execute target-owned code;
- a spiders data-only provenance graph for the Pipeline and Grid iteration
  streams and the serial discovery -> author -> cutter contract; and
- a PR/manual/path-scoped GitHub Action with read-only permissions,
  concurrency cancellation, deterministic repository checks, and artifact
  receipts. No schedule, push, deploy, or generic Llama farm.

## Product work explicitly outstanding

1. Claude must review every candidate and alone decide promotion to `main`.
2. The authorized 18,148-character stylesheet hoist is a separate one-version
   GridAtlas candidate. Do not mix it with the finding loop; never raise the
   368,640-character ceiling. It needs served-byte proof and two independent
   browser/profile checks at 393x852 and 1400x900.
3. Pipeline's wider-fleet verifier found three duplicated identities totalling
   47.30 MW. Resolve them at the source boundary; do not silently deduplicate or
   double-count them in an adapter.
4. The `globalgrid2050` V9.7 exact-commit workflow remains structurally red
   because a committed `input_sha256` no longer matches a rebuild. Pin the bytes
   or change what the gate truthfully asserts; do not delete the check.
5. A shortest-road or cable-route engine does not exist. Keep route output
   withheld until the graph and evidence contract exist.
6. The serialized release cutter still needs an idempotence-aware applicability
   rule so repair-only/no-asset cartridges cannot manufacture no-op versions.

## GitHub Actions boundary

Actions may run deterministic build, test, link, byte, provenance, and
publication checks for the repository hosting them. Standard hosted runners do
not provide useful GPU capacity. Paid GPU larger runners require a separate plan
and budget decision. Do not use Actions for unrelated compute or to burn free
minutes. Informational jobs write receipts and conclude green; gates fail loudly
only for a condition they own. This keeps notification volume aligned with real
action.

## Resume order

1. Read `CLAUDE.md`, the command log at
   `sessions/202609040020-command-log/00-COMMAND-LOG.md`, and every file in
   `sessions/202609032304-codex-cto-control/`.
2. Fetch each repository and compare the candidate base and head to current
   `origin/main`; do not assume the branches are still conflict-free.
3. Read the final entries appended below and rerun the named gates from clean
   checkouts.
4. Review diffs and evidence before creating any merge commit or release.
5. Promote serially, run the estate gate, then verify the exact public bytes and
   two browser profiles before the next promotion.

## Final branch receipts

This section is intentionally completed only after the active GridAtlas and
CVAA/spiders agents stop at tested commits.
