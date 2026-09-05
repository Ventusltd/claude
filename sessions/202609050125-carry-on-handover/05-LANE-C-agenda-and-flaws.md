# Lane C — seven days of git, every chat: THE AGENDA and THE FLAWS

Written 202609050315 UTC. Commissioned by Vikram, verbatim:

> "run another agent that does git tracking of all code since the last 7 days
> and queries all chats and then processes what is the agenda and what are the
> flaws"

Lane C changed nothing. This file and one row on `02-LANE-BOARD.md` are the only
things it wrote.

---

## 0 · The instrument, and what it read

**Repositories.** Enumerated from `user/repos` via `scripts/gh-api.sh`, not from
disk. **39 repositories** on the account (37 public, 2 private). **26 had a commit
in the seven days to 2026-09-05 02:56Z**; 13 were cold. An earlier session
scanned 15.

**Git.** Every branch of every active repository, paginated in full, over
`--since="7 days ago"`.

| | |
|---|---|
| commits landed on default branches | **1,120** |
| commits on branches that never merged | **187** |
| branches carrying unmerged work | **53**, across 9 repositories |
| authors on default branches | `Ventusltd` 1,013 (90.4%) · `actions` 57 · `claude` 29 · `github-actions[bot]` 19 · `data-gridatlas-stage-bot` 1 · `gridbot` 1 |
| busiest days | 03 Sep 297 · 30 Aug 207 · 01 Sep 197 · 31 Aug 187 |

**Chats.** 20 session transcripts, 133 MB, across three project directories
(`C--Users-vikra`, `C--Users-vikra-OneDrive-Documents-GitHub`,
`C--Windows-system32`). Parsed as JSONL; **323 messages of Vikram's own**,
2026-08-30T21:26Z → 2026-09-05T02:57Z, read in full. Assistant turns sampled.
Reproducible: `scratchpad/chats.py`, `sweep2.py`, `ci.py`, `stamps.py`.

**A correction against myself, before anything else.** My first sweep reported
4,797 commits and "86.8% never reached the default branch". That was my own
instrument: `commits?...&per_page=100` with no pagination, so any branch with more
than 100 commits in the window was truncated, and every default-branch commit past
page 1 was misread as unmerged. gridatlas alone has 342 on `main` in the window.
The corrected figures are the ones above. **A sweep that returns a startling
number for the largest repositories first is exactly where to check the
instrument.**

---

# PART ONE — THE AGENDA

## 1 · What this is being built as, in his words

The product statement he wrote himself, 2026-08-30T21:45Z, and never contradicted
in the six days since:

> "this is a **timing engine for grid-connection sales, not a map**. The money for
> studies, cable and LV design is paid BEFORE a project's design freeze; the
> market fights over inverters AFTER. The system's value is being one supplier a
> month ahead of the trade press by watching two registers — Companies House for
> the FUNDING signal and local planning registers for the PROCUREMENT signal — and
> staying silent until both are on the record."

And the architecture, same message and again on 2026-08-30T22:41Z:

> "globalgrid2050 is NOT decaying. It is the **ORIGIN HUB**, being deliberately
> 'big-banged' out into specialised repos and apps... The 240 workflows are
> INTENTIONALLY PAUSED, not abandoned."

The mission statement, 2026-09-04, in the seed repo, over six consecutive
messages between 22:47 and 23:16 — the longest sustained single subject of the
week:

> "I want people to adopt it as a protocal and I want to get to billions of lines
> of CODE"
> "THE INTERNET DOES NOT POWER THE POWER INDUSTRY, THE POWER INDUSTRY POWERS THE
> INTERNET"
> "Every node, every wire, every cable, every light will eventually be mapped in
> gg50 whilst respecting national security and soverignty"
> "the SLDs behind real mechanics and electrics and gauraded in client datarooms
> NOT HERE"

And his own role, stated three times (2026-08-31T13:06Z, 15:44Z, 2026-09-04T21:02Z):

> "I am not a programmer, thats your job, I am the architect"
> "I need you to lead on the MATHS"
> "I need graphically interfaces to understand code as I am not a coder but rather
> a grid specialist"

