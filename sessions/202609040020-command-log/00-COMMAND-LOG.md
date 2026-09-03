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

---

## 202609040035 — shipped on instruction, session closing

The architect called stop-and-ship with the laptop about to go off. Everything that had been
reviewed was pushed rather than left committed-and-held, because held work on a machine that
is about to be switched off is work that may not survive.

### Pushed in this entry

| repo | sha | what |
|---|---|---|
| pipelinenews | `face863` | release `202609032329` — a dash stops claiming a search that never ran |
| pipelinenews | `5f9b4c4` | cartridge `unnamed-is-not-unspoken` — the SUB hover says the layer has no name, and invents none |
| pipelinenews | `0bc5efd` | seventh SPENT note: `wider-fleet-proximity` is the one that fails OPEN |
| globalgrid2050 | `5efdc5ef` | the catalogue compiler identifies the row it governs, so it can refresh it again |
| globalgrid2050 | `5c700a4a` | the homepage names the Grid Atlas actually being served — v9.99 |
| globalgrid2050 | `ea97bf09` | Pipeline News `202609032329` published — **29 snapshots, all reachable** |

`PUBLICATION TRUTH: PASS`. GridAtlas live at `202609032315` (v9.99), homepage 200.

### The three findings that outlive the night

1. **The compiler did not merely refuse — it corrupts.** Pointed at what
   `catalogue-gridatlas-v9.yml` actually feeds it, `compile_root()` returned `changed=True`
   and inserted a SECOND stale row after the V8 sentinel. It has never happened only because
   the workflow dies earlier, on a `cmp` of two files that differ at char 2 of line 1. **A
   latent corruption behind a broken gate is the worst shape in this estate**: the day
   somebody fixes the gate, the corruption ships. Now refused, and the governed row is
   identified structurally by the `GRIDATLAS_V9_AUTOMATION` markers — a narrowing, not a
   loosening.
2. **The href occurs THREE times, not two.** The `os-strip` banner, the governed row, and the
   immutable `.../atlas/releases/202608291239-atlas-v9/` row which contains the composition
   URL as a prefix. Every account of this jam — `CLAUDE.md`, and mine twice tonight — said
   twice. Href-counting was never salvageable. **That correction belongs in `CLAUDE.md`.**
3. **A dash asserted a search that never ran, on 4,633 rows, and was true of none of them.**
   The payload's own coverage block reads `with_circuit 3047, no_circuit 0`. Zero projects
   were measured and found nothing. The two silences — never searched (4,605) and cannot be
   searched (28) — are now separate on screen.

### Open at close, in priority order

1. **The seam we opened ourselves.** `grid-proximity.json` is 4,138 rows; `grid-distance.json`
   and `substation-33kv.json` are 3,047. `grid-distance.json` says of itself: *"carried
   across, not recomputed, so the two can never disagree."* They now disagree by 1,091. A
   payload asserting an invariant that is false is worse than one that is incomplete, and this
   is a regression from tonight's own widening. **Next version.**
2. **The Markinch contradiction.** A lane reported REPD 155 absent from the Pipeline News cut
   entirely — but the architect reached it *from* Pipeline News, and a product cannot emit a
   MAP link for a row it does not hold. Three candidates given to that lane: `repd_ref` typed
   as int in one payload and string in another (`Counter[400]` and `Counter[400.0]` are the
   same key and have produced a false defect here before); the row living in
   `wider-fleet.json` rather than the spine; or REPD 155 being one of the **nine biomass
   projects of 823 that the widening did not reach**. Unresolved.
3. **The stylesheet hoist**, authorised with five acceptance conditions. 35 characters left.
4. **The `--applicable` fix**, authorised, must handle all three traps or not ship.
5. **Two gates that have never been green** — pipelinenews Pages, and globalgrid2050 `V9.7`.

### For the successor

Everything above is pushed. Nothing is held. The lanes were mid-flight when the machine went
down, so assume any agent's unfinished work is lost and re-read the repos rather than the
plan. The reading order in `## RESPAWN` still stands.

---

## 202609040040 — a correction and a data defect, recorded at the buzzer

**The Markinch "not in the cut" finding was WRONG and is withdrawn.** Markinch is in the cut
and **fully measured**: `ref 155 · RWE · biomass · 65.0 MW · Fife · operational`, circuit
**2.47 km at 275 kV**, substation **2.486 km — Glenrothes Substation (SP Energy Networks,
275/33 kV)**. The data is complete and correct.

The lane's own account of how it got there is the transferable part, and it is two instruments
failing the same way:

- `wider-fleet.json` is a bare list of 1,104 dicts, not a dict. The first probe threw
  `AttributeError: 'list' object has no attribute 'items'` and **a thrown probe was allowed to
  count as an answer**.
- Every file was searched for `repd_ref`. **`wider-fleet` and `grid-proximity` key it `ref`.**
  So the grid-proximity check queried a key that does not exist there and returned False for
  all 4,138 rows — a dead instrument reporting a clean negative.

**So the Markinch defect is client-side, timing or Atlas-side, exactly as first suspected, and
nothing on the Pipeline News data side excuses it.** That correction must reach the discovery
lane before it chases a phantom.

### The data defect found on the way, and it is real

Reconciling the widening's 1,091 added rows:

```
wider-fleet          1,104
  no ref                13  →  12 dropped, 1 CARRIED as ref: ""
  ref present        1,091  →  1,090 carried, 1 DROPPED (13263 Rassau)
carried total                   1,091
```

**Two errors that cancel exactly, which is why the total looked right.** One legitimate
ref-bearing project was dropped and one identity-less row was added.

- The added row is `ref: ""` — *BOC Limited, Wholeflats Road, Green Hydrogen Electrolyser
  Plant*, 200 MW — carrying a real proximity measurement **under an empty identity that can
  never be joined back to any project**. Twelve of its thirteen ref-less siblings were
  correctly dropped; this one was not.
- The dropped one, `13263 Rassau Industrial Estate`, has a ref AND a coordinate. Its name
  contains an **embedded newline**, and `widen_spine.py` reshapes rows into a 40-column TSV
  contract where an embedded newline splits one record into two. **Hypothesis, not result** —
  the lane did not run the widening. It belongs to whoever owns `widen_spine.py`.

Capacity was tested and killed as an explanation: 119 of the 120 ref-bearing zero-capacity
rows were carried.

### The rule this earned

> **A zero result is not a finding until the probe has been shown to return non-zero on a
> known-present case.** Both of tonight's instrument failures were a probe that could only
> ever return nothing, reported as evidence that there was nothing.

That is the same shape as the estate's existing rule — *a sweep that returns the same answer
for every subject is a broken instrument* — one level down, and it now has a positive control
attached: Markinch.
