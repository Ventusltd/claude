# Build queue — the next ten versions

Written 2026-09-03, 10:26–11:10 UTC. Every number below was re-derived in this session against a
named commit; nothing is carried over from the handover on trust. Where the handover's number and
mine disagree, **mine is stated and the handover's is named as corrected** — four of them were
wrong, and the corrections are in §Corrections at the foot.

Rulers used, so a later session can tell whether the ground moved:

| repo | ref measured | when |
|---|---|---|
| gridatlas | `ed2135fffd8a82deaa883515dbae137eac3f0f71` (= origin/main) | 10:28Z |
| globalgrid2050 | `a0f93e875717e7de71ed5664f0098b9b59a9df89` (= origin/main) | 10:28Z |
| pipelinenews | `cdb8fe99f2b0e70b4c8afde13e2d92123bf7df42` (= origin/main) | 10:28Z |
| data-gridatlas | `8bf88da9e210ce9f61dc0398869d3369f3fa2445` (= origin/main) | 10:28Z |
| data-grid-gb | `5181de3423e4fe50c77c568b9f3066c61a1d9e41` (= origin/main) | 10:28Z |
| cvaa | `150ca228153c96a59f6b074692420a9d5353f1e8` (= origin/main) | 10:34Z |

The local worktrees of **data-grid-gb** and **cvaa** are on Codex feature branches and behind
origin. They were not measured. Measure origin, not the folder.

CI, read authenticated, latest run **per workflow file** on each repo's own default branch:

| repo | red workflows at head |
|---|---|
| gridatlas | none — 4 of 4 green |
| globalgrid2050 | `v9-7-validate.yml`, `verify-published-versions.yml` |
| pipelinenews | `pages.yml` |
| data-gridatlas | `202608301931-layer-fidelity.yml` |
| data-grid-gb | none |
| cvaa | none |

---

## The queue

### 1 — globalgrid2050: the news matcher reads the wall clock inside a byte-identity gate

| | |
|---|---|
| **version** | globalgrid2050, next generation stamp (no V-number; this is a producer fix) |
| **finding** | `scripts/major_project_news_v6.py:612` computes `age_days = max(0, (datetime.now(timezone.utc) - story["published"]).days)`; line 615 buckets it `10 if age_days <= 14 else 8 if <= 30 else 5 if <= 90 else 2`. The committed artefact `dist/major_project_news_v9_5_1.json` is therefore a function of the day it is rebuilt, and `uk_renewables_pipeline/v9.5.1/tests/run_v9_5_1.sh:17` asserts `git diff --exit-code` on exactly that file. **Measured by simulation in a throwaway clone at `a0f93e87`, changing nothing but the clock:** at +0 and +1 days the artefact reproduces byte for byte; at **+2 days (2026-09-05) six lines change** and the digest moves `e6c42cd886bb340ca4d9887954cd090adfcc22bbf59621289bb48ae548ff5b8b` → `4800ecf7b88f1cc68ceb4ff2ef81aee32f79bcb4133d3f4bde1c959fcdd95cdd`. Distribution of the 86 distinct `published` dates across the four buckets today: `{2: 52, 5: 25, 8: 7, 10: 2}`. **This already happened once:** `v9-7-validate` was red on runs 15–39 (2026-08-29T05:56:37Z → 2026-09-02T06:04:28Z, 25 consecutive). I read the logs of the **first and last** of those two — runs 15 and 39 — and both fail with precisely this diff: `recency 10→8`, `recency 5→2`, `confidence 85→83`, `67→64`. Runs 16–38 are inferred from those two endpoints and are **not individually read**. Commit `77e4eeaf` at 2026-09-02T06:13:43Z cleared it by re-committing the decayed values rather than removing the clock. |
| **owning file** | `scripts/major_project_news_v6.py` — one expression, line 612 |
| **change class** | module (producer). **No full review.** The blast radius is bounded by an existing byte-identity assertion: if the artefact's digest is unchanged, nothing downstream can have moved. |
| **cut or decision** | **CUT.** Freeze `age_days` against a committed as-of date instead of `datetime.now()`. The as-of value is not a free choice: any date in **2026-09-02 … 2026-09-04** reproduces the currently committed bytes exactly (measured), so the fix is provable at zero byte cost. |
| **gate** | `v9-5-1-validate.yml` and `v9-7-validate.yml` — the runner's `conclusion` for the pushed SHA, polled from `repos/Ventusltd/globalgrid2050/actions/workflows/<file>/runs?branch=main`. **Plus a negative control that the estate's own rules demand:** re-run the builder with the simulated clock advanced 30 days and require the artefact to be byte-identical. A fix that only passes today is the same defect with a fresh date. |
| **acceptance** | `sha256(dist/major_project_news_v9_5_1.json)` is still `e6c42cd8…` after a rebuild, and stays `e6c42cd8…` after a rebuild with the clock advanced. |
| **blocked by** | nothing |

