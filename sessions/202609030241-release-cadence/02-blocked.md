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

## B5 — data-gridatlas: the layer-fidelity harness cut, specified but not made

Reproduced in full (Playwright 1.62.1, headless Chromium, `live.mjs` verbatim,
60 layers, 0 console errors, 26 FAIL). Working in `00-LOG.md`. The cut has two
parts and both are in `.github/workflows/202608301931-layer-fidelity.yml`,
which is inside `first_checkpoint_files` and therefore mine to change:

1. **The terminal-state regex does not match seventeen of the sixty layers.**
   `/\[(OK|EMPTY|FAIL)\]/` never matches a statistics label such as
   `Solar PV [2819 | 52.3GW]` or
   `Major Industrial Sites [2458 | 102,956,634 tCO₂e]`. Those layers all report
   `loaded=true` with real feature counts; the harness waits the full 60 s on
   each and then fails them. Seventeen minutes of a forty-minute job.
2. **The 400 MB heap budget is judged per layer and measured per session.**
   `Runtime.getHeapUsage()` is process-wide. It crosses 400 MB at row 40
   (`trunk_roads`, 18,398 features) and never returns below ~309 MB, so every
   later layer inherits the verdict. `motorway_services` — 1,574 features,
   0.5 s — is recorded at 513 MB. Four rows fail on nothing else.

**Not made because the lane moved to gridatlas mid-cycle**, and because the
correct fix is a redesign of someone's gate rather than a repair: a per-layer
heap delta plus a separately named session ceiling, and a terminal condition
the app actually reaches. Lowering the threshold to go green would be exactly
the move the estate forbids, so it is written down instead of guessed at.

Note for whoever takes it: the `offline` job passes completely, so the
repository's own V8-origin fidelity is verified today. Splitting the two jobs
would surface that — but it would also hide a live red, so it is a decision.

## B6 — cvaa: two vaccines on gridatlas are passing on commit-subject coincidence

Not a gridatlas defect and not fixable there. Recorded because a green light
that means nothing is worse than the red it replaced, and because I caused one
of them.

`attestation-freshness` decides freshness by comparing the positions of two
commits found by regex over commit **subjects**:

    const last = commits.find(c => /live|verif|accept/i.test(c.subject));
    const pointerCommit = commits.find(c => /scope|cartridge|compos|promote/i.test(c.subject));
    if (last && pointerCommit && commits.indexOf(last) > commits.indexOf(pointerCommit)) …

A single commit whose subject contains both — *"the live verifier expects the
composition this repository declares"* — is found by both `find` calls, giving
`0 > 0`, which is false, which is immune. Measured: gridatlas flipped FAIL →
immune at `1762170`, before the verifier was touched.

`rollback-exercised` has the same shape and has been passing on a false
positive since 2026-09-01: the only matching subject is `32bc3bb`, *"carry
Codex's assembler boundary — staged, exclusive, and owned rollback"*, which is
not a drill.

**Meanwhile the underlying facts are unchanged:**
`state/live-set.json` still carries `verified_at 2026-08-30T04:07:46Z`, and no
rollback has ever been exercised.

The cure is in the antibodies. A subject line is not an event. Freshness should
compare the attestation's own recorded timestamp or digest against the pointer
it covers — both are in the file — and a drill should be recognised by an
artefact it leaves behind, not by a word in a sentence a human chose.

I did not raise, relax or work around either vaccine, and neither green is
claimed as an outcome of my cuts.

## B7 — the rollback drill: runnable procedure, not run here

`rollback-exists` is closed on evidence. `rollback-exercised` needs a real
drill, and I stopped short of it for three reasons, in order of weight:

1. It takes another lane's shipped work off the live site. Rolling back to
   v9.87 removes the 44 px action the gridatlas UI lane shipped at 02:34Z from
   the live map for the duration. That lane did not ask for it.
2. **`workflow_dispatch` is unreachable from here** — no `gh` CLI, no token.
   Running `tools/rollback.mjs` locally and pushing would exercise the tool but
   not the workflow, and the workflow carries the confirmation and the gates.
3. Doing it by hand and recording it as a drill of the automated path is the
   "merely appear to" failure, in the one place it matters most.

