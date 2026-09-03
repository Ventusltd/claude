# 02 — blocked, and findings handed on rather than cut

## B1 — the gridatlas queue was consumed before I reached it

Items 1 and 2 of my brief (corridor scalar; 44 px `Explore route corridors ▸`)
were shipped by the gridatlas UI lane as `1fb6262` (v9.87) and `8fb95a2` (v9.88)
while I was reading the brief. Both green on the runner at 02:36Z. Nothing to
cut; nothing was cut. I edited no file in `gridatlas`.

## B2 — gridatlas: three dead calendar-day crons, scoped but not cut

Reassigned before cutting. Recording the measurement so it is not re-derived.

    .github/workflows/202608310015-gridatlas-overnight-next-versions.yml
      cron: '30,45 23 30 8 *'
      cron: '*/15 0-7 31 8 *'
    .github/workflows/202608310050-gridatlas-next-version-builders.yml
      cron: '7,37 0-7 31 8 *'

Three schedules pinned to 30–31 August 2026. All have fired for the last time
and cannot fire again until 2027. This is the `no-time-based-gates` cvaa vaccine
and the same class as the `companies` once-a-year cron in D6.

**Both workflows keep `push` and `workflow_dispatch` triggers**, and both fire
in practice — `202608310050 GridAtlas next-version builders` ran on `8fb95a2` at
02:35Z and succeeded — so deleting the `schedule:` blocks removes a trigger that
cannot fire and nothing that works. It is deliberately *not* a candidate for
replacement with a live recurring cron: both workflows commit and push to `main`
and one requests a Pages rebuild, so putting them on a real schedule would add
unattended writes to a repository two agents are cutting in. Removing dead
schedules is safe; adding live ones is a decision for the owner.

Note for whoever takes it: `STATE.md` records `Active workflows: 5` and
`tools/scope/loop.mjs lint` enforces a workflow allowlist, so **remove the
`schedule:` keys, not the files** — deleting a file changes the derived count
and turns a one-line cut into a `STATE.md` regeneration.

## B3 — data-gridatlas: the stale pointer descriptors cannot be corrected tonight

`releases/current.json:13,23` and `state/live-set.json:13,23` still carry the
pre-migration consumer shape:

    "live_url": "https://ventusltd.github.io/gridatlas/202608291239-atlas-v9/"
    "route":    "/gridatlas/202608291239-atlas-v9/"

My brief described the fix as a bound four-file cut including these two. **It is
not safe to make, and the reason is worth recording rather than working
around.** Measured, not reasoned:

1. **They are not load-bearing for the red.** `resolve_state`
   (`atman/202608291507-current-integrity.py:188-197`) binds `release_id`,
   `publication_commit`, `app_pointer_commit`, `release_manifest_sha256`,
   `build_manifest_sha256` and `pointer_sha256` — **not** `live_url` or `route`.
   The consumer probe builds its URLs from the *contract*, not from these files.
   Fixing the probe closed the watchdog with these untouched, which the clean-clone
   run at `8bf88da` shows: all three probes `rc=0`.

2. **Editing them fires a workflow that can never pass again.**
   `.github/workflows/202608291239-verify-live-pointer.yml` triggers on exactly
   these two paths plus itself, and its second step asserts

       test "$(git rev-parse HEAD^)" = "$DATA_RELEASE_COMMIT"   # 32459230…
       git diff --name-only "$DATA_RELEASE_COMMIT" "$GITHUB_SHA" == exactly 3 paths

   It is a one-shot promotion verifier whose parent must be the release commit.
   `HEAD` is now many commits past that, so **any** edit to either pointer file
   wakes a dormant workflow into a permanent red. That is the "honest red
   becomes a different red" outcome the brief warned about, arriving through a
   door the brief did not name.

3. **They are also outside the contract guard's declared boundary.** Neither
   pointer file is in `first_checkpoint_files`, and the guard requires exact set
   equality with the paths changed since the baseline. Editing them without
   declaring them fails the guard I had just turned green.

So the correct sequence is: retire or rewrite `202608291239-verify-live-pointer.yml`
first — it is a fossil of a single promotion and asserts a parent commit that can
never recur — *then* move the two descriptors, `baseline.pointer_sha256`, the
workflow's `POINTER_SHA256` env, and `first_checkpoint_files` in one commit.
That is a decision about retiring a shipped promotion record, not a cut, and it
is not mine to take unilaterally at 02:45 on someone else's authorisation.

**Consequence of leaving it:** two JSON fields describe a URL that 404s. Nothing
reads them. `companies/state/atlas-v9-link-contract.json` (D6) is the copy that
matters, and it is in another repository.

## B4 — data-gridatlas: `202608301931 Layer fidelity` red at 5484218

`33606380156`, failed 2026-09-02T07:59Z. Observed, not investigated — outside
tonight's two cuts. Recorded so it is not mistaken for something either cut
caused.