> **This item has a deadline, which is why it is first.** On 2026-09-05 the artefact stops
> reproducing on its own and reds `v9-5-1`, `v9-6-1`, `v9-6-2` and `v9-7` validate — all four run
> `run_v9_5_1.sh` through the chain. Item 2 is worthless if this is not done first: the manifest
> would be regenerated against an input that changes again 48 hours later.

---

### 2 — globalgrid2050: `regional_manifest.json` does not reproduce from its own inputs

| | |
|---|---|
| **version** | globalgrid2050, next generation stamp (same lane as item 1, separate cut) |
| **finding** | `v9-7-validate.yml` has failed **8 consecutive runs** (run 40 at 2026-09-02T06:13:47Z through run 47 at 2026-09-03T03:17:38Z, head `a0f93e87`). Read from the runner's log, the failing step is `Run V9.7 committed-byte gate`, and the whole diff is **one line**: `input_sha256` committed `cea104c3e9cfc07971680afdf5f64073e1d4825b63bfaf4e969266df8386ebbd` against rebuilt `e6c42cd886bb340ca4d9887954cd090adfcc22bbf59621289bb48ae548ff5b8b`. The other four hashes in the block — `source_contract_sha256`, `module_registry_sha256`, `regional_news_sha256`, `decision_ledger_sha256` — all match, so the derived output has not changed; only the record of the input is stale. `e6c42cd8…` is the sha256 of the current committed `dist/major_project_news_v9_5_1.json` (406,510 bytes) — I re-derived it from both the blob and the worktree and they agree. The input last moved at `77e4eeaf`; the manifest last moved at `39e5b5a2` on 2026-08-24. |
| **owning file** | `uk_renewables_pipeline/v9.7/data/v9.7/regional_manifest.json` — regenerated, not hand-edited, by `uk_renewables_pipeline/v9.7/scripts/build/regional-news-v9-7.mjs:40` |
| **change class** | data (derived artefact). **No review** — the file is machine-written and the gate that rejects it is the same gate that regenerates it. |
| **cut or decision** | **CUT** |
| **gate** | `v9-7-validate.yml` conclusion `success` for the pushed SHA |
| **acceptance** | `node uk_renewables_pipeline/v9.7/scripts/build/regional-news-v9-7.mjs` followed by `git diff --exit-code -- uk_renewables_pipeline/v9.7/data/v9.7` exits 0 on the runner, and `globalgrid2050` drops from two red workflows to one |
| **blocked by** | **1** |

---

### 3 — gridatlas: the proof restates the pin instead of reading it