## 2 · Decided and shipped

Each of these was asked for and exists.

| what he asked | when | where it is now |
|---|---|---|
| All 20 non-spine REPD technologies as **extra tabs, not touching the spine** — "BUT, BUT, BUT, I want this as a seperate tab to not affect the solar, wind and BESS FOCUS!!!!!!!!!!!!!" | 2026-09-02T18:27Z | live; 25 technologies, later collapsed to a dropdown on his own decluttering request 2026-09-03T12:57Z |
| Sort by MW / REPD date, and town, postcode, county columns | 2026-08-31T15:10Z | live in Pipeline News; all ten sort modes verified monotonic by Lane B tonight |
| Capacity slider 1–5000 MW | 2026-08-31T18:11Z | live |
| Grid distance from a project to substations, with a BETA caveat | 2026-08-31T17:46Z | live; `grid-distance-maths`, then `ventus-grid-engine` |
| 400 kV / DCO connection logic for West Burton, Cottam, Beacon Fen | 2026-09-01T13:35Z | live; NESO ETYS appendices B and D via `data-grid-gb`, every figure cited |
| A cross-session memory so "we don't start fresh each time" | 2026-09-03T10:13Z | `claude/logs/parquet/`, 11 sessions, 32,018 rows, 10.7× compressed, verified from a clean checkout |
| "immortalise yourself in the claude repo by logging every 30 minutes" | 2026-09-03T23:20Z | `claude/sessions/`, `logs/`, `docs/boards/`; this session resumed from it |
| A spider receiver page for the engine graph, keeping the 🕷 button exactly | 2026-09-04T20:50Z | https://ventusltd.github.io/ventus-grid-engine/ — reference file reused byte-identical |
| An estate menu linking every dashboard | 2026-09-04T21:10Z | shipped 202609042211 |
| "SEED" paper, 1991 vs 2026 | 2026-09-04T22:59Z | `seed-data`, 4 commits |

## 3 · Decided and NOT shipped — the useful category

These were agreed, in his words, and have not happened. Each is located.

### 3.1 · A licence. He said the estate is open source; **8 of 10 core repositories carry none.**

> "I am designing this to be open source and public so be aware of that!!!!!!"
> — 2026-09-03T10:20Z

> "I want people to adopt it as a protocal" — 2026-09-04T22:47Z

Measured by `git ls-files` for `LICENSE|LICENCE|COPYING`:

| repo | licence file |
|---|---|
| `gridatlas` | none |
| `pipelinenews` | none |
| `ventus-grid-engine` | none |
| `cvaa` | none |
| `spiders` | none |
| `data-grid-gb` | none |
| `seed-data` | none |
| `studies` | none |
| `globalgrid2050` | `LICENSE.txt` — CERN OHL-S v2; GitHub reports `NOASSERTION`, i.e. it does not recognise it |
| `claude` | `COPYING` — GPL-2.0 |

Across all 39 repositories the API reports a recognised SPDX licence on **6**.
Without a licence file the default is all-rights-reserved: nobody can adopt what
he is asking the world to adopt. **This is the single largest gap between the
agenda and the state of the estate, and it is one file per repository.**

### 3.2 · "Bring the v8 layers back" — asked twice, still measurably absent

> "port all the layers in drop down menu and call it Grid, **every layer used to
> work I have tested it myself before**, we have several versions!"
> — 2026-09-03T20:36Z

> "Did you forget bringing the v8 layers back?" — 2026-09-04T21:22Z

Three independent measurements say the layers are gone, not hidden:

1. `Ventusltd/data-gridatlas` → `202608301931 Layer fidelity, V8 origin vs V9
   delivery` is a **scheduled** workflow and its last scheduled run **failed,
   2026-09-04T08:04:45Z at head `8bf88da9`**. A 2026-09-03 diagnosis in this repo
   recorded 50 of 120 layer checks failing, with `ind`, `air`, `metro`, `tram`
   returning **0 features**.
