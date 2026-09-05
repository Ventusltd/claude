# CARRY ON — start here

**This file never moves and never changes its name.** When a session ends — on a usage
limit, a crash, or a night's work finishing — the handover for it is written under
`sessions/` and named here. To pick up where the last session stopped, open the file this
one points at.

## Read these first, in this order

Two logs of session `184379c4` were written by INDEPENDENT agents, deliberately from
different starting points, and they share only 6 substantial lines out of 586 and 942.
Where they disagree, that disagreement is the finding. Read B first — it starts from git,
which is what actually happened, rather than from the conversation, which is what was
intended.

1. **[logs/SESSION-LOG-B.txt](logs/SESSION-LOG-B.txt)** — 1,299 lines. Git-first. Carries
   the commit ledger, eight measured contradictions of this estate's own written record,
   and the traps.
2. **[logs/SESSION-LOG-A.txt](logs/SESSION-LOG-A.txt)** — 1,049 lines. Conversation-first.
   Every one of the architect's 62 instructions quoted verbatim, in order.
3. **[logs/SESSION-LIVE-LOG.txt](logs/SESSION-LIVE-LOG.txt)** — 1,412 lines, 21 machine
   ticks: repo heads, dirty trees, live HTTP codes and byte counts, long-lived processes.
   Written by `logs/live-log.ps1`, which is re-runnable and should be running again.

**There is no SESSION-LOG-FINAL.txt.** A fourth agent was reconciling the three into one
file and was stopped before it wrote anything. If a single authoritative log is wanted, that
job is unstarted, not half-done.

## The narrative handover

**[sessions/202609050257-session-184379c4/00-LOG.md](sessions/202609050257-session-184379c4/00-LOG.md)**

Session `184379c4`, the night of 2026-09-04 into 2026-09-05. Three GridAtlas generations
shipped (v9.117 → v9.119), three Pipeline News iterations from the second lane, the homepage
replaced and then repaired, the build status published, and a third lane auditing seven days
of git and every chat.

**Read §6 first — what is open and where to pick up.** Then §5, which is what the night cost
to learn.

The session before it:
[sessions/202609050125-carry-on-handover/00-LOG.md](sessions/202609050125-carry-on-handover/00-LOG.md)
— session `82e00a22`, GridAtlas v9.108 → v9.116, the ventus-grid-engine repo, the shared
estate menu, the genome spider and the promotion lane.

## Live now

- Build status, republished at intervals: https://globalgrid2050.com/status.html
- The estate's front page: https://globalgrid2050.com/
- Grid Atlas: https://ventusltd.github.io/gridatlas/atlas/
- The engine graph, which is the map of the estate's mathematics:
  https://ventusltd.github.io/ventus-grid-engine/?graph=engine-graph

## Two things about time

Vikram's clock is **BST, UTC+1**. When he writes `202609050333` he means **02:33 UTC**.
Stamps here are read from `date -u` at commit time and never typed, so generations read an
hour behind his phone. That is correct, not drift.

## Open at the moment this window closed, 2026-09-05 ~12:30 UTC

Written here because it is the first thing a fresh session needs, and because two of these
were reported as done by the previous session and were not.

- **Four working trees are DIRTY with uncommitted fixes**, written by agents that were
  stopped mid-task. `globalgrid2050` (+443/-70 across nine files: the mobile table CSS and
  the receiver fetch moved off the render path), `gridatlas-main-202609050200`
  (`atlas/modules/202609031958-menu-bar.js`, the print and save-image fixes, **not
  recomposed into a cartridge, so it cannot reach the served page as it stands**),
  `testcode`, `pipelinenews`. Land them or discard them; do not assume they are proven.
- **The status page silently does not publish.** `deploy-pages.yml` does not list
  `status.html` or `status.json` in `on.push.paths`, so pushing them triggers no workflow.
  Live serves 19 entries; the committed file has 25. One line of YAML.
- **The MAP button is unreachable on a phone**, and this is NOT a regression: the anchor is
  drawn 828 px off the right of a 389 px viewport. Two rules together cause it, neither
  alone — `styles/v9-3.css` `.tablewrap table{min-width:1280px}` and `styles/v9-6-1.css`
  `.hide-mobile{display:table-cell}` under `@media (max-width:768px)`.
- **The v9.7 page's own MAP ATLAS nav link still points at the retired receiver**, in
  `index.html` line 42 — HTML, which the link gate cannot see because it scans only `.js`
  and `.mjs`.
- **Print produces a blank sheet and Save-an-image always refuses.** Both shipped in v9.121.
  The print CSS collapses the map canvas to 0 px; the image path looks up a window handle
  that does not exist.
- Decisions that are the rights holder's alone: the `LIVE VALIDATED` label on v9.6.2 whose
  MAP button computes nothing; the sizing figure (211.2 / 105.6 / 52.8); whether the kernel
  or `testcode` is the single registry.

## Rule this file exists to enforce

A session log written into Claude's private memory under `.claude/projects/` **is not
findable**. That happened on 2026-09-04: the log was asked for, written, and then could not
be located the next morning. Every handover goes in this repository, and this file names the
newest one.
