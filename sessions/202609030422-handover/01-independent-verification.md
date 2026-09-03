# Independent verification of `00-HANDOVER.md` — 2026-09-03, 09:26 UTC

A second pass over the estate and over the 04:22 handover, run by an agent that did not write it.
Everything below is re-measured from source. Where I could not settle a claim I say
COULD-NOT-CHECK rather than borrow the author's answer.

**Rule I held myself to:** I did not reuse the author's numbers as inputs. Where the author's own
instrument (`scripts/gen_drift.py`) was the only tool offered, I wrote a second one on a different
principle (epoch `%at` arithmetic rather than ISO parsing) and compared.

**I changed nothing.** No repository was modified except to add this file to `claude`.

**Line numbers below refer to `00-HANDOVER.md` as of `claude` commit `ef2cc68`, md5
`9de392840fcc449438d5fcb8c99c72fa`, 651 lines, read at 09:29Z.** The file was edited under me
during this pass — it grew from 615 to 651 lines when D15 was closed — so every citation quotes
the sentence as well as the line, and the quote is the durable half. Nothing I checked was
invalidated by that edit; the three inconsistencies in §4 survive it unchanged.

---

## Lead with what is wrong

Four things. Two are new estate facts, two are defects in the document.

1. **NEW RED — `data-gridatlas` is failing and the handover does not know about it.** Its
   `202608301931-layer-fidelity.yml` workflow failed at **08:09Z today**, hours after the
   handover was written, at the current head `8bf88da`. It is the only failing workflow in that
   repo — the other four at the same head are green. Cause below.
   *(Corroborated: the CI spider found the same red independently at 09:19Z, `claude` commit
   `6752fff`, and correctly notes it is new and unowned.)*

2. **`globalgrid2050` has TWO failing workflows at head, not one.** The handover's §8 table
   (line 477) records the repo's red as *"D1, firing. Not a defect — my verifier working"*.
   That is true of `verify-published-versions.yml`. But `v9-7-validate.yml` is **also failing at
   the same head `a0f93e8`, and has failed on every run since at least 2026-09-02 19:25Z** — six
   consecutive failures across six different commits. It is not D1 and it is not a verifier
   reporting a known open decision. Attributing the repo's red solely to D1 hides it.

3. **REFUTED (in part) — claim 6, the `cvaa` row of the stamp-drift table.** The handover reports
   `cvaa` at **15 stamped / 3 ahead / worst 248 min**. That is a measurement of the **parallel
   session's divergent local worktree** (`C:\Users\vikra\OneDrive\Documents\GitHub\cvaa`, HEAD
   `c18cc13` — 9 behind and 2 ahead of origin), which the same document flags at line 335 as
   *"a different session's checkout"*. Measured on **`cvaa` origin/main** the answer is
   **24 stamped / 1 ahead / worst 200 min**. The published figure is not a measurement of cvaa's
   main line. Every other row in that table checks out exactly.

4. **The document is still internally inconsistent in three places** (Task 3, detail in §4):
   a stale 32-repo denominator at line 567, a failing-surface table that sums to 46 against a
   stated total of 47, and a `claude` commit count that reads 86 in one paragraph and 89 in two
   others.

Everything else I was asked to check is CONFIRMED.

---

## 1. Estate CI — every repo, its own default branch

Repos enumerated from `user/repos?per_page=100&affiliation=owner` (authenticated), **not** from
disk.

```
35 owned repositories
  1 fork      pandapower (default branch: develop)
  2 private   cable_selection, crm
```

Measured two ways, which agree:

