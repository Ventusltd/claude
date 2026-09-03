# 02 — runner health

Every case where MY OWN check was wrong. A spider that never corrects itself is
not measuring, it is asserting.

---

## RH1 — 2026-09-03T01:25Z — the cvaa vaccine `disk-is-not-what-ships` is a
## 100% false positive, and I nearly reported it as the estate's top defect

**What the check said.** 18 of 18 repositories not immune, every one with the
identical finding:

    no .gitattributes: the working copy and the blob can differ, so any check
    that reads a file off disk is asking a different question from any check
    that reads what ships

That is a perfect wall. A perfect wall is the signature of a check that cannot
fail, and the brief says a check that cannot fail is not a check.

**What is actually true.** `cvaa` itself carries a `.gitattributes` with a
correct `* text=auto eol=lf` on line 30, plus binary rules and explicit
`text eol=lf` for every executable extension. Reproduced by hand:

    $ ls -a cvaa | grep gitattributes
    .gitattributes
    $ grep -E '^\s*\*\s+text=auto\s+eol=lf\s*$' cvaa/.gitattributes
    * text=auto eol=lf

**The defect.** The antibody opens with:

    export default ({ files }) => {
      const attrs = files['.gitattributes'];

and `inoculate.mjs` line 96 builds that object as:

    const files = { STATE: exists('STATE.md') ? read('STATE.md') : null,
                    index: exists('index.html') ? read('index.html') : null };

The key `.gitattributes` is never present in any repository, so
`if (!attrs)` is unconditionally true and the first branch always fires. The
second half of the antibody — the `SUSPECT` regex hunting for `createHash` over
`readFileSync` and `hashlib.sha256`, which is the defect the vaccine was
actually written to catch after four incidents in one evening — iterates
`Object.entries(files)`, so it only ever inspects `STATE.md` and `index.html`.
It has never examined a single line of the code it exists to police.

The vaccine's reasoning is sound and its provenance is real. Its wiring is not:
it was given none of the data it asks for.

**What I changed.** I do not edit `cvaa` — it is not my lane, and relaxing a
rule to make repos pass is forbidden. Instead:

1. `disk-is-not-what-ships` is listed in `spider-state.json` under
   `cvaa.distrusted_vaccines` and is EXCLUDED from every adoption count I
   report. The corrected top-three failing vaccines are
   `monotonic-utc-generations`, `chaining-token` and `pinned-actions`.
2. I evaluate the rule by hand instead, which takes one line and gives the
   right answer. Result, pass 1, all 18 local clones:

   | verdict | repos |
   |---|---|
   | `* text=auto eol=lf` present and correct | 14 |
   | `.gitattributes` present but WITHOUT that line | chatgpt-audits, claude, codex-chatgpt, gemini |
   | absent entirely | 0 |

   So the true finding is 4 repos, not 18, and none of them for the stated
   reason. Those four are all agent-notes repositories rather than shipping
   surfaces, which is why this ranks low on consequence.

**The fix cvaa needs** (recorded, not applied): `buildContext` must add
`'.gitattributes'` to `files`, and the second half of the antibody needs a
source-file corpus rather than a two-key object. Until then the vaccine reports
a conclusion it has no evidence for — which is the precise disease the cvaa
architecture exists to prevent, in cvaa itself.

---

## RH2 — 2026-09-03T01:52Z — four gates I called FAILING were my own
## invocation errors

I ran every discovered gate with no arguments and recorded four failures. All
four were mine.

| gate | my reading | truth |
|---|---|---|
| `pipelinenews/tools/intelligence/render_proof.mjs` | exit 2, FAIL | prints `usage: node render_proof.mjs <release-id>`. With `202609030009-pipelinenews`: **26 checks, 0 failed** |
| `…/sector_render_proof.mjs` | exit 2, FAIL | same; **11 checks, 0 failed** |
| `…/surface_truth_proof.mjs` | exit 2, FAIL | same; **8 checks, 0 failed** |
| `data-grid-gb/chatgpt/verify_product.py` | exit 1, IndexError | takes a product path. With `chatgpt/derived/etys-2025.normalized.json`: **PASS**, sha `40f0aa1c…`, 1735 sites / 1392 circuits / 1472 transformers |

A fifth, `data-gb-electricity/pipelines/verify_bounded_growth.py`, exits 1 on
`FileNotFoundError: reports/fetch_latest_month_latest.json`. That one is not an
invocation error and not a defect: it is a CI-only gate that verifies an audit
artefact the monthly updater produces. It is recorded as
`not-runnable-locally`, which is a different state from `fail`, and
`spider-state.json` keeps those states distinct so a later pass does not
resurrect it as a regression.

**What I changed.** `spider-state.json.gates` now stores the full command
including arguments for every gate, so a fresh instance cannot repeat this. Any
gate whose first run produces a usage string is a discovery result, never a
finding.

---

## RH3 — 2026-09-03T01:10Z — my crosslink extractor was blind to the three
## most important edges in the estate

The first extractor scanned line by line. Shipped gridatlas cartridges build
their product URLs by string concatenation across two lines:

    const PRODUCT = 'https://raw.githubusercontent.com/Ventusltd/data-grid-gb/'
      + 'main/derived/connection-points.v3.json';

The repository name is on line 1 and the ref is on line 2, so my
`raw.githubusercontent.com/Ventusltd/(repo)/(ref)/(path)` regex matched nothing.
The result was a graph that reported `gridatlas -> data-grid-gb` as a
*contract* edge only, and listed three mutable runtime edges when there are
five. Had I stopped there I would have reported that the exact edge the
coordinator flagged does not exist in shipped code — a false all-clear on the
highest-consequence finding of the night.

**What I changed.** The extractor now collapses JS/Python string concatenation
(`'…' + '…'`, across a newline) before matching, and attributes the hit to the
line the first fragment sits on. Recount:

    mutable shipped runtime-data edges   3  ->  5
    total raw edges                    667  -> 671

The two recovered edges are `gridatlas -> data-grid-gb@main` for
`derived/connection-points.v3.json` and `derived/gb-transmission-network.v1.json`.

**Generalisation for later passes:** any estate that writes URLs as constants
will split them at the 80th column. A line-oriented scanner under-reports
dependencies systematically, and it under-reports them silently — the graph
still looks plausible, just smaller. Count before trusting a count.

---

## RH4 — 2026-09-03T01:36Z — I committed a generation stamp in BST and
## labelled my own timestamps `Z`

My pass-1 commit is `202609030220: cicd-spider pass 1 baseline…`. Its actual
UTC commit time was 01:22Z. The stamp is **58 minutes ahead of the event it
names**, because I read the machine clock (BST, UTC+1) and wrote it as a
generation without converting.

    $ date -u +%Y-%m-%dT%H:%M:%SZ   ->  2026-09-03T01:35:56Z
    $ date    +%Y-%m-%dT%H:%M:%S %Z ->  2026-09-03T02:35:56 GMTDT

Several timestamps in `00-LOG.md`, `01-drift.md` and `03-crosslink.md` carried
the same error and have been corrected in place.

This is precisely `monotonic-utc-generations`, the vaccine I had just reported
as the estate's most widely failing rule at 14 of 18 repositories — "generations
are read from `date -u` at commit time, never chosen". I made the error in the
same hour, in the artefact reporting it. The vaccine is right, and it would have
caught me.

**What I changed.** Every timestamp I write now comes from
`date -u +%Y-%m-%dT%H:%M:%SZ` or Python's `datetime.now(timezone.utc)`, never
from the local clock. `pass.py` already used the UTC form, which is how the
discrepancy surfaced — the driver and I disagreed by exactly one hour and the
driver was right. The session directory name `202609030120` is correct UTC and
stays as it is; renaming it would break the resume contract for no gain.

The commit stamp itself cannot be corrected without rewriting a pushed commit,
which is not worth it. It is recorded here instead, which is what the vaccine
asks for: a wrong generation that is admitted beats a wrong generation that is
tidied away.

---

## RH5 — 2026-09-03T01:37Z — I summarised a gate from `tail -4` and reported
## the wrong scale

In pass 1 I recorded `gridatlas run-current` as "4 proofs run; every composed
cartridge passed its generation-matched proof", taken from the last four lines
of its output. The exit code was 0, so the verdict was right — but the *scale*
was wrong: at v9.82 the same gate prints `664/667 checks passed`, and the "4
proofs" line I quoted is a per-section footer, not the suite total.

The consequence is that a later pass comparing "4 proofs" to "667 checks" would
read a composition change as a catastrophic regression, or the reverse. A tail
is not a summary; it is whatever happened to be printed last.

**What I changed.** `pass.py` records the exit code as the verdict and stores
only the last non-empty line as a hint. When a gate goes red I now read the
`FAILURES` block explicitly rather than quoting the tail — which is how the
three real gridatlas failures were found.
