# Command log — the overnight shift of 2026-09-03/04

**Opened 202609040020** (00:20 BST, 2026-09-03 23:20 UTC).

This file exists so the command survives the session. It is appended every ~30 minutes with a
UTC stamp, and it is written for **a successor who has no memory of any of this** — which,
in this estate, is every session. Read `## RESPAWN` first if you are that successor.

Machine state is not duplicated here. `logs/board.md` carries live generation, CI conclusions,
proof rc, the cartridge ceiling and map-share on a sixty-second loop; `logs/red-board.md`
carries 48 classified red jobs with grounded quotes. This file carries **what was decided and
why**, which is the part no daemon can write.

---

## RESPAWN — start here if the session died

**Your role is CEO / field commander.** The architect's standing instruction, verbatim:
*"ALL YOUR TOKENS MUST BE FOR LEADERSHIP AND SHIPPING INSTRUCTIONS not BUILDING UNLESS YOU SEE
AN AGENT OR CODE OUT OF LINE."* You orchestrate; the lanes build. Codex is CTO and rules on
governance. The local models do the clerical reading. You are not to hand-write cartridges,
cut releases, or edit the homepage unless a lane is out of line.

Read in this order, and nothing else before you act:

1. `CLAUDE.md` — the disciplines, each earned by a failure.
2. `sessions/202609032300-four-lanes-one-night/00-NOTE.md` — the four mistakes of the first
   half of the night and the rules they earned.
3. `sessions/202609032310-coaching/` — an agent grading other agents; it found the ceiling
   gauge lying by a factor of 1,171.
4. `sessions/202609032304-codex-cto-control/` — Codex's rulings and my reply. **This is the
   channel to Codex.** Post there; do not relay through the architect.
5. This file, bottom entry first.
6. `logs/board.md` and `logs/red-board.md` for machine state.

**Then re-verify before you quote anything.** This estate's characteristic failure is a
baseline measured once and quoted thereafter. Live generation, CI conclusions and the ceiling
all move hourly.

### Who owns what, as of the opening entry

| lane | owns | never touches |
|---|---|---|
| **Codex (CTO)** | governance rulings; 30 GridAtlas + 30 PN candidates on `codex/*` branches | `main` |
| **A — Discovery** | old-vs-new A/B in its own Chrome; writes `logs/queue/FINDINGS.md` | any product file |
| **B — Cartridge author** | `pipelinenews/tools/intelligence/cartridges/*` | `releases/`, cutting |
| **C — Cutter** | the ONLY lane that runs `release_builder.py --from ... --cartridge` | globalgrid2050 |
| **Publication** | globalgrid2050 homepage + mirrors, in batches; unjamming `compile_root()` | `pipelinenews/releases/` |
| **Immunisation** | cvaa vaccines + spiders crawls | product repos |
| **Cloud** | GitHub Actions crawls, informational and exit-0 by design | product gates |
| **Autopilot / Runners** | local-model and measurement daemons, zero Claude tokens | any git write verb |

**Interlocks that will cost you a night if you break them:**
- Never `git add -A` in any estate repo. Six lanes share the index. Stage by explicit path and
  commit in the SAME shell call.
- Never write a commit message through an unquoted heredoc. Backticks get executed. Three
  occurrences so far, one of them in the entry documenting the rule. Write the message to a
  file and pass `-F`.
- Never `git clean` in pipelinenews: seven untracked `202609010145` files there are the only
  copy of real work.
- Never amend or force-push a shipped commit. A correction is a new entry.
- `gridatlas/atlas/world/index.html` belongs to another lane.
- `sld-sandbox` has **35 characters** of headroom. Anything larger fails the gate, and the
  answer is never to raise the ceiling.

---

## 202609040020 — opening entry

### Shipped since 21:00 UTC

| | version | what it did | evidence |
|---|---|---|---|
| GridAtlas | v9.96 `202609032213` | layer panel opens closed | phone map 29.3% → 69.7%; one tap restores exactly |
| GridAtlas | v9.97 `202609032222` | deep link dismisses the search that found it | arrival 13.0% → 20.0% |
| GridAtlas | v9.98 `202609032246` | arrival frames by viewport | zoom 12 → 13.83 at 1400 px, unchanged at 393 px |
| GridAtlas | v9.99 `202609032315` | the ceiling gauge tells the truth | printed 40,995 clear at 35 clear — 1,171× overstated |
| Pipeline News | `202609032159` | one summary drives all five surfaces | counter, dataset, 3 gauge numbers, 3 arcs, CSV |
| Pipeline News | `202609032251` | grid proximity for the whole fleet | 3,047 rows / 2 techs → 4,138 / 11 |
| globalgrid2050 | `d5aafef`, `d62d512` | the homepage names what is live | `publication-truth` red → green, twice |

Every one concluded on the runner, not a laptop.

### Decisions I made

- **Discarded a version before pushing it.** I had built a cartridge to fix a MAP route
  returning 404, and the route lives in a module `app.mjs` does not import. Three deep-link
  modules ship in every release; one is imported. Measuring a file is not measuring the
  artefact. Build and cartridge deleted.
- **Kept a red red.** The Pipeline News Pages deploy refuses to publish an additive-cartridge
  release, which is correct. I made it say so by name instead of failing on a schema mismatch
  that named a change which never happened — but I did not make it green, because a step that
  reports success over a release it did not publish is the other half of the disease.
- **Accepted Codex's ruling over my own proposal.** Their classifier fails on missing,
  malformed, ambiguous and unknown classes, and on an additive manifest claiming any
  deployment state other than `not-authorised`. Mine could only say yes or nothing.
- **Refused to manufacture versions.** The architect asked for 30 Pipeline News versions. The
  shelf held 15 applied, 6 drifted, 1 applicable — there were never 30 features waiting. Lane
  C is instructed to wait rather than pad the count. Honest expectation: 12–20 real ones.
- **Handed over the front door.** I was hand-editing the homepage because `compile_root()` has
  been jammed since 30 August by a duplicate href. The publication lane now owns both the
  publishing and the unjamming, because a door that needs a person is a defect, not a duty.

### Open, and blocking

1. **The stylesheet hoist.** 18,148 characters in the cartridge with 35 left; the sibling has
   ~147,000 free; v9.85 already proved the route. Until Codex rules, GridAtlas can ship
   module-carried features and removals and nothing else. **This is the throughput blocker.**
2. **Two gates that have never been green** — pipelinenews Pages (8 of 8 failures) and
   globalgrid2050 `V9.7 Exact Commit Validation` (10 of 10, a committed `input_sha256` that no
   longer matches a rebuild). A genuine new break in either is invisible today.
3. **`cancelled` is counted as nothing** by the CI reader, so globalgrid2050 shows 10
   workflows and accounts for 9. Harmless only while V9.7 is red anyway.

### Measured, so nobody re-derives it

- GPU: **19% mean at 13.4 W** before the autopilot started — bursts of real work separated by
  nothing queued. After: 86.4% mean, 94% median, 97 tok/s, 72 °C, 38–106 W.
- Memory: `FreePhysicalMemory` read 0.82 GB while `\Memory\Available MBytes` read **6,555 MB**
  minutes apart on the same machine. Both look like alarms; only the second decides whether an
  allocation succeeds. The real leak is orphaned `llama-server` processes breeding behind dead
  parents — four in one evening. Parentage is the only test.
- Local model: 42 of 44 red-job classifications grounded, **2 rejected as inventions**, and the
  rejections were the predicted class — two real log lines spliced into one command that was
  never run.
