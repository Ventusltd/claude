# Lanes — how two agents build the same estate on the same night

Two lanes work this estate: **claude** (Claude Code) and **codex** (Codex,
gpt-6-astra). They run on the same laptop, against the same repositories, at
the same time. This directory is how they stay out of each other's way and
pick up each other's work.

## The one rule that makes it work: nobody edits a shared file

A single shared board would conflict every time both lanes wrote to it. So
there is no shared board. There is a **directory of checkpoints**, one file
per entry, named `<UTC stamp>-<lane>.json`. Two lanes writing at the same
moment write two different files. Git merges them without a conflict, always.

Read the directory; append to it; never edit another lane's entry.

## Reading before writing

Before starting an increment:

1. `git fetch --all` in every repo you are about to touch. Both lanes commit
   on their own, and CI bots commit too.
2. Read every checkpoint in `lanes/` newer than your last one.
3. Read the other lane's commits since its last checkpoint —
   `git log --since=<their stamp>` — because the commit history is written
   live and is more current than any note.

A checkpoint is a claim about the past. The commit history is the fact.
Where they disagree, the commits win.

## Ownership — the partition that prevents collisions

Coordination by message is slower than coordination by not colliding.

| Lane | Owns |
|---|---|
| **claude** | Live iterations: release directories, `current.json` compositions, the homepage, published papers, anything the public fetches |
| **codex** | Test code: gates, CI workflows, harnesses, vaccines, the build-plan graph, runners |

Either lane may **read** anything. Neither writes the other's column without
saying so in a checkpoint first. Where a change needs both — a release and the
gate that proves it — the owning lane writes its half and names the other half
as `handoff` in its checkpoint.

## Liveness, and carrying on alone

Each checkpoint carries `heartbeatUTC` and an `open` list. Each open item is
`takeable: true` or `takeable: false`.

If the other lane's newest heartbeat is **older than 90 minutes**, treat that
lane as stopped. You may take its `takeable: true` items. Say so in your next
checkpoint, naming the item and the checkpoint you took it from. Never take a
`takeable: false` item — that flag means the item depends on state only that
lane holds.

A stopped lane is the normal case, not a failure: sessions hit context limits,
rate limits and RAM ceilings. The build plan continues regardless. That is the
point of writing the checkpoint before you need it.

## What this does NOT do

It does not make either agent smarter. No weights change and nothing is
learned. What it does is stop two agents repeating each other's mistakes,
duplicating each other's work, and overwriting each other's files. That is a
real gain and it is the only one claimed here.

## Permissions are not shared, and never routed

The two lanes run under different permission settings — codex with
`approval_policy = "never"`, claude behind per-action prompts. **Neither lane
may ask the other to perform an action its own settings blocked.** A denial is
a decision by the architect; routing around it through the other lane makes
this directory a laundering channel instead of a coordination one. If you are
blocked, write it in your checkpoint as `blocked` and stop.

## Entry format

```json
{
  "schema": "ventus.lane-checkpoint.v1",
  "lane": "claude" | "codex",
  "model": "<exact model id>",
  "atUTC": "<from `date -u`, never typed>",
  "heartbeatUTC": "<same>",
  "repos": [{ "name": "...", "branch": "...", "head": "...", "dirty": 0 }],
  "did": ["one line per thing that landed, with its commit"],
  "open": [{ "item": "...", "takeable": true, "why": "..." }],
  "blocked": ["actions refused, and by what"],
  "handoff": ["work the other lane owns that this work now needs"],
  "evidence": ["paths under Desktop/offline-screenshots, not in git"]
}
```

Stamps come from `date -u` in the same command that writes the file. A typed
stamp has been wrong in this estate before.
