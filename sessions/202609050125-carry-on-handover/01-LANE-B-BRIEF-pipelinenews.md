# Lane B brief — Pipeline News, overnight 2026-09-05

You are the second lane. The first lane (this session) holds GridAtlas. Do not
touch `gridatlas/` — we will collide on `atlas/current.json` and `index.html`,
which git cannot merge meaningfully.

Your repository: `C:\Users\vikra\OneDrive\Documents\GitHub\pipelinenews`
(`Ventusltd/pipelinenews`). Published under `Ventusltd/globalgrid2050` at
`/uk_renewables_pipeline/`. The live domain is https://globalgrid2050.com.

## Target

**Ship at least three iterations of Pipeline News by morning (~07:00 UTC).**
Each one stamped, committed, pushed, and verified on the served URL — never on
the working tree.

## Defect 1 — the technology filter leaks, and it is the priority

Vikram, verbatim, 2026-09-05: *"pipelinenews also has loads of bugs such as
other technologies sort also brings up solar"*.

Selecting a technology other than solar still returns solar projects. Find where
the technology filter is applied, and be careful: this estate's characteristic
fault is that a fix lands in a source part and never reaches the composed
cartridge the browser loads. **Prove it against the composed bytes that are
served, not against the part you edited.** Measure the leak before and after —
counts per technology on a named query — and put those numbers in the commit.

Suspect list, from the engine graph at
https://ventusltd.github.io/ventus-grid-engine/?graph=engine-graph :
`sld-sandbox-technology-buckets.js LAYER_ID_FOR_BUCKET` is one of five separate
deep-link/bucket implementations in this estate, and the graph marks several of
them DUPLICATES of each other. If the mapping from a technology name to its
bucket exists in more than one file, they will have drifted, and the leak is
very likely that drift. Report every copy you find, even the ones you do not fix.

## Defect 2 — find the rest

He said "loads of bugs". Drive the live app in Chrome and find them: sort
controls, the RELEVANT filter, the REPD UPDATED header toggle, mobile table
scroll (v9.6 was discontinued for a broken mobile release — check v9.7 has not
regressed the same way), and the international/US/Europe separation that v9.6.2
introduced. Test at 393×852 as well as desktop; the phone path is where this
estate's defects hide.

## Standing facts you must not rediscover the hard way

- **The estate record labels v9.7 CANDIDATE and v9.6.2 LIVE VALIDATED.** v9.7 is
  the link 216 industry readers received. Do not silently promote or demote
  either; if your work changes which one should be current, say so and leave the
  decision to Vikram.
- Stamps come from `date -u +%Y%m%d%H%M` **evaluated in the same command as the
  commit**. Never type a stamp. Verify with `git log --format=%ct`, not `TZ=UTC`
  — Windows git ignores that flag.
- **Never `git add -A` or `git add .`** Stage explicit paths, and stage and
  commit in the same shell call: the index is shared with other lanes.
- `git fetch` immediately before every write. Rebase, never force.
- `python3` is a broken Windows Store stub — use `python`. No `gh` CLI, but
  `bash claude/scripts/gh-api.sh <path>` authenticates at 5000 req/hour.
- A gate that reports success while executing nothing is this estate's most
  common failure. Make a check fail before you trust it passing.
- Report measurements, never grade them. No "STRONG"/"GOOD" verdicts.
- Write to `sessions/202609050125-carry-on-handover/` in the `claude` repo if you
  need to leave findings; that is where this brief lives.

## Report back

When you finish each iteration, report: the stamp, the commit SHA, the live URL
you probed, the HTTP code you got, and the measurement that proves the defect is
gone. If you cannot fix something, say so plainly and leave it named — an
unfixed defect that is written down is worth more than a green light that
measured nothing.