| | |
|---|---|
| **version** | gridatlas **v9.89** |
| **finding** | `atlas/modules/202609030137-pinned-products.js` is the module that owns the runtime data pins — three products at lines 53–76, each with a 40-char ref, a SHA-256 and a byte length. The composed cartridge is fine: `tools/build-cartridge.mjs` **inlines the module verbatim** (verified — the 1,032-byte `const PINS` block appears byte-identical inside `atlas/cartridges/202609030234-substation-intelligence-v9-63.js`), so the cartridge is derived and needs no edit. But `tools/proofs/202609030234-substation-intelligence.proof.mjs` **hard-codes the literal ref twice** — at line 402 (`pins.url('connection-points.v3') === 'https://raw.githubusercontent.com/Ventusltd/data-grid-gb/1c9909d1138704b29235c27fd769436dda8a0b18/derived/connection-points.v3.json'`) and at line 438 (`api.product_pin.ref === '1c9909d1138704b29235c27fd769436dda8a0b18'`). **So moving one pin is two files, and the module does not own what it declares.** The proof runs 97 checks, 97/97 passing at `ed2135f` (I executed it). |
| **owning file** | `tools/proofs/202609030234-substation-intelligence.proof.mjs` — lines 399–402 and 436–439 |
| **change class** | proof. **No cartridge, module or part changes.** No full review. |
| **cut or decision** | **CUT.** Replace the two 40-char literals with structural assertions against the module's own declaration — that the URL is composed from `pins.pin(id).ref` and the path (so a branch name can never appear where a commit belongs), and that `api.product_pin.ref` equals the ref the loaded module declares. The identity of the bytes is already asserted where it belongs, by digest, at build time and again in the browser. |
| **gate** | `.github/workflows/202608312212-cartridge-proof.yml`, conclusion `success` for the pushed SHA. The proof must still be **capable of failing**: prove it by running it once against a module whose `ref` is a branch name and confirming a red, before shipping. A check built only from cases the code already passes cannot fail. |
| **acceptance** | 97/97 (or the new total) on the runner, and `grep -c '1c9909d1138704b29235c27fd769436dda8a0b18' tools/proofs/202609030234-substation-intelligence.proof.mjs` returns 0 |
| **blocked by** | nothing. **Unblocks 4** — after this, a pin move is one file. |

---

### 4 — gridatlas: move the data-grid-gb pin to `5181de3`, and pay 13 locations for 484 transformer counts

| | |
|---|---|
| **version** | gridatlas **v9.90** |
| **finding** | The Atlas currently pins **`1c9909d1138704b29235c27fd769436dda8a0b18`** for both data-grid-gb products (`pinned-products.js:55` and `:63`). *(The handover said `b91e45b`; it does not appear as a pin anywhere in gridatlas — corrected.)* Comparing the pinned commit with origin/main `5181de3` in `derived/connection-points.v3.json`, measured from the blobs: **886 site codes on both sides, none added, none removed**; **`transformers` changes on 484 of 886 sites, total 2,920 → 1,526**; the declared `counts.with_location` moves **502 → 489 — thirteen sites lose a location**, and the `location` field differs on 16 records; a new `join_context_key` field appears on all 886, and no existing key changes. In `derived/gb-transmission-network.v1.json` the content changes at **identical byte length, 10,069,966 either side** (`fc331cc2…` → `b26b324c…`) — only the digest catches it. |
| **owning file** | `atlas/modules/202609030137-pinned-products.js` — lines 55/57/58 and 63/65/66 (ref, sha256, bytes for each of the two products). One file **after item 3**; two files before it. |
| **change class** | module. Then `tools/build-cartridge.mjs` recomposes the cartridge from it — a rebuild, not a second edit. No full review. |
| **cut or decision** | **DECISION.** The question, stated so it can be answered in one line: **is losing a location on 13 of 502 located sites an acceptable price for correcting the transformer count on 484 of 886 sites (2,920 → 1,526), or should the pin wait for a data-grid-gb release that keeps both?** There is no technical answer to this; it is a judgement about which number the map is more often wrong about. Do not queue it as a cut — the loss is real and the map currently shows those 13. |
| **gate** | cartridge proof conclusion `success`, then the live composition's `product_pin.state` reading `verified` against the new digest in the browser |
| **acceptance** | the Atlas reports 1,526 transformers where it reported 2,920, and the 13 named sites are recorded in the cut's message as a known loss rather than discovered later |
| **blocked by** | **3** (so it is one file), and an architect answer |

---

### 5 — pipelinenews: every published page names a release that is not its own

