# CARRY ON — start here

**This file never moves and never changes its name.** When a session ends — on a usage
limit, a crash, or a night's work finishing — the handover for it is written under
`sessions/` and named here. To pick up where the last session stopped, open the file this
one points at.

## Read these first, in this order

**Start with the Astra review.** It is the newest document, it is the only one that
re-measured the live pages rather than reading the record, and it CORRECTS the other three
in several places. Where it disagrees with anything below, it wins.

1. **[logs/ASTRA-ISSUE-REVIEW-20260905.txt](logs/ASTRA-ISSUE-REVIEW-20260905.txt)** — 379
   lines, an independent Codex/Astra review written 11:31-11:38Z on 2026-09-05 against local
   source AND the deployed pages. 30 findings, each tagged RUNTIME / SOURCE / HISTORICAL /
   OPEN REQUEST so a reproduction is never confused with an inference. Its verdict:
   *the principal reported user-facing failures remain deployed.* Its evidence directory is
   OUTSIDE this repo at `C:\Users\vikra\astra-issue-review-20260905` and is NOT backed up.

Then the two independent session logs. They were written by separate agents from
deliberately different starting points and share only 6 substantial lines out of 586 and
942. Where they disagree, that disagreement is the finding.

2. **[logs/SESSION-LOG-B.txt](logs/SESSION-LOG-B.txt)** — 1,299 lines. Git-first: the
   commit ledger, eight measured contradictions of this estate's written record, the traps.
3. **[logs/SESSION-LOG-A.txt](logs/SESSION-LOG-A.txt)** — 1,049 lines. Conversation-first:
   every one of the architect's 62 instructions quoted verbatim, in order.
4. **[logs/SESSION-LIVE-LOG.txt](logs/SESSION-LIVE-LOG.txt)** — 1,412 lines, 21 machine
   ticks: repo heads, dirty trees, live HTTP codes and byte counts, long-lived processes.
   Written by `logs/live-log.ps1`, which is re-runnable and should be running again.

**There is no SESSION-LOG-FINAL.txt.** A fourth agent was reconciling the three into one
file and was stopped before it wrote anything. If a single authoritative log is wanted, that
job is unstarted, not half-done.

### What the Astra review corrects in A, B and the session narrative

Do not carry these numbers forward; they were restated confidently and are wrong.

```
MAP off-screen      measured x=1156.17, w=37.06, h=21 at viewport 393 (763 px past the
                    edge). NOT the 828 px figure - that was a different filtered row.
Search vanishing    visible 2,272 ms, hidden 3,020 ms in that run, and the timing moves
                    with load. NOT a fixed 450/950 ms deadline. The transition is the
                    evidence; the clock is not.
"10 MB downloaded"  10,043,874 bytes is DECODED JSON. On the wire it is ~1.18 MB
                    compressed. The parse and DOM cost is real; the transfer claim is not.
323,801 "DOM nodes" that is querySelectorAll('*') - ELEMENTS. Total nodes is a different,
                    larger number.
cache:no-store      bypasses the HTTP cache. It does NOT force a fresh DNS/TCP/TLS
                    handshake on every visit; connections may be reused.
The MAP race        does not explain the off-screen button. Valid hrefs and an
                    unreachable target coexist. The geometry is the defect.
```

### Five findings that are NEW in the Astra review and appear in no other log

```
13  run.mjs offlineFailures omits `absent`. A MISSING required offline gate lets the
    network gate run and the process exit 0. Demonstrated with a fixture.
16  The export outcome proof written last night has its own driver faults: it clicks
    Save without opening File, then looks for the button by its OLD text after the
    click changed it. Its failures are the driver's, not the app's. Do not trust it.
17  browser_map_reachability_v9_7.mjs hardcodes exactly 7,680 rendered rows and allows
    60 s for them - it would REJECT correct pagination. Its 120 s route timer can
    outlive the browser.
20  The CVAA engines.json claim that selftest crashes on a path is FALSE. It runs to
    completion, exits 1, and names three real problems instead.
30  The candidate receiver's failure semantics contradict its own comment: schema-valid
    JSON with an unsupported schema REMOVES the route and still returns verified:true.
```

4. **[logs/ASTRA-ISSUE-REVIEW-20260905.txt](logs/ASTRA-ISSUE-REVIEW-20260905.txt)** — an
   agent's review of the reported user-facing failures against local source AND the deployed
   pages. Closest thing to a verdict that exists. Its own summary: *the principal reported
   user-facing failures remain deployed.*

## Open work — uncommitted, in OTHER repos, written by agents that were stopped

Both fixes below exist only as dirty working trees. Neither is committed, neither is
deployed, and neither has a proof that was made to fail first. Check them before writing
anything new over the same files.

```
globalgrid2050                          (11 dirty)
  uk_renewables_pipeline/v9.7/index.html
  .../scripts/core/atlas-receiver-v9-7.js
  .../scripts/plugins/projects-v9-5-1.js
  .../styles/v9-3.css  .../styles/v9-6-1.css
  .../tests/{browser_smoke_v9_7,check_v9_5_1}.mjs  .../tests/run_v9_7.sh
  ?? .../tests/browser_map_reachability_v9_7.mjs
  ?? scripts/test_catalogue_gridatlas_v9.py
      -> the mobile MAP fix. Unfinished.

gridatlas-main-202609050200             (2 dirty; a WORKTREE of gridatlas/)
  atlas/modules/202609031958-menu-bar.js
  ?? tools/proofs/export-print-and-image-outcomes.browser.mjs
      -> the blank-print and dead-save fix. NOT RECOMPOSED, so as it stands it
         cannot reach the served cartridge even if committed.
```

## Four checks that should become CI, not agent work

Each one is a finding from this session that currently lives only in prose, and will decay:

```
live status.json  ==  committed status.json     (would have caught the silent non-deploy;
                                                 deploy-pages.yml omits status.html and
                                                 status.json from on.push.paths - 1 line)
grep the SERVED HTML, not only .js/.mjs, for retired receivers   (index.html:42)
git status --porcelain empty after any agent is stopped
commit stamp == commit time within 5 min, compared in UTC via %cI
a required gate reported `absent` must exit nonzero, not fall through   (Astra 13)
```

Confirmed real drift, not a timezone artefact: `c1b24e6d` is stamped `202609050415` and was
committed at `09:36:49Z` — 5 h 21 min out.

Note on the last one: `git log --format=%cd` prints LOCAL time (BST, +01:00 here). Comparing
that to a UTC stamp manufactures a false 60-minute drift. Re-measure with `%cI` before
quoting the "73 commits drift" figure from Log B; the large outliers are real, the count
is not yet trustworthy.

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