2. `claude/docs/boards/estate-link-crawl.md`, crawled 2026-09-04T07:24Z:
   **140 distinct dead URLs on the `gridatlas-atlas` surface**, including
   `uk_motorways.geojson`, `uk_trunk_roads.geojson`, `uk_primary_roads.geojson`,
   `uk_mainline_railways.geojson`, `uk_metros_trams.geojson`,
   `heavy_emitters_uk.json`, `dist/repd_master.json` — all 404 at
   `https://ventusltd.github.io/<file>`, each seen in 5 releases.
3. `170 of 238 routes dead` across the ten published Atlas releases.

He is right, and the reason is a root-path move nobody followed.

### 3.3 · Codex's 41-iteration branch, ordered by him, never merged

> "Work till all tokens are exhausted or at least 30 iterations of pipelinenews
> and gridatlas are built each improving on the last... use isolated branches to
> not conflict and **we can merge after testing**" — 2026-09-03T23:10Z

`Ventusltd/gridatlas` → `codex/20260904-gridatlas-30x`: **41 commits**, iterations
01–41, 2026-09-03T23:17Z → 23:55Z, **2,436 lines across 3 files**
(`atlas/codex/20260904-finding-loop-30x/finding-loop.mjs` 1,336 lines,
`proof.mjs` 1,030, plus a candidate workflow). It is now **19 commits behind
`main`** and has never been merged or evaluated. The testing he named as the
merge condition has not been recorded anywhere in the repo.

This is the largest single block of work in the week that reached no product.

### 3.4 · "Do not build huge monologues" — the file grew instead

> "also remember to build code in a **modular fashion do not build huge
> monologues** that become difficult to maintain" — 2026-09-01T17:28Z
> "**if there are 4000 lines then modularise next versions**" — 2026-09-01T18:34Z

Measured in a clean clone of `origin/main` at `5c013cd` (2026-09-05T03:03Z), the
cartridge the live composition actually loads:

```
atlas/cartridges/202609050301-sld-sandbox-v9-8.js     7,382 lines
```

`atlas/cartridges/` holds **100 files, 29 MB, of which 52 are copies of
`sld-sandbox`** — one whole 7,000-line file per generation. His threshold was
4,000 lines four days ago.

### 3.5 · The four functions that block every skin he described

> "you should be able to create endless avatars of the app for any environment any
> form, in future in cars, laptops, Google hubs, smart TVs, watches"
> — 2026-09-03T15:38Z

The skin-architecture study he commissioned (`claude/sessions/202609031559-skin-architecture/00-SKINS.md`,
commit `2fe3e37`, 2026-09-03) ended with one sentence:

> "**If the estate does one thing from this document, it should be changing those
> four return shapes to data**... That is smaller than any skin and unblocks all
> of them."

Two days later, in the live cartridge `202609050301-sld-sandbox-v9-8.js`, all four
still return markup:

| function | line | still returns |
|---|---|---|
| `corridorBeside` | 1902 | `''` / HTML |
| `nearestScope` | 2112 | `''` / HTML |
| `declaredBlockHtml` | 2135 | `''` / HTML |
| `caveatHtml` | 3432 | `` return `<div class="neon-caveat">` `` |

The measurement is data; the sentences that make it honest are markup. Nothing has
changed.

### 3.6 · A GitLab mirror so the work outlives the domains

> "possibly a without domain version served on github and gitlabs mirror **so that
> my work outlives me** and if i stopped paying the domain names, the work carries
> on" — 2026-09-04T22:44Z

No mirror exists. No repository has a GitLab remote, and nothing in the seven days
of commits mentions one.

### 3.7 · The Pipeline News homepage pointer

Named openly by Lane B on this board tonight and still true at the time of
writing: `globalgrid2050/index.html` reached only `202609050233` while
`pipelinenews` had built `202609050242` and `202609050304`. This is live work in
flight, not a defect — recorded so the next session knows the lag existed.

## 4 · Open decisions that are his and have never been answered