| | |
|---|---|
| **version** | Pipeline News, next generation |
| **finding** | **25 of 25** published directories under `globalgrid2050/pipelinenews_intelligence/` carry `<title>PipelineNews \| Current verified Atlas V9 deep-link successor 202608300309</title>` — every publication from `202608311343` to `202609030009`. **Zero published pages state their own generation.** Verified live: `curl https://globalgrid2050.com/pipelinenews_intelligence/202609030009/` returns that title. *(The handover said "all seven recent generations"; the real figure is 25 of 25 — corrected.)* The mechanism: `tools/intelligence/release_builder.py:409` does `shutil.copytree(parent, target)` and line 500 does `apply_once(idx, "<title>", "<title>", "title tag present", …)` — it asserts a title tag **exists** and never rewrites its stamp, so the string is carried forward from a 30 August parent. The only non-release file in the repository containing that sentence is `orchestration/202608300309-build-current-atlas-link-successor.py`, which interpolates `{args.generation}` and has not run since. |
| **owning file** | `tools/intelligence/release_builder.py` — the index.html section, lines 491–501 |
| **change class** | module (release builder). No review. Released bytes are immutable and are **not** touched; this changes what the next release is built with. |
| **cut or decision** | **CUT** |
| **gate** | **Not `pages.yml`** — that is red for item 6's reason and is not the publication route. Publication is globalgrid2050 copying `releases/<id>-pipelinenews` byte for byte. The gate is a new assertion inside the builder itself — *the title names the release being built* — which fails on the current parent and passes on the new one, plus the served page after the globalgrid2050 publish. |
| **acceptance** | `curl https://globalgrid2050.com/pipelinenews_intelligence/<new-id>/ \| grep -o '<title>[^<]*</title>'` names `<new-id>`, not `202608300309` |
| **blocked by** | nothing |

---

### 6 — pipelinenews: the deploy gate has no branch for the format 30 of 32 releases use

| | |
|---|---|
| **version** | Pipeline News — no version until the question is answered |
| **finding** | Counted from the **committed blobs**, not the working tree (which holds untracked candidates): 32 `releases/*/release-manifest.json` — **30 carry `pipelinenews.additive-cartridge-release.v1`**, 1 carries `pipelinenews.current-atlas-link-release.v2`, 1 carries `pipelinenews.timestamp-folder-successor.v1`. `pages.yml` has **27 consecutive failures**; the last success was run 35 at **2026-08-30T11:13:37Z** at `a30b9e45`. *(The handover said "dead since 31 Aug"; the last green was 30 Aug — corrected.)* I re-ran `pn_walls.py` against a clean clone at `cdb8fe99`: for `202609030009-pipelinenews`, **13 assertions fail** in order — timestamp release schema, build schema, manifest generation, manifest release ID, not immutable, classification, entrypoint not folder-local index.html, public URL, pointer state in immutable bytes, immutable release encodes transient pointer state, identity-routing contract, functional output list missing, output list missing — then `TypeError: object of type 'NoneType' has no len()`, so everything past 13 is **unmeasured, not passing**. The control holds: the same harness against `202608300309-pipelinenews` (the one v2-schema release) runs to completion with **zero** failed assertions, so the thirteen are properties of the newer format and not of my instrument. |
| **owning file** | `atman/202608262014-build-pages.py` — a new `validate_additive_cartridge_v1()` beside `validate_current_atlas_link_v2` (line 399), dispatched at line 650 where the v2 branch is already dispatched. The constant at line 52 and the `require` at line 664 stay as they are. **One file, one new function** — the shape already exists in the code. |
| **change class** | module (deploy gate). **A full review of that one function is required** — each of the thirteen is somebody's deliberate guarantee about an immutable release. |
| **cut or decision** | **DECISION, and not disguisable as a cut.** Editing the line-52 constant clears assertion 1 and exposes eleven more; it is not a rename. The question: **of the thirteen guarantees, which still bind `additive-cartridge-release.v1`?** Answer it as thirteen yes/no answers, not as a principle — that is what makes it one sitting's work rather than a design exercise. |
| **gate** | `pages.yml` conclusion `success` for the pushed SHA, which would be its first green since 2026-08-30 |
| **acceptance** | `pn_walls.py` against the same release reports **no assertion failed and the validator ran to completion**, the same sentence the v2 control already produces |
| **blocked by** | nothing technical; blocked on the architect's thirteen answers |

---

### 7 — data-gridatlas: the layer harness reports a swallowed timeout as a healthy layer

