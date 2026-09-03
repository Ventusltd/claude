# Overnight, PipelineNews lane

Started 2026-09-03 01:13 UTC. No conversational memory. Everything below was
re-derived tonight from `Ventusltd/pipelinenews` at `origin/main` = `47a99b0`.

A second agent is in `gridatlas` and its session directory
(`sessions/202609030103-overnight-phase0/`) was already on disk uncommitted
when I arrived. I have not touched it, and every commit I make to this
repository names only my own directory.

---

## 1. Task 1, the jammed deploy: F1's diagnosis is not the operative cause

F1 says the Pages gate fails because
`validate_live_pointer()` requires the pointer commit to **be** HEAD. That line
is real and it does fail — but it is **not** the first thing that fails on the
path the workflow actually takes, and removing it does not unjam anything.

I reproduced against a clean `--shared` clone of `gh/main` exactly as the brief
specified. Three independent gates block the deploy, in this order.

### Blocker 1 — 30 of 32 releases carry a schema no validator knows

`.github/workflows/202608301214-pages-v2.yml` chooses the
`--timestamp-folder-release` argument by looking at what the pushed commit
changed:

```
mapfile -t changed < <(git diff-tree ... "$GITHUB_SHA" \
   | sed -nE 's#^releases/([0-9]{12}-pipelinenews)/.*#\1#p' | sort -u)
if test "${#changed[@]}" = 1; then release="${changed[0]}"
```

At HEAD that resolves to `202609030009-pipelinenews`, and the build stops
immediately:

```
$ python atman/202608262014-build-pages.py --generation latest --stage _site \
        --timestamp-folder-release 202609030009-pipelinenews
PAGES BUILD GATE FAILED: timestamp release schema changed
  atman/202608262014-build-pages.py:664
```

Census of every release folder on `main`:

```
 1  pipelinenews.timestamp-folder-successor.v1     202608291447-pipelinenews
 1  pipelinenews.current-atlas-link-release.v2     202608300309-pipelinenews
30  pipelinenews.additive-cartridge-release.v1     202608311343 .. 202609030009
```

`validate_timestamp_folder_release()` accepts exactly two schemas. The third —
the additive-cartridge lineage that has produced **every** release since
31 August — is written by `tools/intelligence/release_builder.py:494` and is
read by **nothing**:

```
$ grep -rl "additive-cartridge-release" --include=*.py --include=*.mjs \
       --include=*.js --include=*.yml --include=*.md .
./tools/intelligence/release_builder.py
```

One producer, no consumer. And every one of those manifests declares
`"deployment": "not-authorised"` and `"runtime_verified": false` in its own
bytes. So the workflow's auto-selection hands the gate a release the release
itself says is not authorised for deployment.

The last successful Pages run was 2026-08-30 11:13 UTC. The first
additive-cartridge release is `202608311343`. The dates agree.

### Blocker 2 — the pointer/HEAD equality, and why fixing it changes nothing

With the pointer's own release passed instead, the build reaches F1's line and
fails there:

```
$ python atman/202608262014-build-pages.py --generation latest --stage _site \
        --timestamp-folder-release 202608291447-pipelinenews
AssertionError: live pointer commit is not deployment HEAD
  atman/202608262014-build-pages.py:904
```

F1 asked whether the rule should be *ancestor* rather than *equal*. **The
repository has already answered that question in its own source.** The newer of
its two pointer validators, `validate_current_or_predecessor_pointer()` at
line 619 — added 2026-08-30 in commit `aeb8827`, "validate Atlas-link v2 release
and current-or-predecessor pointers" — checks the same object like this:

```python
subprocess.run(["git", "merge-base", "--is-ancestor", pointer_commit, "HEAD"],
               cwd=root, check=True, capture_output=True)
```

Both validators check the same three companion invariants (copies committed
together, pointer commit is a one-parent child of the release commit, the
pointer commit changed nothing but the pointer files). Only the older one
demands equality with HEAD. So aligning them is a consistency repair, not a
weakening — I patched it in the repro clone and confirmed the assertion goes
away.

It does not unjam the deploy. The next gate fires.

### Blocker 3 — the published tree is frozen to 29 August by owner authorisation

```
PAGES BUILD GATE FAILED: legacy public tree changed outside exact Atlas V9
release/pointers: [1,756 paths]
```