1. **The domain.** He asked how to move `globalgrid2050.com` to the new
   `globalgrid2050-homepage` repo (2026-09-04T22:23Z), then wrote *"I need to
   understand the website aspect longer, shall I leave it as it is for now?"*
   (22:42Z). No answer is recorded. Meanwhile **both** repos now exist and are
   live: `globalgrid2050-hompage` (misspelled) serves a 200 redirect page to
   `globalgrid2050-homepage`, and the apex domain still serves from
   `globalgrid2050`. Three surfaces, one homepage.
2. **`ventusltd.com` off Yola/Wix to GoDaddy** — stated as intent 2026-09-04T22:44Z,
   not done; the `ventusltd.com` repo has one commit in the window.
3. **The array/inverter design ratio** — recorded as open since 2026-09-01 and
   never closed.
4. **Whether "discontinue all current versions" and restore V8 was ever meant.**
   A subagent refused it on 2026-09-04T13:37Z as a one-way product decision. It has
   neither been confirmed nor withdrawn.
5. **What "tested" means.** He set the bar himself — *"What counts as tested is if
   at least two agents on different browsers clicked and checked that it fucking
   works"* (2026-09-03T20:11Z). No promotion in the week records two browsers.

## 5 · Tangents dropped, and whether dropping them was right

- **Road/rail-aware cable routing** ("a way to design v2 where the substations
  lines dont compute straight line but via the nearest road path like a satnav
  travelling between coordinates, and programmed to avoid railways?",
  2026-09-02T23:34Z). A gated study answered it on evidence: routed median
  absolute error **20.3%** against a gate of <15%, and routing beat the straight
  line on **52.6% of all 95 circuits** against a gate of ≥80%. Verdict: do not
  build. **Dropped deliberately, with numbers.** The right outcome — but it is
  recorded in a session log, not in the product, and he has asked adjacent
  questions since.
- **Local llama/Ollama inference on the GPU** — measured (108–119 tok/s on a 4B
  model, 95–97% GPU), then removed 2026-09-04 after it took the laptop's RAM.
  Deliberate.
- **Google Antigravity / Gemini as a third lane** — ran out of quota
  2026-09-03T01:01Z; dropped with feeling.

---

# PART TWO — THE FLAWS

Every one names a file, a commit, a run or a URL.

## F1 · Four exact-commit gates now fail on a calendar boundary, not on a commit

**Where.** `Ventusltd/globalgrid2050` — `V9.5.1`, `V9.6.1`, `V9.6.2`, `V9.7 Exact
Commit Validation`.

**Evidence.** Read from run `33940365683` (V9.5.1) and `33940365649` (V9.7) at head
`9a1cd023`, step *"Run V9.x committed-byte gate"*. Both print the same diff against
`dist/major_project_news_v9_5_1.json`:

```
-      "confidence": 91          -          "recency": 10          -        "runner_up_score": 91
+      "confidence": 89          +          "recency": 8           +        "runner_up_score": 89
```

**Cause, exactly.** `scripts/major_project_news_v6.py`:

```
612:        age_days = max(0, (datetime.now(timezone.utc) - story["published"]).days)
615:    components["recency"] = 10 if age_days <= 14 else 8 if age_days <= 30 else 5 if age_days <= 90 else 2
```

The committed fixture carries `"updated": "2026-08-22T20:45:25Z"` and the story is
`published: 2026-08-21`. It was one day old when frozen, so `recency` was 10.

**The date arithmetic is visible in the run history.** All four were **green at
`5260db10`, 2026-09-04T22:37:11Z** and **red at `a4faffc1`, 2026-09-05T01:39:00Z**,
and have failed on every push since. Those two runs bracket the instant
`age_days` crossed 14→15. Five reds; no commit between them touched the fixture.

**It will get worse on two known dates, and nobody is watching for them.**

| from | `age_days` | `recency` | `confidence` (same −2/step delta, inferred) |
|---|---|---|---|
| 2026-09-05 | 15 | 8 | 89 — **now** |
| **2026-09-20** | 31 | **5** | 86 |
| **2026-11-19** | 91 | **2** | 83 |

Re-freezing the fixture today buys 15 days. The gate needs a frozen clock, not a
new fixture.

