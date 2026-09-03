# 00 — release cadence log

One block per cycle. What was cut, or why nothing was.

---

## Cycle 0 — 02:35Z–02:41Z — reassigned before cutting anything

Briefed as the gridatlas release cadence lane. Read `claude/CLAUDE.md`,
`202609021835-estate-and-corridor/07-routing-table.md`, `gridatlas/AGENTS.md`,
`STATE.md`, `atlas/current.json`, `202609030120-cicd-spider/01-drift.md`.

**Both queue items were already shipped by the gridatlas UI lane while I was
reading.** Measured, not assumed:

    1fb6262  v9.87  a straight line is not a route, and the card now says how far off   <- item 1, corridor scalar
    8fb95a2  v9.88  a 44 px action, and a long press that stands down for everything    <- item 2

Baseline observation at 02:36Z, one Actions API call, `head_sha=8fb95a2`:

    33708191973  202608312212 GridAtlas cartridge proof   completed  success
    33708191948  202608310050 GridAtlas next-version builders completed success
    33708190975  pages build and deployment               completed  success

So gridatlas HEAD was green on the runner, tree clean, and the UI lane was
cutting every few minutes. Local proof at 8fb95a2: `run-current.mjs` **702/702,
4 proofs, rc=0**. `loop.mjs lint` PASS.

I had begun scoping the third queue item (the three dead calendar-day crons in
`202608310015-...yml` and `202608310050-...yml`, the `no-time-based-gates`
finding) and had **not edited a single file** when the coordinator reassigned
me. Nothing in gridatlas was touched. Recorded in `02-blocked.md` so the finding
is not lost.

**New lane: `data-gridatlas`.** Nobody owns it tonight; its hourly watchdog has
been red since 2026-09-01.

---

## Cycle 1 — 02:41Z — `4dd5c2d` — the automation boundary names `.gitattributes`

Not the defect I was sent for. Found while establishing the baseline for it, and
it had to go first because it blocks the real cut.

`atman/202608291507-current-integrity.py:901` (command_guard):

    require(set(changed) == expected_files, "automation source boundary mismatch")

where `changed` is `git diff --name-status <baseline> HEAD` and `expected_files`
is `contract.first_checkpoint_files`. Commit `5484218` (2026-08-31) added
`.gitattributes` — **and nothing else** (`git diff --name-only b335aca 5484218`
is one line) — without declaring it.

**Proof before**, clean `--shared` LF clone at 5484218, 0 CRLF paths, pointer
digest `08664a2f…` matching `baseline.pointer_sha256` exactly:

    guard rc=1   automation source boundary mismatch
                 actual   = expected + '.gitattributes'

**Why nothing was red.** The guard's push paths are `.github/workflows/**`,
`atman/**`, `compiler/**`, `contracts/**`, `schemas/**`, the release dir, the two
pointers, `requirements.lock`, `runbooks/**`. `.gitattributes` is in none of
them, so the guard **has not fired since `b335aca` on 2026-08-30**, where it
succeeded. Two days of a gate that would fail if it ran. This is the same shape
as D6 — not a red light, no light — inside the guard rail rather than inside a
release.

It is also a hard prerequisite for cycle 2: that cut edits `contracts/**` and
`atman/**`, which **are** in the guard's push paths, so the guard fires on it.
Cutting the watchdog fix first would have produced a second red and looked like
the fix caused it.

**The cut.** One line: `".gitattributes"` added to `first_checkpoint_files`,
which is now eleven paths instead of ten. The invariant is untouched — still
exact set equality, not a relaxation.

**Proof after**, fresh clean clone of the commit, 0 CRLF paths:

    guard rc=0   VERIFIED_READ_ONLY_AUTOMATION_CONTRACT
                 3 automation workflows verified, 1 actions:write grant,
                 0 contents:write grants

Pushed 02:41Z. Runner conclusion in `01-releases.md`.

**Runner conclusion, `4dd5c2d`:** `33708576547` Automation contract guard —
**success**. Gate met.