| | |
|---|---|
| **version** | data-gridatlas, next generation |
| **finding** | `202608301931-layer-fidelity.yml` has failed on **all six runs it has ever had** — run 1 at 2026-08-30T17:56:57Z through run 6 at 2026-09-03T08:09:44Z. **It has never been green.** *(The handover called it "red since 08:09Z today"; 08:09Z is merely its most recent run — corrected.)* The `offline` job **passes** — 40 unique source URLs across 60 layers, all fidelity checks good — so the data is not the problem. The `browser` job fails. Its table has **60 rows: 35 PASS, 25 FAIL** *(not "50 of 120"; that is the same thing counted as two checks per layer — I am reporting the rows I counted)*. The predicate is line 368: `bad = !label.includes('[OK]') \|\| !loaded \|\| seconds > 15 \|\| heapMb > 400 \|\| features < 1`. Broken down: **17 rows exceed the 15 s budget** — 15 at 60.3 s and 2 at 60.4 s, i.e. all of them parked on the harness's own `{ timeout: 60000 }`; **5 rows return zero features** — `11kv`, `ind`, `air`, `metro`, `tram` *(the handover named four and missed `11kv` — corrected)*; **3 rows exceed the 400 MB heap** — `primary_roads` 677, `ev` 587, `motorway_services` 575. **The instrument is the finding.** Line 348's second `waitForFunction(… isSourceLoaded …, { timeout: 60000 })` ends in `.catch(() => {})`, so a timeout is discarded; the `page.evaluate` immediately after then records `loaded: true` for all 17, and records `features: 32775` — **the identical number on all seventeen**, which is a saturated `querySourceFeatures` viewport sample, not a feature count. So the row says a layer loaded successfully in 60.3 seconds with 32,775 features, and at most one of those three claims is a measurement. |
| **owning file** | `.github/workflows/202608301931-layer-fidelity.yml` — the `live.mjs` heredoc, lines 344–370 |
| **change class** | workflow (the measuring instrument only). **No product, cartridge or data change.** Blast radius on consumers is zero and that is enforced, not asserted: the data plane is pinned twice, at build time in `gridatlas/compiler/202608292126-build-map-ready-v9.py` against a commit in `contracts/202608292126-map-ready-runtime.json`, and again at runtime by the cartridge re-hashing the bytes in the browser. |
| **cut or decision** | **CUT.** Make the swallowed timeout a recorded state with its reason instead of a silent `loaded: true`, and record `querySourceFeatures` under a name that says it is a viewport sample. **Do not raise the 15 s budget to make the lane pass** — the budget is a shared promise; make the reading precise and let the number say what it says. |
| **gate** | `202608301931-layer-fidelity.yml` conclusion for the pushed SHA, and the `layer-fidelity-browser-<run>` artefact, whose rows must now distinguish *timed out* from *loaded in 60.3 s* |
| **acceptance** | no row in the artefact reports `loaded: true` for a probe whose readiness wait timed out; the 5 zero-feature layers and the 3 over-heap layers still FAIL, because they are real |
| **blocked by** | nothing |

> The 5 zero-feature layers are **not** fixed by this item and must not be claimed as fixed. This
> item makes the 17 timeout rows legible so the zero-feature five stop being buried under them.
> Their cause is unmeasured; queue the diagnosis after this lands, not before.

---

### 8 — data-grid-gb: the product's key order is not deterministic, so a rebuild forges a data change

