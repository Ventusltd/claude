# claude

The working record of Claude Code sessions on the GlobalGrid2050 estate.

This repository holds what a session **learned**, not what it built. The builds live in
their own repositories and are the deliverable. What is kept here is the part that is
otherwise lost when a session ends: the measurements, the defects found and how they were
found, the theories that turned out to be wrong, and the scripts that can reproduce any of it.

A session has no memory. This repository is the memory.

## Why it exists

Across one session on 2 September 2026 the following were established, and none of them
existed in writing anywhere before that session ended:

- PipelineNews had refused **25 consecutive Pages deploys** and the live site was five days
  behind `main`. The cause was a gate that requires the live-pointer commit to *be* HEAD,
  combined with a push trigger that fires on the paths where daily work lands.
- The GridAtlas substation name join binds **69 sites across 34 colliding keys** to whichever
  record loaded first, because the normaliser strips the exact words that distinguish them.
- **43%** of NESO connection points carry no coordinates, so every "nearest substation" claim
  is nearest-among-57%.
- The site-wide transformer count is **1.90x** overstated across 92% of sites, because winding
  ends are counted rather than records.
- Road routing between substations **fails** against published cable lengths, and is beaten by
  a single multiplier. A six-month feature was cancelled on one afternoon of measurement.

Each of those is a defect or a decision that would otherwise have to be rediscovered.

## Layout

```
sessions/<YYYYMMDDHHMM>-<slug>/
    00-LOG.md            the full narrative record, in order, including what was wrong
    01-findings.md       every defect, with its evidence and reproduction
    02-measurements.md   every number, with the command that produced it
    03-provenance.md     how the NESO chain was verified, end to end
    04-licensing.md      pandapower, BSD-3, and the attribution stack
    05-corridor-study.md the routing feasibility gate and why it failed
    scripts/             every script written, runnable
    data/                every measurement output, as JSON
    artifacts/           published pages, as shipped
```

## Rules for anything written here

1. **Measurements, not impressions.** Every number carries the command that produced it.
2. **Record the wrong turns.** A theory that was disproven is worth more than one that was
   never tested, because it stops the next session re-running it. The disproven ones are
   marked `WRONG` in the log and left in place.
3. **Nothing is graded.** Findings are reported, not scored. The estate's own
   `not_a_connection_assessment` discipline applies here too.
4. **Scripts must run.** If a script needs data that is not here, it says where the data is.
5. **Nothing is amended.** A later session adds a new dated directory; it does not rewrite
   an earlier one. A correction is a new entry that names what it corrects.

## Sessions

| date | session | what it established |
|---|---|---|
| 2026-09-02/03 | [`202609021835-estate-and-corridor`](sessions/202609021835-estate-and-corridor/) | Estate-wide CI/CD scan; four Atlas defects; datapoint and LOC census; NESO provenance verified to the cell; routing gate run and failed |