**The procedure, for whoever holds the token.** It is symmetric, and that is
the point: after a rollback lands, the generation it replaced is an ancestor of
the new one, so rolling forward again uses the same tool and the same guards —
there is no second mechanism to test.

    1. confirm the UI lane is idle: git fetch, HEAD unchanged for one cadence
    2. dispatch  rollback-composition.yml
                 to_generation = 202609030233      (v9.87, one back)
                 reason        = "rollback drill; nothing is wrong with v9.88"
                 confirm       = ROLL BACK
    3. gate      the cartridge proof on the pushed commit must be success
    4. verify    https://ventusltd.github.io/gridatlas/atlas/current.json
                 generation == the new stamp, composition_version == v9.87
    5. dispatch  rollback-composition.yml again
                 to_generation = 202609030234      (v9.88, now an ancestor)
                 reason        = "rollback drill complete; restoring v9.88"
                 confirm       = ROLL BACK
    6. gate + verify as above; composition_version back to v9.88

Ends where it started, with three new generations and a path that has been
used. Expect `atlas/current.json`, `atlas/state/live-set.json`, one new
`atlas/manifests/<stamp>-composition.json` and `STATE.md` to change and nothing
else — the workflow enforces exactly that allowlist and fails if anything else
moves.

## B8 — cvaa `loop-exists` demands exactly what gridatlas's own lint forbids

Not a cut in either repository. A disagreement, and it needs an owner.

cvaa `202608301704-loop-exists.md`:

    loops.filter(w => !/schedule:/.test(w.text))
      .map(w => `${w.file} has no schedule; the loop is not perpetual`)

gridatlas `tools/scope/loop.mjs:113-115`:

    if (master.data.status === 'done') {
      invariant(loopWorkflow.includes('scope-loop-mode: retired'), …);
      invariant(!/^\s*schedule:/m.test(loopWorkflow), 'retired scope loop must not retain a schedule');
    }

`STATE.md` records `Master: done`. So gridatlas's gate **fails the build** if
`202608301321-scope-loop.yml` carries a schedule, and cvaa **reports a finding**
if it does not. There is no state of that file that satisfies both.

The vaccine's own Symptom section names this exact situation — *"gridatlas scope
6 removed the schedule; scope-loop now runs only on manual dispatch"* — so cvaa
knows about the retirement and considers it the disease. gridatlas considers a
closed scope-of-works a reason to retire the loop. Both positions are coherent;
they cannot both hold.

**Deliberately not resolved by me.** Either answer changes a rule rather than a
file: relax cvaa to accept a retired loop when the master is closed, or reopen
gridatlas's loop and change what `done` means. And it is trivially gameable in
the wrong direction — the antibody matches `schedule:` anywhere in the text,
including in a comment, so gridatlas could go green by writing the word. That
would be gaming it, and I have not.

## B9 — cvaa: three antibodies decide from text they have not parsed, and I tripped all three

One finding, three instances, all measured tonight. Grouped because the cure is
the same shape.

| antibody | reads | what tripped it |
|---|---|---|
| `attestation-freshness` | commit **subjects** by regex | one subject containing both "verif" and "compos" flipped it FAIL → immune with the file untouched (B6) |
| `rollback-exercised` | commit **subjects** by regex | `32bc3bb`, a commit about an assembler boundary that happens to contain the word "rollback", has passed it since 2026-09-01 (B6) |
| `no-time-based-gates` | raw workflow **text** | quoting a *removed* cron in the comment that replaced it kept the finding standing; fixed in `a9247f1` by keeping the record and dropping the shape |
| `full-history-checkout` | raw workflow **text**, gated on `/cvaa\|inoculate/i` | writing the word "cvaa" in a comment in `202608312212-cartridge-proof.yml` brought that workflow into scope and produced *"runs cvaa with 2 checkout(s) lacking fetch-depth: 0"* — that workflow does not run cvaa |

The last one is the sharpest, because the sentence it produces is **false**. The
cartridge proof's checkouts are shallow, deliberately — its own header says
*"node, no browser, no history"* and nothing in it reads the past. It became
in-scope because of a word in a comment about the vaccine that reported it.