Two other runs fired on that push and are recorded for honesty: Hourly watchdog
`33708576503` **failure** and Current integrity `33708576554` **failure**. Both
are the pre-existing D9 consumer-probe 404, unchanged by this cut and closed by
the next one. Cutting the boundary fix first was deliberate — see the cycle 1
note — so that the guard was already green when the watchdog fix landed and
could not be blamed for it.

---

## Cycle 2 — 02:43Z — `8bf88da` — the consumer probe reads the directory that is served

D9/D6, the defect I was reassigned for. The hourly watchdog had failed every
hour since 2026-09-01 and had been correct every time.

**Proof before**, clean LF clone at 5484218, each step exactly as the router
runs it, 0 CRLF paths, pointer digest matching `baseline.pointer_sha256`:

    resolve              rc=0  RESOLVED_VERIFIED_LIVE_POINTER
    probe data-pointer   rc=0  VERIFIED_WATCHDOG_PROBE
    probe data-release   rc=0  VERIFIED_WATCHDOG_PROBE, 3 range sentinels
    probe consumer       rc=1  public fetch failed after 4 attempts:
                               .../gridatlas/202608291239-atlas-v9/release-manifest.json
                               HTTPError 404

**What is actually served.** GridAtlas moved its published releases under
`atlas/releases/`. At the new path every digest the contract already names is
byte-exact — measured, not assumed:

    200  atlas/releases/202608291239-atlas-v9/release-manifest.json  7c903a39…  match
    200  atlas/releases/202608291239-atlas-v9/build-manifest.json    889986bc…  match
    200  atlas/releases/202608291239-atlas-v9/index.html             023f758f…  match
    200  …/?repd_ref=16135  returns the release index unchanged

So nothing about what is served changed. Only where the verifier looked.

**The cut**, both files already inside `first_checkpoint_files` so the guard's
boundary is untouched:

- `contracts/202608291507-automation.json` — `public.app_release_prefix:
  "atlas/releases/"` and `public.app_route: "atlas/"`, beside the existing
  `app_root`.
- `atman/202608291507-current-integrity.py` — new `app_release_url(contract,
  release_id)`; three literal concatenations at lines 428, 493 and 535 now call
  it.

**One assertion changed rather than moved, and this is the part worth reading.**
Line 536 was

    require(current.get("live_url") == release_url, "current app live URL mismatch")

Before the migration a release was served *at* the app route, so `live_url` and
the release directory were the same string and this compared one against itself
by accident. They are now distinct, measured off the live pointer:

    current.live_url      https://ventusltd.github.io/gridatlas/atlas/
    current.release_route /gridatlas/atlas/releases/202608300453-atlas-v9/

Naively repointing `release_url` would have left this comparing the app route to
a release directory and failed for a second, unrelated reason. Each is now bound
to what it is, so the pointer must declare the exact directory the verifier then
reads. That is a stronger check than the one it replaces.

**Proof after**, fresh clean clone at 8bf88da, 0 CRLF paths — all four watchdog
steps plus the guard:

    guard                rc=0  VERIFIED_READ_ONLY_AUTOMATION_CONTRACT
    resolve              rc=0  RESOLVED_VERIFIED_LIVE_POINTER
    probe data-pointer   rc=0  VERIFIED_WATCHDOG_PROBE
    probe data-release   rc=0  VERIFIED_WATCHDOG_PROBE
    probe consumer       rc=0  VERIFIED_WATCHDOG_PROBE, release 202608300453-atlas-v9

**Runner conclusion, `8bf88da`** — the gate, one API call:

    33708715190  Hourly watchdog 8bf88da…        success   <- first green since 2026-09-01
    33708715223  Current integrity 8bf88da…      success   <- was failure at 4dd5c2d
    33708715205  Automation contract guard       success
    33708714505  pages build and deployment      success

`Current integrity` recovered without being touched: `command_verify` calls the
same `verify_consumer`, so it had been failing on the identical 404 and nobody
had connected the two. **D9 and D6 are closed on the runner, not on my disk.**
