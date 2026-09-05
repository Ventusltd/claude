# Session log — 184379c4, night of 2026-09-04 into 2026-09-05

**Filed 202609050257 UTC.** Written so this session can be resumed by anyone —
a person, or the next model — after a usage limit, a dead context window or a
crash. Everything here was verified on the served URL or measured in the
repository, not recalled.

All times UTC. **Vikram's clock is BST, +1**: when he writes `202609050333`
he means **02:33 UTC**. Stamps in this estate are read from `date -u` at commit
time, never typed, so generations read an hour behind his phone. That is
correct, not drift.

Transcript: `C:\Users\vikra\.claude\projects\C--Users-vikra\184379c4-0ce4-49bf-9e89-600d63e68803.jsonl`
Session link: https://claude.ai/code/session_01GHy4YJRM7KeXW5Yp4jr475

---

## 1. How the session started

Vikram asked to continue from the last session by reading the log files. The
previous session, `82e00a22`, had been cut off by the usage limit at
2026-09-04 23:25:05 UTC, one minute after he said *"this is the main session do
it here"*. Its log had been written **into Claude's private memory only** —
a hidden path under `.claude/projects/` — so he could not find it the next
morning:

> "The fucking session limit made me stop now I cannot find the log file, you
> can made a handover kind of doc in it too, look properly"

**That is the rule this directory exists to enforce.** Every handover now lives
in this repository, and `/CARRY-ON.md` at the root always names the newest one.

## 2. What shipped, in order

| UTC | repo | commit | what |
|---|---|---|---|
| 01:25 | claude | `31bc1a2` | the previous session's handover, filed where it can be found |
| 01:31 | claude | `6e85062` | renamed `00-LOG.md`, the entry point `CLAUDE.md` already documents |
| 01:39 | globalgrid2050 | `a4faffc1` | front page shows only what is being built now; old page archived byte-identical at `/historical_builds.html` **at the root**, the only place its 229 relative links keep resolving; the search box wired for the first time; `catalogue-gridatlas-v9.yml` retired with its reasoning in the file |
| 01:45 | globalgrid2050 | `6ecc0dc0` | carried the 15 published-version labels the exact-commit gates require, read out of the archive rather than retyped |
| 02:00 | globalgrid2050 | `1a6445cc` | the spiders link came off the front page on his word: *"dont publish that its random and doesnt make sense"* |
| 02:05 | pipelinenews | `e4f32ae4` | **lane B** — WIDER FLEET, the other-technologies control, returned other technologies |
| 02:16 | pipelinenews | `1b51cf26` | **lane B** — the shared pager named a window it did not move |
| 02:33 | pipelinenews | `347d93fa` | **lane B** — 2,416 of 7,680 records were in statuses no control could select |
| 02:38 | gridatlas | `54438ef` | **v9.117** — attribution out of the map into About, last, small print; About gains an Estate group |
| 02:40 | globalgrid2050 | `799dd36d` | `status.json` + `scripts/build_status.py` publish `/status.html` at intervals |
| 02:44 | gridatlas | `9c1ed59` | **v9.118** — all 44 engine-graph nodes in File, grouped; one copyable command |
| 02:49 | gridatlas | `100d206` | **v9.119** — the command drops `npm install`, because the engine needs none |
| 02:49 | ventus-grid-engine | `30efa2b` | the receiver takes `?focus=<module>` so a menu can link into one piece of maths |
| 02:55 | globalgrid2050 | `9a1cd023` | the thirty Pipeline News releases put back on the front page |
| 02:56 | claude | `60d2a5e` | lane C brief — seven days of git, every chat, the agenda and the flaws |

**Live at filing:** GridAtlas generation `202609050249` (v9.119).

## 3. Repository state at filing

| repo | branch | head |
|---|---|---|
| globalgrid2050 | main | `9a1cd023` |
| gridatlas | **`candidate/promotion-lane`** `3061dfc` | the canonical clone is NOT on main |
| gridatlas worktree `../gridatlas-main-202609050200` | main | `100d206` — **this is where the Atlas work happens** |
| ventus-grid-engine | main | `30efa2b` |
| pipelinenews | main | `6b7890d` |
| claude | main | `60d2a5e` |
| spiders | main | `a0f2231` (untouched tonight) |

A scratch copy of the built Atlas lives **outside OneDrive** at
`C:\Users\vikra\ga117`, with `node_modules` junctioned from the canonical clone.
It exists because the browser gate could not be made to run inside OneDrive;
see §5.

## 4. What he asked for, in his own words

Recorded verbatim so nothing is softened in the retelling. Struck items are done.

- ~~"MAKE THIS THE DEFAUL HOME PAGE ... put all content in an archieve ... make prominent ONLY what we are building right now, call the rest historical builds"~~
- ~~"Push this to about menu https://ventusltd.github.io/spiders/spider_printer_v1/"~~
- ~~"Push this to about menu to in gridatlas and pipeline news [federation map]"~~ — **done in GridAtlas, NOT yet in Pipeline News**
- ~~"move the attribution away from the menus" / "Attribution bar clashes move that to about and in small print at the bottom"~~
- ~~"why are the drop down engines here NOT in the menus of gridatlas and pipelinenews"~~ — **done in GridAtlas, NOT yet in Pipeline News**
- ~~"Why are the mjs files not there?"~~
- ~~"Ensure to publish regular intervals on to globalgrid2050.com homepage"~~ — `/status.html`
- ~~"run another agent that does git tracking ... last 7 days ... what is the agenda and what are the flaws"~~ — lane C running
- **"fix the map button"** — NOT DONE. Never diagnosed.
- **"the scoping menu has nothing it seems"** — measured: Scope holds Radius Search, Radius Area, Poly Zone, Measure. Not empty. His complaint is probably (a) the panel at his viewport or (b) the tools not working. NOT RESOLVED.
- **"the polyzone undergrid doesnt work"** — NOT DONE.
- **"the UI via deeplink into gridatlas can be awkward as the cards get in the way"** — NOT DONE.
- **"test as many REPD deep links as you can"** — a sweep harness is written at `tools/proofs/repd-deep-link-sweep.browser.mjs` but **has never been run**, and its REPD source assumption is wrong: it reads the build manifest, which is not a project list. The corpus is `data/repd_browser_registry_202608290716.json`, 9.3 MB, 11,069 unique refs.
- **"Berwick bank offshore wind farm doesn't complete nearest grid view pipeline news"** — QUEUED, not investigated.
- **"Then spin Ubuntu in virtual environments ... Ubuntu is already installed in powershell"** — NOT DONE.
- **"they should be able to build our entire code offline too just like Linux did git"** — measured for the engine: zero dependencies, no proof opens a socket, `node verify.mjs` runs 133 checks from a clone offline. **Not yet measured for gridatlas or pipelinenews.**