| | |
|---|---|
| **version** | data-grid-gb, next `refresh_network_products` generation |
| **finding** | Between `b91e45b` and `5181de3` — consecutive commits on main — `derived/gb-transmission-network.v1.json` changes content at **identical byte length, 10,069,966**, and the **entire diff is a key reordering inside one nested dict**: `"20": 2` moves from before `"132": 2` to after `"25": 2`. Nothing else in the file differs. The writer is `pipelines/build_network_model.py:370-371`: `json.dumps(product, ensure_ascii=False, indent=1)` — **no `sort_keys=True`**. So every refresh can move the digest without moving a single value, and a consumer pinned by SHA-256 sees a change that is not one. This is the same file the estate spent a night celebrating for changing content at identical byte length; that observation stands, but its cause is partly this. |
| **owning file** | `pipelines/build_network_model.py` — line 371, one keyword argument |
| **change class** | data (producer). No review. |
| **cut or decision** | **CUT.** Add `sort_keys=True` to the emit. Note the sibling writer `derived/build_connection_points.py:358` has the same omission and should be done in the same cut **only if a rebuild proves it also reorders** — if it does not, leave it and say so; do not change a line you cannot show is wrong. |
| **gate** | `refresh_network_products.yml` conclusion `success`, plus the proof that matters: build the product **twice** from the same inputs and require the two SHA-256s to be equal. That check does not exist today and should land with the fix. |
| **acceptance** | two consecutive builds from identical inputs produce identical digests; the next refresh's diff contains only values that actually changed |
| **blocked by** | nothing. Do it **before** item 4 if item 4 is approved, so the pin moves to a deterministic artefact. |

---

### 9 — globalgrid2050: the publication-truth gate is holding the flagship repository red

| | |
|---|---|
| **version** | globalgrid2050 — no version until the question is answered |
| **finding** | `verify-published-versions.yml` fails at head `a0f93e87`. Read from the runner's log, verbatim: `PUBLICATION TRUTH: FAIL — the homepage names Grid Atlas v9.86 / 202609030200 as the current verified release while the live composition is v9.88 / 202609030234`. Both halves confirmed independently: `gridatlas/atlas/current.json` declares `generation 202609030234`, `composition_version v9.88`, `composition_id 202609030234-gridatlas-v9.88`; and the data-gridatlas offline job, reading the Atlas from a different direction, reports `gridatlas_generation: 202609030234`. The gate is not broken — it is the verifier working. GridAtlas cut ten versions overnight and the homepage stamp is hand-maintained, so the gap reopens minutes after every cut. |
| **owning file** | **None, and that is the finding.** The stamp is written into `index.html`; the reader is `scripts/verify_published_versions.py`; the compiler that would refresh it, `scripts/catalogue_gridatlas_v9.py`, cannot run on that file because `compile_root()` requires the catalogue URL's entry line to match byte for byte and an `os-strip` banner added on 30 August carries the same href. Three files, three different owners, and the change that closes it depends on which meaning is chosen. |
| **change class** | depends entirely on the answer — part (`index.html` row), proof (`verify_published_versions.py`), or module (`catalogue_gridatlas_v9.py`) |
| **cut or decision** | **DECISION.** The question is unchanged from D1 and it is one word: **does "Current Verified Release" mean the newest release, or the reviewed one?** If *newest*, the stamp must be generated, not typed, and the compiler's byte-exact entry-line requirement has to be repaired first. If *reviewed*, the gate is asserting the wrong invariant and should compare the homepage against a review ledger rather than against `current.json`. Re-stamping by hand buys roughly the time until the next GridAtlas cut and is not an answer. |
| **gate** | `verify-published-versions.yml` conclusion `success` — and it must stay green **through** a subsequent GridAtlas cut, which is the property that distinguishes an answer from a re-stamp |
| **acceptance** | globalgrid2050 has zero red workflows and stays that way across one GridAtlas version |
| **blocked by** | nothing technical; blocked on one word from the architect |

---

### 10 — claude / cvaa: the estate's published immunity numbers were measured against 25 of 27 rules, on working trees