So in one night, three of these produced a verdict that had nothing to do with
the state of the repository: two false greens and one false red, all from text
matching. **The failure mode is symmetric and that is what makes it dangerous** —
it is not conservative in either direction, so neither a red nor a green from
these three can be taken at face value.

The cure is in the antibodies. Parse the workflow and read `on.schedule`, not
the file text. Recognise a drill by an artefact it left, not by a word someone
chose. Compare an attestation's own recorded timestamp against the pointer it
covers — both are already in `state/live-set.json` — rather than the ordering of
two regex hits over commit subjects.

Until then, every green from these four should be treated as unmeasured.

## B5 — UPDATE, and the conclusion is reversed: this is not a cut

I built the fix, ran it three times against the live surface, and **it must not
ship.** The reason is worth more than the fix would have been.

### What the harness actually gets wrong

The original judges each layer on its label, a 400 MB heap ceiling, and a
feature count. All three are session state wearing a per-layer label:

- **The label.** 17 of 60 layers end in a statistic — `Solar PV [2819 | 52.3GW]`
  — not a status marker, so `/\[(OK|EMPTY|FAIL)\]/` never matches and each burns
  its full 60 s timeout. **1,049 s of a 40-minute job.**
- **The heap.** `Runtime.getHeapUsage()` is process-wide and monotone. It
  crosses 400 MB at `trunk_roads` and never returns, so `motorway_services` —
  1,574 features, 0.5 s — is recorded at 513 MB.
- **The features.** `querySourceFeatures` returns what is in the loaded tiles.
  **`src-repd` is shared by 16 layers and `src-metros` by three**, so `tram`
  reports 0 only because `dlr` and `metro` were unchecked before it was reached.

### The real bug, which I did find

    if (state.sourceId && state.label.includes('[OK]')) {
      await page.waitForFunction(sourceId => map?.isSourceLoaded(sourceId) === true, …)
    }

**The explicit wait for the source to load is gated on `[OK]`.** The 17
statistic layers never enter it; in the original they get 60 s of *accidental*
waiting from the settle timeout instead. Fixing the settle predicate without
also making that wait unconditional removes the accident and leaves nothing.

Measured exactly that way, three versions against the same live surface:

    v1  original                          26 failures   1,049 s
    v2  settle predicate fixed             9 failures      34 s   <- 21 of 60
                                                                     verdicts
                                                                     changed
    v3  + unconditional source-load wait   4 failures      ~40 s

### Why it still must not ship

**v3 run twice, minutes apart, same commit, same live surface:**

    run A   4 layer failures   empty sources: 11kv, 132, 275, air, subs
    run B   2 layer failures   empty sources: 11kv, 132, 66
    verdict disagreements between the two runs: 4  (66, subs, tram, wind)

A gate that returns a different answer each time it runs is not a gate, and
tightening its predicates does not fix that — it moves the flake around. The
cause is structural: **per-layer verdicts cannot be deterministic while sixteen
layers share one source whose load state is racing the previous layer's
uncheck.** A correct design groups layers by source and measures once per
source; that is a redesign for the owner to choose, not a repair I should make
unilaterally in another lane's gate at 03:45.

Shipping v3 would have replaced 26 wrong failures with 2-4 different wrong
failures and looked like progress. That is the trap this session was warned
about, arriving from the direction of a genuine improvement.

### What IS stable across all four runs, and worth taking

    console errors                     0, every run
    src-11kv and src-132               no features in ANY run
    settle-predicate fix               1,049 s -> ~35 s, no downside when the
                                       source wait is made unconditional

So there are two real signals under the noise: the page throws nothing, and two
sources never produce a feature under any camera or toggle order. Both are
currently invisible because 26 meaningless per-layer failures are printed over
them.

**Recommended, in this order:** (1) make the source-load wait unconditional and
fix the settle predicate — that alone returns thirty-five minutes a day and is
not contentious; (2) move the verdict from per layer to per source; (3) keep the
400 MB ceiling as a named session observation rather than a per-layer test;
(4) assert `console_errors === 0`, which the harness already collects and does
not check.