| basis | green | red | no runs |
|---|---|---|---|
| latest run on the default branch (the baseline's method) | **19** | **5** | **11** |
| latest run *per workflow file* at each repo's current head | **19** | **5** | **11** |

I ran the second basis deliberately, because "latest run overall" hides a red workflow behind a
newer green one from a different workflow. It did not change the population — but it is what
exposed the second `globalgrid2050` failure in §1.2 below, which the first basis cannot see.

**No runs (11):** `Mahabharata`, `Solar-PV-Hybrid-and-off-grid`, `cable_selection`, `claude`,
`codex-chatgpt`, `crm`, `gemini`, `pandapower`, `pv-arc-protection-circuit`,
`solar-repowering-whitepaper`, `uk-dno-data`.

**Red (5):** `data-gridatlas`, `data-interconnectors`, `globalgrid2050`, `globalgrid2050-hompage`,
`pipelinenews`.

### DRIFT from the ~05:00 baseline

| | baseline ~05:00Z | now 09:26Z | drift |
|---|---|---|---|
| owned repos | 35 | 35 | none |
| fork / private | `pandapower` / `cable_selection`,`crm` | identical | none |
| green | 20 | **19** | −1 |
| red | 4 | **5** | +1 |
| no runs | 11 | 11 | none |

**One drift, one member: `data-gridatlas` moved green → red.** At the baseline its most recent run
was `Hourly watchdog` at 04:32Z, `success`. Its `202608301931-layer-fidelity.yml` workflow then ran
at 08:09Z and failed. The other four baseline reds are unchanged and still red for the same causes.

### Cause of each red, read from the log

| repo | run | cause (one line) |
|---|---|---|
| **`data-gridatlas`** | `33731864220`, 08:09Z today, head `8bf88da` | **NEW.** `layer-fidelity` renders every layer in a headless browser and fails any layer that takes >15 s, exceeds 400 MB heap, or yields <1 feature: **50 of 120 layer checks failed** — four layers (`ind`, `air`, `metro`, `tram`) return **0 features**, and the large data layers (`solar`, `wind`, `bess`, `naei_co2`, …) all sit at **60.3 s** against a 15 s budget, i.e. they hit the 60 s source-loaded timeout. Criterion at the workflow's line 424: `!label.includes('[OK]') \|\| !loaded \|\| seconds > 15 \|\| heapMb > 400 \|\| features < 1`. 70 layers still PASS, so the instrument discriminates — this is not a flat failure. |
| **`globalgrid2050`** (a) | `33710834586`, 03:17Z today | `PUBLICATION TRUTH: FAIL` — *the homepage names Grid Atlas **v9.86 / 202609030200** as the current verified release while the live composition is **v9.88 / 202609030234***. Exactly the baseline's known open decision (D1), and the exact version pair the baseline predicted. **Not a defect.** |
| **`globalgrid2050`** (b) | `33710834537`, 03:17Z today, and 5 earlier runs back to 2026-09-02 19:25Z | **Not in the handover.** `v9-7-validate.yml`: the V9.7 regional build reproduces `uk_renewables_pipeline/v9.7/data/v9.7/regional_manifest.json` with a different `input_sha256` (`cea104c3…` committed vs `e6c42cd8…` rebuilt); the job diffs the rebuilt manifest against the committed one and exits 1, then posts commit status `globalgrid/v9.7-validation = failure`. The committed manifest no longer reproduces from its inputs. |
| **`pipelinenews`** | `33698385910`, 00:10Z today | `PAGES BUILD GATE FAILED: timestamp release schema changed` → `AssertionError` at `atman/202608262014-build-pages.py:664`, in `validate_timestamp_folder_release`, from `require(release_manifest.get("schema") == TIMESTAMP_FOLDER_RELEASE_SCHEMA, …)`. The D8 schema divergence, exactly as the baseline and the handover describe. |
| **`data-interconnectors`** | `33623861881`, 2026-09-02 11:17Z | `##[error]Input required and not supplied: token` at the checkout step of `gridbot_uk_interconnector_build.yml`, which passes `token: ${{ secrets.GRIDBOT_PAT }}`. |
| **`globalgrid2050-hompage`** | `33626102903`, 2026-09-02 11:43Z | Identical: `Input required and not supplied: token`, `gridbot_federation_systems_map.yml`. |

**Secrets, verified directly** (`/actions/secrets`, authenticated) — the handover's table at
lines 497–501 is CONFIRMED:

```
data-interconnectors    total_count 0   []
globalgrid2050-hompage  total_count 0   []
globalgrid2050          total_count 2   ['GRIDBOT_PAT', 'OCM_API_KEY']
```

---

## 2. The seven claims

### Claim 1 — GridAtlas v9.79→v9.88 (10 cuts); Pipeline News 3 generations since 2026-09-02 18:00 — **CONFIRMED**

`git log origin/main --format='%aI %h %s'` in `gridatlas` (local HEAD `ed2135f` == `origin/main`),
last commit naming each version:

```
v9.79  2026-09-03T01:11:06Z  ac810d6   v9.88  2026-09-03T02:35:08Z  8fb95a2
v9.80  01:16:48  v9.81 01:20:00  v9.82 01:28:26  v9.83 01:38:13
v9.84  01:52:02  v9.85 01:56:55  v9.86 02:00:52  v9.87 02:33:32
```

Ten distinct versions, v9.79 through v9.88 inclusive, all cut between 01:11Z and 02:35Z on
2026-09-03. (v9.78 landed at 01:02Z and is correctly excluded from the ten.) The live-composition
version reported by `globalgrid2050`'s publication-truth gate is **v9.88 / 202609030234**, which
matches `8fb95a2`'s own stamp — an independent corroboration from a different repository.

Pipeline News, `ls -d releases/*-pipelinenews` in `pipelinenews` (local `cdb8fe9` == `origin/main`).
Releases in order around the boundary:

```
… 202609020552, 202609020611, | 18:00 Sep 2 | 202609021945, 202609022308, 202609030009
```

Exactly **three** after 18:00 on 2026-09-02, and they are the three named. Nothing has been cut
since `202609030009` (00:09Z); at 09:26Z that is 9 h 17 m of silence, up from the 4 h the handover
recorded.

> **Soft inconsistency worth flagging, not a refutation.** §1 line 20 quotes the cadence agent as
> logging *"nine generations, all green"* while the same table records **3** delivered. Eight
> `202609*` releases exist in total. The two numbers are measuring different things (the cadence
> agent's whole run vs. the post-18:00 window), but a reader lands on 3, 8 and 9 in the same
> section with nothing reconciling them.

### Claim 2 — cvaa green on main at `93e568e` or later — **CONFIRMED**

```
$ git -C cvaa fetch origin main && git log -1 --format='%H %aI %s' origin/main
93e568ea7b1df4e328f395746976dcdc5c326922  2026-09-03T04:27:01Z
202609030427: a rollback drill leaves an artefact, not a sentence
```

`origin/main` HEAD is still **`93e568e`** — the other agent working in `cvaa` has not pushed as of
09:26Z. Latest runs on `main` from the Actions API:

```
2026-09-03T04:27:05Z  success  93e568e  202608301447 Self-test and full-history fleet audit
2026-09-03T04:27:04Z  success  93e568e  pages build and deployment
2026-09-03T04:14:15Z  success  7c8ed09  202608301447 Self-test and full-history fleet audit
```

Both `7c8ed09` and `93e568e` are green, as the handover states at lines 34–37. **Note for whoever
picks this up:** the local checkout at `OneDrive/Documents/GitHub/cvaa` is still at `c18cc13`,
9 behind and 2 ahead of origin, exactly as §5 item 6 describes. It is untouched by me. It is also
the tree that produced the wrong drift figure in claim 6.

### Claim 3 — exactly 3 of 18 local repos lack the anchored rule — **CONFIRMED**

18 directories under `C:\Users\vikra\OneDrive\Documents\GitHub\` contain a `.git`. Predicate
applied to the **committed** `.gitattributes` (`git show HEAD:.gitattributes`, with
`MSYS_NO_PATHCONV=1` set inline on that one command only):

```
grep -qE '^[[:space:]]*\*[[:space:]]+text=auto[[:space:]]+eol=lf[[:space:]]*$'
```

| result | repos |
|---|---|
| **FAIL — 3** | `chatgpt-audits`, `codex-chatgpt`, `gemini` — each carries bare `* text=auto` on line 2, GitHub's default template, with no `eol=lf` |
| **PASS — 15** | `claude`, `companies`, `cvaa`, `data-centres-gb`, `data-federation-map-for-globalgrid2050-all-repos`, `data-gb-electricity`, `data-grid-gb`, `data-gridatlas`, `data-interconnectors`, `gb-electricity-ui`, `globalgrid2050`, `grid-distance-maths`, `gridatlas`, `pipelinenews`, `spiders` |

**`claude` PASSES** — confirmed. The offender set is exactly the three claimed, by name.

Control on the instrument, since the whole point of D5 is that the loose predicate lied: the
anchored test returns **3 FAIL / 15 PASS**, a discriminating answer. A loose `grep text=auto`
returns 18/18 — the flat answer the handover says it published twice. The discriminating one is
reproducible here.

### Claim 4 — `claude` has zero tracked files at `i/lf w/crlf` — **CONFIRMED**

```
$ git -C claude ls-files --eol | grep -c '^i/lf.*w/crlf'
0
```

Zero, and `grep '^i/lf.*w/crlf'` returns no lines at all.

### Claim 5 — PipelineNews release-manifest schema census — **CONFIRMED**

The consumer path is confirmed from the failing CI log itself, not just from the source:
`atman/202608262014-build-pages.py` → `main()` line 1517 →
`validate_timestamp_folder_release(root, args.timestamp_folder_release)` → line 664, which reads
`releases/<id>/release-manifest.json`.

Parsing every `releases/*/release-manifest.json` in `pipelinenews` at `cdb8fe9`:

```
     30 pipelinenews.additive-cartridge-release.v1
      1 pipelinenews.current-atlas-link-release.v2      releases/202608300309-pipelinenews/
      1 pipelinenews.timestamp-folder-successor.v1      releases/202608291447-pipelinenews/
```

32 manifests, 30/1/1 as claimed, and the `v2` one is `202608300309` as named. (There are 37 entries
under `releases/`, of which 32 are `*-pipelinenews` release directories; the rest are loose
candidate HTML files and shared asset directories.)

### Claim 6 — generation-stamp drift — **CONFIRMED for 5 of 6 repos, REFUTED for `cvaa`**

I wrote a second instrument rather than trust `gen_drift.py`. Mine reads `%at` (epoch seconds) and
does calendar arithmetic on the 12-digit stamp with `calendar.timegm`; the author's parses `%aI`
with `datetime.fromisoformat` and converts. Different failure modes, same window
(`git log -400`), same threshold (stamp more than 15 minutes **ahead** of its own commit time).

| repo | claimed stamped / ahead | **my measurement** | verdict |
|---|---|---|---|
| `pipelinenews` | 220 / **125** | **220 / 125**, worst +253 min | CONFIRMED |
| `gridatlas` | 298 / **118** | **298 / 118**, worst +249 min | CONFIRMED |
| `globalgrid2050` | 56 / 19 | **56 / 19**, worst **+827 min** | CONFIRMED |
| `claude` | 89 / 8 | **8 ahead**; stamped now 106–108 | CONFIRMED, denominator has since drifted (below) |
| `cvaa` | 15 / **3** | **origin/main: 24 / 1**, worst +200 min | **REFUTED — wrong tree** |
| `data-grid-gb` | 5 / **5 of 5** | **5 / 5**, worst +117 min | CONFIRMED |

The worst-case minutes differ by exactly 1 on three rows (253 vs 252, 249 vs 248, 117 vs 116)
because the author's script truncates with `int()` and mine rounds. That is arithmetic, not
disagreement, and the 827 agrees exactly.

**The `cvaa` refutation, shown rather than asserted.** Running my instrument against the two trees:

```
cvaa @ c18cc13  (local worktree, 9 behind / 2 ahead of origin)  stamped=15  ahead=3  worst=248
cvaa @ origin/main (93e568e)                                    stamped=24  ahead=1  worst=200
```

The local figure reproduces the published `15 / 3 / 248` to the digit. So the handover's `cvaa`
row was taken from the parallel session's checkout — the one it explicitly says at line 335 it did
not touch and could not vouch for. On cvaa's actual main line, one commit is stamped ahead, not
three, and the denominator is 24, not 15. I checked the other five repos for the same hazard:
`pipelinenews`, `gridatlas`, `globalgrid2050` and `claude` all had local HEAD identical to
`origin/main`, and `data-grid-gb` (local 1 behind) gives 5/5 on both refs — so no other row is
affected.

**On `claude`'s 89.** At `56aa063` — the last commit of the handover session — I measure
**106 stamped, 8 ahead, 1 behind, worst +78 min**; at current HEAD `6752fff`, 108 stamped, 8 ahead.
The **8 ahead** is stable and confirmed. The denominator 89 was correct when written and has simply
grown as the session kept committing; it is a snapshot, not an error. But see §4 — the document
also states 86 in another paragraph, and those two cannot both be right.

I also reproduced the handover's controlled 01:57Z split independently, at `56aa063`:

```
before 01:57Z:  18 commits,  8 outside 15 min  (44%), worst 385 min
after  01:57Z:  88 commits,  1 outside 15 min  (1.1%), worst  19 min
```

The **before** row matches the document exactly (18 / 8 / 385). The **after** row has grown from
71 to 88 commits with the single exception unchanged — so the remedy's evidence has strengthened,
not weakened, since it was written.

### Claim 7 — every published generation carries the same `<title>` naming `202608300309` — **CONFIRMED**

Live over HTTPS, five generations including two the handover did not test:

```
202609030009 [200] <title>PipelineNews | Current verified Atlas V9 deep-link successor 202608300309</title>
202609022308 [200] <title>PipelineNews | Current verified Atlas V9 deep-link successor 202608300309</title>
202609021945 [200] <title>PipelineNews | Current verified Atlas V9 deep-link successor 202608300309</title>
202608312339 [200] <title>PipelineNews | Current verified Atlas V9 deep-link successor 202608300309</title>
202609020552 [200] <title>PipelineNews | Current verified Atlas V9 deep-link successor 202608300309</title>
```

Byte-identical titles, all `200`, across five different served directories.

**I applied the "same answer for every subject" rule here before reporting it**, because this is
precisely the shape of a broken instrument. The instrument is not broken: the same `curl | grep
-oiE '<title>...'` pipeline returns a *different* title from other pages on the same host, and the
five URLs demonstrably serve different directories (different HTTP paths, all 200, none redirecting
to a common page). The uniformity is a property of the artefact, and `202608300309` is
independently corroborated as the last release whose schema the deploy gate accepts (claim 5).

---

## 3. Bonus finding — the CSV exemption note is itself incomplete

Not one of the seven, but it is a factual claim in the same document and it is cheap to check.

Lines 160–165 state that the only CRLF blobs in the estate are 223 CSVs in `globalgrid2050`, and
offer a self-correction: *"the comment says 221 historical generation CSVs under `data/generation/`;
the measurement is 223, and they include `data/electricity/`."*

The total is right and all 223 are `.csv` — but the correction's account of *where* they live is
not:

```
$ git -C globalgrid2050 ls-files --eol | grep 'i/crlf' | wc -l          223
$ ... | grep -c '\.csv$'                                                223
199  data/generation/
 12  data/electricity/
  7  uk_energy_tracking_v5/
  5  uk_energy_tracking_v6/
```

199 + 12 = 211, not 223. Twelve of them sit under `uk_energy_tracking_v5/` and
`uk_energy_tracking_v6/`, which the correction does not mention. The exemption verdict is
unaffected — they are all CSVs and all covered by `*.csv -text` — but a reader who takes the
correction literally will look for 223 files in two directories and find 211 in four.

---

## 4. Internal consistency of the document

Re-checked every population count, every `N of M` and every total. The 32-vs-35 denominator the
document was corrected for **is fixed in the places it was flagged** — §8's headline (line 442),
the denominator box (lines 444–464), the vaccine census (lines 526–531) and the failing-surface
table (lines 544–550) all now say 34 or 35 consistently, with the 32 appearing only where it is
explicitly labelled as the superseded figure.

Three contradictions remain.

### 4a. Line 531 — a stale 32-repo denominator survived the correction

> line 562: *"across **34 repos × 25 vaccines = 850 states: 777 immune, 47 fail, 26 warn**"*
>
> line 567: *"`pinned-actions` … **17 immune, 15 warn, 0 fail**. It led every table we produced."*

17 + 15 + 0 = **32**, not 34. Every other per-rule figure in the document is stated over 34
(lines 535–537, 508–514, each row of which sums exactly to 34). This is the same 32-repo
denominator the document corrected forty lines earlier, in the one sentence the correction did not
reach. By the document's own reconciliation at line 529 — the two added repos are private, carry
zero workflows and are immune, so no failing or warning count moved — the corrected line should
read **19 immune, 15 warn, 0 fail**.

### 4b. Lines 508–514 vs lines 526–527 — the failing surface sums to 46, not 47

> lines 526–527: *"777 immune, **47 fail**, 26 warn"*, repeated at line 572: *"47 vaccine-repo pairs"*

The table said to be *"the complete failing surface"*:

```
monotonic-utc-generations  14      no-time-based-gates            3
chaining-token             12      pointer-verifies               2
self-terminating-loops      7      executor-declared              1
no-per-release-workflows    6      loop-exists                    1
                                                          total  46
```

**46, against a stated 47.** Line 520 says *"Eight rules fail at all"* and eight rules are listed,
so a ninth rule has not been dropped from the table — one of the two numbers is wrong. Each row is
internally consistent (`failing` + `quiet on` = 34 on all seven rows), which points at the 47 or at
a single row's count rather than at the table's structure. I could not settle which is right
without re-running the spider's `census.sh`, which lives in `cvaa` where another agent is working.
**COULD-NOT-CHECK which number is correct; the contradiction itself is confirmed.**

### 4c. Line 574 vs lines 555 and 584–585 — `claude` is 86 in one paragraph and 89 in two others

> line 591 (the drift table): `| claude | 89 | 8 | 77 min |`
> line 610: *"77 of 86 in `claude` are within 15 minutes"*
> lines 620–621: `before 01:57Z | 18` + `after 01:57Z | 71` = **89**

86 ≠ 89. And the two are not reconcilable by rounding: the document states 8 commits ahead
(line 591) plus 1 behind (implied by line 621's single exception after 01:57Z and line 599's
*"exactly one commit here is that case"*), i.e. 9 outside the window. 89 − 9 = **80** within, not
77. 77 within with 9 outside implies a denominator of 86.

Both were probably true at different minutes of a session that was still committing — my own
measurement at `56aa063` gives 106, and 86 and 89 are simply earlier snapshots of the same growing
number. But as it stands a reader gets three different totals for the same repository in the same
section, and the "77" does not follow from either.

### Also noted, prose rather than arithmetic

Line 403: *"a disk scan has under-counted this estate twice — 15, then 30, then 33"* lists three
under-counts, not two, since 33 is itself an under-count of 35 (it is the unauthenticated
public-only figure the document identifies at line 452).

### Checked and found consistent

- 20 + 4 + 11 = 35 (line 442) — arithmetic correct for the state at 04:22.
- 777 + 47 + 26 = 850 = 34 × 25 (lines 526–527).
- 727 + 47 + 26 = 800 = 32 × 25, and 777 − 727 = 50 = 2 × 25 (line 529) — the reconciliation of
  the two censuses is exact.
- 33 public − 1 fork = 32; 35 owned − 2 private = 33 (lines 451–454).
- pinned-actions 15 warn + least-permissions 11 warn = 26 warn total (lines 523, 490).
- Every row of the failing table: `failing` + `quiet on` = 34.
- §8's headline `20 green · 4 red · 11` (line 442) is a correct 04:22Z snapshot, not an
  inconsistency — but it is now **stale**: at 09:26Z the estate reads 19 · 5 · 11. Anyone quoting
  that line after `data-gridatlas` went red at 08:09Z will be quoting a five-hour-old number.
- 30 + 1 + 1 = 32 releases (lines 280–284).
- Thirteen numbered walls listed, "a second wall, there are twelve" = 13 (lines 295–311).
- 4 + 19 = 23 files at `i/lf w/crlf` (lines 148, 157).
- D5's four repos (line 102) minus `claude`, fixed, leaves the three at line 132; the spider's
  "4 and 14" sums to 18 (line 126).
- Seven generations listed against "all seven" (lines 365–366).

---

## 5. What I could not check

| | why |
|---|---|
| Which of `47` or the table's `46` is the true failing-surface total (§4b) | needs the spider's `census.sh` re-run, which lives in `cvaa` — another agent is working there and I was asked not to touch its files |
| The per-rule vaccine counts themselves (14/12/7/6/3/2/1/1) | same reason. The document is candid that these are the spider's measurement and not a second one (line 562); I have not added a third |
| The mobile-viewport question at lines 388–393 | the author's own account of the failure is that Chrome reported resizes as successful while `innerWidth` never moved. Out of scope for this pass and I have no better harness |
| Whether `additive-cartridge-release.v1` is the intended successor schema (§5's open question) | a design judgement, not a measurement |

---

## 6. Method

- Repos from `user/repos?per_page=100&affiliation=owner`, authenticated via
  `scripts/gh-api.sh`. Never from disk.
- CI from `/actions/runs?branch=<the repo's own default_branch>`, deduplicated on the **workflow
  file path** at the current head, not on run-name — GitHub's `name` is the run-name, and
  `data-gridatlas` interpolates `${{ github.sha }}` into it, so keying on it counts stale runs at
  superseded heads as separate workflows. (This is RH36 in `sessions/202609030120-cicd-spider/`;
  I hit the same trap and adopted the same fix.)
- All five failure causes read from `/actions/runs/<id>/logs` — 200, not 403.
- Drift from a second instrument written for this pass, epoch-based, compared against
  `gen_drift.py`'s window and threshold.
- Live titles over HTTPS with `curl`, HTTP status recorded alongside every title.
- `git show HEAD:.gitattributes` with `MSYS_NO_PATHCONV=1` **inline**, per the note in the task.

Everything above is at 2026-09-03 09:26Z. `data-gridatlas` was green four hours before I looked.