| | |
|---|---|
| **version** | `claude`, next session entry — a re-measurement, not a build |
| **finding** | Two defects in the instrument that produces the numbers everyone quotes. **First, coverage:** cvaa `origin/main` at `150ca228` carries **27 vaccine files and 27 `vaccines.lock` entries**, but `sessions/202609030120-cicd-spider/census-members.json` (committed `28849c01`, 2026-09-03T06:27:32+01:00) measures **34 repos × 25 rules**. `no-expiry-windows` is superseded, and `memory-store-complete` (generation 202609031019) landed after the census ran — so **no repository in this estate has ever been measured against rule 27**, and the widely quoted "16 of 34 immune" is 25-rule immunity being reported as immunity. **Second, provenance:** `census.sh:26` measures the 18 canonical repos as **working trees** under `OneDrive/Documents/GitHub/$d`; only the 16 cold repos are freshly cloned. That is *measure the artefact, never the workspace* broken by the census that publishes the estate's numbers — and it is the exact failure that put `cvaa`'s own drift row into the handover wrong. The per-rule counts I did re-derive from the committed census and they hold: `monotonic-utc-generations` **14 fail / 20 immune**, `chaining-token` **12 / 22**, `self-terminating-loops` **7 / 27**, `no-time-based-gates` **3 fail** — `companies`, `globalgrid2050`, `pipelinenews`. |
| **owning file** | `sessions/202609030120-cicd-spider/census.sh` — line 26 for the clone, and the ruler pin for the rule set |
| **change class** | proof / tooling. No review. |
| **cut or decision** | **CUT.** Point every repo at a clean clone of its own `origin/main`, pin the ruler at `150ca228`, re-run, and publish the denominator as **34 × 27** with the previous **34 × 25** named as superseded. If a count moves, the movement is the finding; if none moves, the census has earned its numbers for the first time. |
| **gate** | the re-run's own output, with `census-members.json` recording the ruler SHA and the rule count in the file rather than in prose around it |
| **acceptance** | the committed census states 27 rules and 34 repos, every repo row cites a clean-clone SHA, and any repo whose state changed between working tree and clone is listed by name |
| **blocked by** | nothing |

---

## Cuts, decisions, and the ratio

**Seven cuts, three decisions.**

**Executable now, without the architect — 1, 2, 3, 5, 7, 8, 10.** Every one is already diagnosed
to a line number, routes to a single file, and is proved by a check that already exists on a
runner. A fresh session can open item 1 and start editing; there is no investigation left in any
of the seven. Two of them have hard sequencing: **2 waits on 1** (regenerating the manifest
against an input that decays in 48 hours buys nothing), and **4 waits on 3** (until the proof
stops restating the pin, a pin move is two files and the module does not own its own declaration).

**Blocked on a decision — 4, 6, 9.** Each is a real question, not a stalled cut:

| # | the question, in one line |
|---|---|
| 4 | Are 13 lost site locations an acceptable price for 484 corrected transformer counts? |
| 6 | Of the thirteen guarantees the deploy gate makes about an immutable release, which still bind `additive-cartridge-release.v1`? |
| 9 | Does "Current Verified Release" mean the newest release, or the reviewed one? |

**Blunt on the ratio.** Seven-to-three is a better queue than last night's ten-to-nothing, and the
reason is worth naming: three of the seven cuts (1, 7, 10) are **fixes to instruments**, not to
products. The estate's shippable-product surface is genuinely close to drained — that is why the
release-cadence agent stopped at three Pipeline News generations — but its *measuring* surface is
not. A clock inside a byte-identity gate, a harness that calls a swallowed timeout a healthy
layer, and a census that measures working trees are all defects that make every number downstream
of them a guess. They are worth a version each.

One further observation the ratio hides: **item 6 is the highest-value item in this queue and it
is a decision.** `pipelinenews` has the highest in-degree in the estate and has not deployed since
30 August. Nothing else here is worth as much, and no amount of building moves it.

## Open, measured, and deliberately not queued

Three things I verified but did not give a slot, with the reason, so the next session does not
rediscover them:

- **`gridatlas.live-set.v5` dropped the data-plane pin block.** `releases/current-v4.json` carries
  `current.data_release` (commit `32459230…`, `manifest_sha256 3246dbda…`, release id, repository),
  `current.product_oracle`, `current.map_ready` and `current.search`. `releases/current-v5.json` and
  its byte-identical twin `state/live-set.json` (both sha256 `2b57ae23…`, 4,367 bytes) carry **none
  of them**. Nothing is floating — the digest is still enforced at build time and in the browser —
  but the top-level live pointer no longer attests the pin it used to declare. Not queued because
  the owning file is genuinely two byte-identical files and the right answer is probably a
  generator that writes both; that is a design question, not a cut.