*(V9.3, V9.4 and V9.5 are a separate matter: V9.5 went red once at `a4faffc1` and
recovered on the next commit. Only the four above are time-driven.)*

## F2 · A gate that outlived the thing it gates — `Verify published versions are reachable`

**Where.** `Ventusltd/globalgrid2050` → `verify-published-versions.yml`, red on
**nine consecutive runs** since `5260db10` (2026-09-04T22:37Z), including the head
commit. Run `33940365678`, step *"Test fail-closed publication rules"*: **17 tests,
12 failures, 1 error.**

**Two distinct decay classes in one file**, `scripts/test_verify_published_versions.py`:

1. **Hard-coded generation stamps.** `self.assertEqual("202609040144", published[-1])`
   at line 25 — the run reports `'202609040144' != '202609050233'`. The file pins
   **14 distinct 12-digit stamps** and the whole Grid Atlas identity chain
   `v9.99 → v9.106` at lines 159–199. The live Atlas is at **v9.119**
   (`generation 202609050249`, read from `atlas/current.json`). Every new version
   published makes this test more wrong.
2. **It asserts a structure that was deliberately removed three hours ago.**
   Twelve of the failures are `['the homepage has no Grid Atlas version catalogue
   block']`. That is correct: commit **`a4faffc1`** (2026-09-05T01:38:56Z, "the
   front page shows only what is being built now") rewrote `index.html` from
   **111,836 bytes / 353 lines** to **30,736 bytes / 293 lines** and, in the same
   commit, retired `catalogue-gridatlas-v9.yml` to `.disabled` and cut a proper
   snapshot (`homepage_versions/homepage_v036.html`). The producer was retired
   honestly; **its consumer check was left enabled and now fails forever.**

Measured on HEAD `9a1cd023` and confirmed byte-identical to the live page
(`sha256 3af0fcdbc7fb751b8fc31a04090e8d6aceed78373c79d1bc92672ab21794329b` for
both `git show HEAD:index.html` and `curl https://globalgrid2050.com/`):

| probe | count in the served homepage |
|---|---|
| `GRIDATLAS_V9_AUTOMATION_START` | **0** |
| `GRIDATLAS_V9_AUTOMATION_END` | **0** |
| `UK Grid Atlas V8` (the sentinel) | **0** |
| `data_gridatlas_release` | **0** |

**Consequence to state plainly.** `CLAUDE.md` records that
`scripts/catalogue_gridatlas_v9.py` fails closed unless the V8 sentinel and both
markers survive verbatim, and that `compile_root()` was rebuilt on 2026-09-04
(`5efdc5ef`) to identify the governed row **structurally by those two markers**.
Both markers are gone from the served bytes. That fix is now unreachable, and
`MARKER_START/MARKER_END` at `scripts/catalogue_gridatlas_v9.py:42-43` have nothing
to bind to. The workflow was disabled in the same commit, so nothing is currently
corrupting anything — but **the twenty fail-closed cases pinned in
`scripts/test_catalogue_gridatlas_v9.py` now guard a contract the product no
longer carries**, and the day someone re-enables that workflow it will meet an
input it has never seen.

## F3 · The sizing double-count is live, in five byte-identical copies

**Where.** `Ventusltd/globalgrid2050`, line 147 of each:

```
solar-bess-topology-v5/gis-sld-v5-calculations.js
solar-bess-topology-v6/gis-sld-financial-sandbox/gis-sld-v5-calculations.js
solar-bess-topology-v7/gis-sld-financial-sandbox/gis-sld-v5-calculations.js
solar-bess-topology-v8/bess-gis-sld-financial-sandbox/gis-sld-v5-calculations.js
solar-bess-topology-v8/bess-pcs-standalone/gis-sld-v5-calculations.js
```

All five carry the identical three lines:

```
144:    const total_blocks = inv_per_mv * mv_per_ring * rings;
147:    const ac_mw_direct = total_blocks * central_skid_mva * inv_per_mv;
148:    const production_substation_ac_mva = central_skid_mva * inv_per_mv;
```

`inv_per_mv` is already inside `total_blocks`; multiplying by it again at line 147
double-counts. The same file also **defines `ac_mw_direct` twice** — line 111
without the extra factor, line 147 with it.

**It is served, not merely committed.** `curl` against
`https://globalgrid2050.com/solar-bess-topology-v7/gis-sld-financial-sandbox/gis-sld-v5-calculations.js`
returns **HTTP 200, 8,674 bytes**, and line 147 of the served bytes is the buggy
form. Same for v6. This is the page Vikram opened himself on 2026-08-31T19:38Z.

**The correction already exists and none of the five imports it.**
`gridatlas/atlas/modules/202609012205-sizing-arithmetic.js` computes
`Math.min(inverter_ac_total, skid_ac_total)`. `ventus-grid-engine/genome/engine-graph.json`
records the worked numbers: shipped defaults give **211.2 MW**; the corrected
computation gives **min(105.6, 52.8) = 52.8 MW**. *(The brief's "105.6 is real"
names the inverter total; the graph's own evidence says the binding constraint is
the skid total, 52.8. Worth resolving before either number is quoted at a client.)*

## F4 · The engine graph: 31 of 44 nodes are fragments; 7 have measurably diverged

**Where.** `Ventusltd/ventus-grid-engine` → `genome/engine-graph.json`, rendered at
https://ventusltd.github.io/ventus-grid-engine/?graph=engine-graph

44 nodes: **31 `fragment`**, 11 `canonical`, 1 `extract`, 1 `reference`.
51 edges: `duplicates` 18 · `supersedes` 13 · `should_import` 10 · `drifts_from` 7 ·
`imports` **3**. RAG: 24 green, 9 amber, **7 red**.

**The seven `drifts_from` edges — copies that no longer agree with their original:**

| fragment | drifts from | how |
|---|---|---|
| `solar-bess-topology-v5/…-calculations.js:147` | `202609012205-sizing-arithmetic.js` | F3 |
| `…v6/…:147` | same | F3 |
| `…v7/…:147` | same | F3 |
| `…v8/bess-gis-sld-financial-sandbox/…:147` | same | F3 |
| `…v8/bess-pcs-standalone/…:147` | same | F3 |
| `202609041330-substation-intelligence-v9-63.js:6083-6092` inline `nearest()` | `atlas/modules/202609011950-substation-lookup.js:57-70` | `options?.limit ?? 1` vs `(options && options.limit) \|\| 1` disagree at `limit: 0`; the **live** copy lacks the `voltages_kv \|\| []` default and **can throw where the module cannot** |
| `202609040229-place-global-search-arrival-identity.js:604` `receiveExactRepdDeepLink()` | `pipelinenews/…/atlas-pointer-deep-link.mjs:161` `buildAtlasV9DeepLink()` | receiver regex `/^[A-Za-z0-9-]{1,40}$/` vs emitter `/^\d+$/` — **the receiver silently accepts identities the live emitter would never send** |

The last two are live and shipping. Note the shape of the whole graph: **10
`should_import` edges against 3 `imports`.** The engine repository currently
*documents* the duplication rather than removing it — which was the point of
creating it on 2026-09-04, and is not yet done.

## F5 · 175 dead routes and 9 dead-and-shipped sentinels, recorded where nobody reads

**Where.** `claude/docs/boards/estate-link-crawl.md`, written by
`202609032340-estate-link-crawl.yml`, crawled **2026-09-04T07:24:25Z**.

```
releases crawled: 79 (35 whose page did not answer)
routes checked: 1094, dead: 175
sentinels checked: 38, dead: 9, dead AND shipped: 9
```

The board's own definition: *"A dead sentinel that is shipped is what a user gets
when they click."* All nine are on `pipelinenews-releases`, and all nine are the
pre-move Atlas path:

```
404  https://ventusltd.github.io/gridatlas/202608300453-atlas-v9/
404  https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=13599
404  …?repd_ref=16135 · 17494 · 12453 · 2484 · 12780 · 2535 · 13429
```

These are the same **"consumer left pointing at a producer that reorganised"**
404 deep links Vikram was told about on 2026-08-30 and called *"the single most
important"* vaccine. The path moved under `/atlas/`; six days later they are still
404.

**Why nobody knows.** The workflow says so in its own comment: *"nothing here can
go red, so this cannot become a recurring failure notification"* and *"the crawl
exits 0 on every finding, so a dead link is recorded here rather than mailed to
anyone."* That was a deliberate, defensible choice against the estate's earlier
email storm. But **the board has been committed exactly twice** (`d571709`,
`f188de3`) and nothing in the three lanes running tonight references it. A green
tick in the Actions list is the only signal anyone sees, and it means nothing about
the estate.

## F6 · The estate's own ordering mechanism is wrong on 60% of stamped commits

The 12-digit generation stamp is what every release name, ledger, pointer and
version number in this estate is ordered by. Measured over the seven days, every
commit whose subject carries a 12-digit stamp, compared to that commit's own UTC
author time from the API:

| relation of stamp to commit time | commits | share |
|---|---|---|
| ahead 1–55 min | 1,523 | 35.6% |
| **honest** (0 to 15 min behind) | 1,506 | 35.2% |
| **exactly +1 h (55–65 min) — the BST signature** | **646** | **15.1%** |
| ahead >65 min | 398 | 9.3% |
| behind 15–120 min | 151 | 3.5% |
| behind >120 min (replayed / backdated) | 60 | 1.4% |
| **total stamped** | **4,284** | |

**2,567 of 4,284 (59.9%) carry a stamp in their own future.** A stamp taken from
`date -u` at commit time can only ever be at or slightly behind the commit; a stamp
ahead of it means the clock was BST, or the number was chosen. The +1 h signature
by repository: gridatlas 288 · chatgpt-audits 255 · pipelinenews 64 ·
globalgrid2050 21 · companies 7 · data-grid-gb 4 · claude 3 · data-gridatlas 3 ·
ventus-grid-engine 1.

This matches, and quantifies over a week, the genome spider's 2026-09-04 finding
that the mechanism is wrong on all 8 repositories it tested. `claude` is the
cleanest at 253 of 274 honest — the mechanism works where it is installed, and it
is installed almost nowhere.

## F7 · A scheduled workflow failing since 2026-09-03, on the exact thing he keeps asking for

`Ventusltd/data-gridatlas` → `202608301931 Layer fidelity, V8 origin vs V9
delivery`. Last **scheduled** run: **failure, 2026-09-04T08:04:45Z**, head
`8bf88da9`. It has failed at head since 2026-09-03. It is on a schedule, so it will
keep failing, and it is the instrument that would tell anyone whether §3.2 —
"bring the v8 layers back" — had been done.

Also on that repository: `Hourly watchdog` exists as **six separate workflows, each
named after a commit SHA**, four of them ending in failure. `pipelinenews` carries
**33 workflows**, of which 17 have a failing latest run and most are one-shot
workflows named after the commit that created them (`Repair immutable timestamp
Pages gate from 9b6f05cff946`, `PipelineNews exact Atlas successor 10 from
609b841e9592`, …), all last run on 2026-08-30. **The Actions tab of these
repositories is a graveyard, and a real red is indistinguishable from a fossil.**
This is `cvaa`'s own `no-per-release-workflows` rule, failing where it was written.

## F8 · Two homepage repositories, one letter apart, both live

`globalgrid2050-homepage` and `globalgrid2050-hompage` were both created and pushed
within **41 seconds** of each other on 2026-09-04 (`816a728b` at 22:32:56Z,
`e0c3de9b` at 22:33:37Z). Both serve HTTP 200 from GitHub Pages; the misspelled one
serves a `<meta http-equiv="refresh">` redirect and is honestly labelled *"Moved"*.
The misspelled repo also carries a failing workflow (`GridBot Federation Systems
Map`, failure 2026-09-02T11:43:38Z). With the apex domain still served from
`globalgrid2050`, there are now three homepage surfaces and the decision at §4.1 is
still open.

## F9 · 187 commits on 53 branches that never merged

The full table is in `scratchpad/sweep2.json`. The ones that carry product intent:

| repo | branch | commits | window | state |
|---|---|---|---|---|
| gridatlas | `codex/20260904-gridatlas-30x` | **41** | 2026-09-03 23:17–23:55 | 19 behind main, never evaluated (§3.3) |
| gridatlas | `candidate/20260905-ci-refinement` | 6 | to 2026-09-05 01:42 | in flight tonight |
| gridatlas | `candidate/promotion-lane` | 5 | 2026-09-04 22:34 | built and proven, not promoted |
| gridatlas | `candidate/v9.117-menu-contiguous` | 1 | 2026-09-04 22:10 | "proven, not cut, per the review" |
| gridatlas | `codex/202609030251-grid-data-v9-89` | 9 | 2026-09-03 | superseded |
| pipelinenews | `codex/202609012115-board-continuity` | 5 | 2026-09-01 | never merged |
| claude | `codex/20260904-overnight-governor` | 2 | to 2026-09-04 12:42 | **"six UI defects measured in Chrome, two artefacts disproved"** — measurements sitting on a branch |
| chatgpt-audits | 25 `audit/*` branches | 41 | 2026-08-31 | every subject begins `UNREVIEWED` |

`globalgrid2050` additionally carries **42 branches**, eleven of them `copilot/*`
from April 2026, each 3,300–3,400 commits behind `main`.

## F10 · The identity that travels and the measurement that does not

Recorded in `claude/sessions/202609031759-identity-leak/00-FINDING.md` (`faddebd`)
and fixed in the Atlas at v9.91 (`65786ae`, 2026-09-03) — noted here because the
**general shape recurred four days later on a different surface** and is worth
carrying as a class, not an incident:

> a card whose identity block and measurement block are computed from different
> sources will, at some point, print a real project's name, REPD reference and
> planning status above a measurement to a substation in another county.

The Atlas fix bound them by construction. The equivalent binding does not exist on
the pages that carry F3's sizing arithmetic — those five sandboxes print a
capacity figure with no identity binding at all.

---

## 6 · What I could not verify, and what would settle it

- **Whether the Pipeline News 404 sentinels (F5) are reachable from a link a
  reader would actually click today**, or only from archived releases. The crawl
  proves the URL 404s; it does not prove a live surface still emits it. Settled by:
  grep the served bytes of the newest Pipeline News release for
  `github.io/gridatlas/2026` without `/atlas/`.
- **Whether the four exact-commit gates (F1) would go green on a re-frozen
  fixture**, or whether a second time-dependent value is behind the first. The
  logs show the diff truncated at the second hunk. Settled by: `git stash` nothing —
  run `bash uk_renewables_pipeline/v9.5.1/tests/run_v9_5_1.sh` in a clean clone and
  read the whole diff.
- **The 211.2 / 105.6 / 52.8 disagreement in F3.** The brief and the engine graph
  name different corrected values. Settled by: executing both functions on the
  shipped defaults and printing all three intermediate totals.
- **globalgrid2050, gridatlas and pipelinenews were all being written to while I
  measured them.** gridatlas moved `3061dfcc` → `5c013cd` (v9.120) during this
  session; globalgrid2050 took four commits. Everything above is measured against a
  named commit or a clean clone, and where it is a working tree I have said so.
  `globalgrid2050` had 2 uncommitted paths when I read it, both another lane's.

## 7 · Corrections against myself

1. The pagination bug in §0 — reported and fixed before it reached a finding.
2. `bash claude/scripts/gh-api.sh "/user/repos"` returns 404. The leading slash
   makes `https://api.github.com//user/repos`. Pass paths **without** a leading
   slash. Worth adding to the script's usage block.
3. `Ventusltd` is a **user account, not an organisation** — `orgs/Ventusltd/repos`
   returns 404 and `user/repos` is the correct enumeration.
4. Windows `python` cannot open `/c/Users/...`. Bash writes there happily and the
   read then fails with `FileNotFoundError` on a file that exists. Use `C:/Users/...`
   for anything handed to `python`, `/c/Users/...` for bash — in the same script.