`atman/202608262014-build-pages.py:1223-1256`, inside
`candidate_publication_boundary()`, and reached only when an owner
authorisation exists in `build/authorisations/` (there is exactly one,
`202608271524-v8-fast-pages-authorisation.json`):

```python
changed_public_paths = { git diff --name-only ATLAS_V9_SOURCE_PARENT HEAD
                         -- releases data archive state }
allowed_public_changes = timestamp-folder outputs
                       + the two pointer files
                       + every file under releases/<pointer release id>/
require(changed_public_paths.issubset(allowed_public_changes), ...)
```

`ATLAS_V9_SOURCE_PARENT = "693ccda8e6288d449763ce2b3a4ba16ed7b93fee"` is a
hard-coded constant — commit `693ccda8`, 2026-08-29 02:09 BST.

Measured at HEAD:

```
git diff --name-status 693ccda8 HEAD -- releases data archive state
  1796  A   (added)
     0  M   (modified)
     0  D   (deleted)
```

**Every one of the 1,796 divergences is an addition. Nothing that was published
at the freeze commit has been modified or deleted.** The allowance can cover at
most the 40 files of the pointer-bound release plus the two pointer files.

This is not an oversight. Read together with the README — *"Build instructions
do not authorise deployment. Every deployment requires explicit owner
approval"* — and with the `"deployment": "not-authorised"` stamped into every
additive-cartridge manifest, the gate is doing exactly what it was built to do:
**the owner authorised the publication of one exact tree, and nothing built
since has been authorised.** 27 red runs are that refusal, repeated once per
ordinary push, because the trigger asks for the deployment every time.

### The defect that is actually worth naming

There is **no route by which an owner can authorise a wider closure.** The only
authorisation record the gate understands is
`build/authorisations/<gen>-v8-fast-pages-authorisation.json`, which binds a
v8-fast candidate and carries no field that can move the closure; and
`ATLAS_V9_SOURCE_PARENT` is a constant in source, not data. A `workflow_dispatch`
with an explicit `expected_sha` — the manual route the workflow provides for
exactly this purpose — fails on the same three gates. So the authorisation
mechanism cannot express the authorisation the situation needs.

### What I did not do, and why

I did not ship a change to the Pages gate.

- Advancing `ATLAS_V9_SOURCE_PARENT`, or relaxing the closure check to permit
  additions, redefines what "the owner-authorised public closure" means, for
  1,796 paths. That is the decision the check exists to hold, and it is not
  mine to make unsupervised.
- Narrowing the workflow trigger (candidate (b)) would turn 27 red runs green
  by ensuring the workflow almost never runs, and would leave
  `ventusltd.github.io/pipelinenews/` on its 30 August build permanently while
  looking fixed. A green light over a question nobody is asking is the exact
  failure this estate keeps recording — the clock-dependent byte gate, the
  naming gap, the disconnected slack.
- Shipping only the ancestor alignment (candidate (a)) changes a governance
  gate's behaviour without achieving anything: blocker 3 still fires.

The brief said: *"If you cannot fix it without weakening a real check, stop and
say so — that is a legitimate outcome."* That is where this lands. The prepared
patch and the measurements are in `03-blocked.md` so the decision costs the
architect one command, not one investigation.

**What I got wrong on the way here.** I spent the first hour assuming F1 was
right and looking for the surrounding invariants of *one* line. The one-line
model survived until I ran the build. Reading the gate would never have told me
which assertion fires first; running it took ninety seconds.

---

## 2. A finding fell out of the closure audit: 10 published SHA ledger entries name bytes that were never served

To decide whether the 1,796 additions could be defended as ledger-covered, I
verified every `releases/<stamp>-pipelinenews/sha256sums.txt` against the bytes
on disk. 1,740 of 1,796 are covered. Ten entries, across six immutable
releases, **do not match their own release's published ledger**:

```
releases/202608311530-pipelinenews/data/202608311530-grid-proximity.json.sha256
releases/202608311550-pipelinenews/assets/202608311550-grid-proximity.mjs
releases/202608311550-pipelinenews/data/202608311550-grid-proximity.json.sha256
releases/202608311557-pipelinenews/assets/202608311557-grid-proximity.mjs
releases/202608311557-pipelinenews/data/202608311557-grid-proximity.json.sha256
releases/202608311558-pipelinenews/assets/202608311558-grid-proximity.mjs
releases/202608311558-pipelinenews/data/202608311558-grid-proximity.json.sha256
releases/202608311610-pipelinenews/assets/202608311610-grid-proximity.mjs
releases/202608311610-pipelinenews/data/202608311610-grid-proximity.json.sha256
releases/202608312018-pipelinenews/assets/202608312018-atlas-pointer-deep-link.mjs
```

I did **not** report these as corruption, because I checked before asserting.
For all ten, `sha256(bytes.replace(LF, CRLF))` equals the ledger digest exactly.
These ledgers were written by `release_builder.py`'s `sha256_file()` — the raw
hasher, not `sha256_published()` — from a Windows working copy holding CRLF,
before `.gitattributes` (added 2026-08-31 23:50) forced LF everywhere. The
served bytes are the LF bytes and they are correct; the **ledger** is wrong.

Consequence, and the reason it matters rather than being a curiosity: a reader
who downloads one of those six releases and checks it against its own published
`sha256sums.txt` gets a mismatch on a release nobody has touched. It is the same
defect the board already recorded for the inherited registry digests, in the one
place that was not fixed: `cmd_check` normalises line endings, the ledger writer
does not.

`releases/202608291447-pipelinenews` has no `sha256sums.txt` at all — it predates
the additive-cartridge builder. Not a fault, recorded for completeness.

---

## 3. The deep-link technology parameter: every wider-fleet MAP link is invalid by construction, and no release ever emitted `Landfill Gas`

The brief named a live failure — a deep link with `technology=Landfill Gas`
throwing `[V9 DEEP LINK FAILED] canonical project technology is invalid` — and
asked me to verify what PipelineNews actually emits. Two measured answers, and
the second is much worse than the first.

**PipelineNews has never emitted `technology=Landfill Gas`.** All three
wider-fleet releases build the link from `row.t`, not `row.rt`:

```
releases/202609030009-pipelinenews/assets/202609030009-wider-fleet.mjs:68
  query.set("technology", row.t);
```

and in the payload `rt` is the REPD type while `t` is an engine layer id. Every
`Landfill Gas` row emits `technology=biomass`. Verified across
`202609021945`, `202609022308` and `202609030009` — all three, same field.

Where `Landfill Gas` *can* reach a `technology` slot is the UI, not the URL, and
only in the two older releases: `202609021945` set `data-technology="${type}"`
on the wider tabs from the REPD type name, which is the spine's own attribute
and its own filter vocabulary. `202609030009` fixed that and says so in a
comment — *"NOT data-technology: that attribute is the spine's, and a value
outside its whitelist reaching its filter would empty the product's own table."*
So a click on a wider tab in `202609021945` could put `Landfill Gas` into the
spine's technology state, and any subsequent spine MAP link would carry it.
That is the most likely provenance of the reported URL, and it is already fixed.

**The larger finding is that fixing it changes nothing.** GridAtlas validates
the parameter against a four-member set —
`atlas/cartridges/202609030109-substation-intelligence-v9-63.js:823`, in the
live composition:

```js
const allowedTechnologies = new Set(['solar', 'bess', 'wind_onshore', 'wind_offshore']);
if (!allowedTechnologies.has(requestedTechnology)) throw new Error('canonical project technology is invalid');
```

Those four are exactly `SPINE_TYPES` in
`tools/intelligence/cartridges/wider-fleet/build_payload.py:71` — the four the
wider fleet is defined as *excluding*. The nine values the payload can emit —
`biomass, hydro, hydrogen, act, tidal, geothermal, caes, flywheel, other` — are
all outside it. So **all 1,104 wider-fleet MAP links throw on that lane, and
would still throw if the parameter carried the REPD type verbatim.** There is
no value PipelineNews can put in `technology` that this allow-set accepts.

The contract verifier passes 11/11 on this pair. It proves both sides agree on
the seven parameter *names*. Nobody had asked what happens to the *values* —
the same shape as every other finding in this estate's log.

**Not fixed by me, and deliberately so.** The remedy is on the GridAtlas side
(widen the allow-set, or scope the check to the lane that owns those four), and
that repository is the other agent's tonight. What my lane owed was the
measurement, and a check that asks the question. Both are here.