- **`state/streaming-road-fix.json` carries three commits with no digest** — `v8_oracle_commit`
  (line 6), `data_fidelity_commit` (line 8), `cvaa_commit` (line 10); the file contains zero
  `sha256`/`digest` fields. Four sibling state files have the same shape
  (`public-verification-request.json`, `v9-5-request.json`, `202608301821-highway-forensics.json`,
  `cross-repo-atlas-v9-milestones.json`). These are request records, not runtime pins, so nothing
  reads them to fetch bytes. Worth a sweep, not a version.
- **`no-time-based-gates` cannot see the defect in item 1.** The antibody is
  `({ workflows }) => workflows.flatMap(…)` and matches only `MISSION_EXPIRES_AT`, `EXPIRES_AT:`,
  `INCEPTED_AT`, `embargo_until` and calendar-pinned crons in `.github/workflows/`. `inoculate.mjs`'s
  `buildContext` carries no producer sources at all — `files` holds `STATE.md` and `index.html` and
  nothing else. It *does* fire on `globalgrid2050`, via `.github/workflows/catalogue-gridatlas-v9.yml`,
  which makes it worse rather than better: the repo is already flagged for the wrong clock while
  the one that actually reds four workflows sits in `scripts/major_project_news_v6.py:612`,
  invisible. Not queued because giving antibodies a source surface is `inoculate.mjs` **plus** a new
  vaccine — two files, estate-wide blast radius, and a decision about how much of a target
  repository cvaa should read. Raise it after item 1 lands, with item 1 as the worked example.

## Corrections to the 04:22 handover

Four numbers in the handover did not survive re-measurement. All four were caught the same way —
by re-deriving rather than re-reading.

| claim | measured |
|---|---|
| `v9-7-validate.yml` red on every run since **2 Sep 19:25Z**, six consecutive failures | red since **run 15, 2026-08-29T05:56:37Z** — **33 consecutive failures**, last green run 14 on 2026-08-26T04:01:15Z. And it is **two different causes**: runs 15–39 were the recency clock (item 1), runs 40–47 are the stale manifest (item 2). Fixing one leaves the other. |
| `data-gridatlas` layer-fidelity **red since 08:09Z today**; **50 of 120** checks fail; **four** layers return zero features | **all six runs since 2026-08-30T17:56:57Z have failed — it has never been green**. **25 of 60 layer rows** FAIL (17 over budget, 5 zero-feature, 3 over heap). **Five** zero-feature layers — `11kv` was missing from the list. |
| moving the pin is **three entries** in `pinned-products.js`, currently pinned at `b91e45b` | currently pinned at **`1c9909d1…`**; `b91e45b` appears in gridatlas only as prose. It is **two entries, six fields** — and until item 3, also two files, because the proof hard-codes the ref twice. |
| the stale Pipeline News title affects **all seven recent generations** | **25 of 25** published directories, every publication since 2026-08-31 13:43. |

One more, smaller: `pages.yml`'s last green was **2026-08-30T11:13:37Z**, not 31 August; and there
are **27** consecutive failures, which the handover had right.

## Method

- CI read authenticated through `scripts/gh-api.sh`, latest run **per workflow file** on each
  repo's own default branch — the per-branch sampling that hid `v9-7-validate` behind a newer green
  is not repeated here. Failure causes read from `/actions/jobs/<id>/logs`, which returns 200.
- Byte-level work done in `git clone --shared` copies under the scratchpad, never in a worktree.
  No repository other than `claude` was written to; `pipelinenews` and `cvaa` worktrees were left
  dirty exactly as found.
- The clock simulation in item 1 monkey-patches `datetime.datetime` in the two builder modules and
  restores the artefact with `git checkout` afterwards, in a throwaway clone. Script:
  `scratchpad/simulate_tomorrow.py` — the method is recorded here rather than the file, since a
  scratchpad does not survive.
- Numbers I could **not** verify are marked as such in the body. There is exactly one:
  the handover's *"882 of 886 records changed"* for the 04:02Z mutable-edge event. I measured
  886 of 886 records differing between `1c9909d` and `5181de3`, but that is a different commit
  pair than the one that event compared, so it neither confirms nor refutes it. **UNVERIFIED.**