## 5. What was learned the hard way tonight

These are the transferable parts. Each cost real time.

**A `tail` in a pipe hides a running process.** `node proof.mjs | tail -20`
produced zero bytes for twenty minutes and looked like a hang. It was not.
Never pipe a long-running proof through `tail` when you need to see progress.

**An append inside a MutationObserver is a feedback loop.** `adoptLate()` in
`atlas/modules/202609031958-menu-bar.js` runs from a MutationObserver. My first
attribution fix re-appended the node on every pass so a late DOM rebuild could
not float it back above the controls — and that append is itself a mutation,
which re-entered `adoptLate`, which appended again. **It crashed the renderer
outright** under the 393×852 arrival gate. Every DOM write in that function must
settle to a no-op: test `lastElementChild !== node` before moving it, and guard
async work with a synchronous flag, not with DOM it has not yet written.

**The control is what tells you whose bug it is.** The crash was only pinned on
me by running the *previous* generation through the *same* harness, where it
passed and printed a full arrival. Without that, it looked environmental.

**The browser gate will not run inside OneDrive.** Serving the worktree from
`OneDrive/Documents/GitHub/...` stalled or crashed Playwright every time. The
same build copied to `C:\Users\vikra\ga117` passed in about four minutes. Copy
`atlas/`, `data/`, `tools/` and junction `node_modules`.

**A proof written after the code must be falsified against the old bytes.**
Two proofs tonight were written after their fix; both were run against the
pre-change file first and observed failing (9 of 14, and 5 of 8) before being
trusted.

**A check can fail on its own prose.** `!/npm install/.test(composed)` failed
because the comment *explaining* the removal contained the words. Assert the
value, not the file.

**New cartridge generations need a `.gitattributes` line.** `recompose.mjs` does
not add it. Only the substation-intelligence cartridge is exempt — adding one
for sld-sandbox makes a different proof fail.

**Restamp BOTH cartridges together.** Cutting a generation that restamps only
one leaves the other's carried-forward proof asserting the previous composition
identity, and three manifest checks fail.

## 6. Open, and where to pick up

1. **The undone UI list in §4** is the work: map button, poly zone, the cards
   obstructing a deep-link arrival, the Scope complaint, and the REPD deep-link
   sweep (fix its corpus source first).
2. **Pipeline News has none of the menu work.** The engine modules, the Estate
   links and the federation map all went into GridAtlas only. He asked for both.
   The integration snippet is one `<script>` tag; see
   `spiders/species/seer-spider/estate-menu/INTEGRATION.md`, which documents
   exactly where it goes in `globalgrid2050/uk_renewables_pipeline/v9.7/index.html`.
3. **Four exact-commit gates fail by the clock, not by any commit.** V9.5.1,
   V9.6.1, V9.6.2 and V9.7 recompute news scoring and the fixture has aged:
   `recency 10 → 8`, `confidence 91 → 89`, `runner_up_score 91 → 89`. They will
   fail on every push until the clock is frozen for the fixture. V9.3, V9.4 and
   V9.5 went green again once the published-version labels were carried.
   `Verify published versions are reachable` was already red before tonight.
4. **Lane C's report** lands at
   `sessions/202609050125-carry-on-handover/05-LANE-C-agenda-and-flaws.md`.
5. **Licensing is still open and still his.** Four of five core repos carry
   `license: null`. The seed's own §10 is the argument: *"The licence was not
   incidental to that outcome. It was the mechanism."*
6. **The promotion lane is still unmerged** — `candidate/promotion-lane`
   `3061dfc`. Activating it needs a GitHub Environment, a secret and a decision
   about the three legacy workflows that still push main.

## 7. Rules in force

- Proofs read **composed bytes**, never parts.
- Make a proof fail before trusting it.
- Stamps from `date -u` **in the same command as the commit**, never typed.
  Verify with `git log --format=%ct`, not `TZ=UTC` — Windows git ignores it.
- Check `git branch --show-current` before committing. The canonical gridatlas
  clone sits on a candidate branch.
- **Never `git add -A`.** Stage explicit paths; stage and commit in one shell
  call. `git add -A .github/workflows/` swept another lane's file tonight and
  had to be unstaged before the commit.
- Report measurements, never grade them.
- Every tool gets a view he can open on his phone. Prioritise iPhone.
  Playwright's WebKit is installed locally and is a closer proxy to iOS Safari
  than Chromium, but **it is not iOS** — his phone screenshots remain the only
  real iOS evidence.
- Nothing private is published. His correspondence is context, never content.

See [[carry-on-2026-09-05]], [[composed-bytes-not-parts]], [[stamps-and-lanes]],
[[chrome-automation-hidden-tab]], [[graphical-interfaces-not-terminals]].
