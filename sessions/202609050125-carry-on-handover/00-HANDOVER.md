# Carry-on handover — session 82e00a22, 2026-09-04 into 2026-09-05

**Filed 202609050125 UTC.** This is the log Vikram asked for at 23:21 UTC on 2026-09-04
("create a log file for this session in time stamped order so I just have to say claude
carry on"). It was written that night into Claude's private memory only — a hidden path
under `.claude/projects/` — and so could not be found the next morning. It now lives here,
in the repository, beside every other session log, and is pointed at by `/CARRY-ON.md` at
the root of this repo, which always names the newest handover.

All times UTC. Vikram's clock is BST, +1. The session ended at **2026-09-04 23:25:05 UTC**
on the usage limit, mid-sentence, with one question unanswered.

---

## 1. Timeline — what shipped, in order

| UTC | repo | commit / generation | what |
|---|---|---|---|
| 12:21 | gridatlas | v9.108 | live state on takeover; wind_onshore / wind_offshore / other MAP arrivals failing 100% |
| 13:30 | gridatlas | `64268fd` v9.111 gen 202609041330 | three technology buckets arrive; duplicate VENTUS wordmark on phones removed |
| 14:00 | ventus-grid-engine | `3589fac` | repo created: engine maths + deep-link contract, 3 proofs / 69 checks (subject says 1500 — typed in BST, an error) |
| 19:45–19:57 | gridatlas | v9.112 → v9.115, gen 202609041957 `b7a40d1` | iOS background-tab arrival fix (had been written into a part, never composed); one DuckDB runtime; GRID/SUBS chips on map; CRLF false-failure fixed; STATE.md contract breach corrected |
| 20:03 | ventus-grid-engine | `e7520b4` | Spider Sandbox receiver page, byte-for-byte copy, 60 checks, 🕷 pill proven in both states |
| 20:40 | ventus-grid-engine | `9ff94b3` | 4 engine modules promoted (7 proofs / 133 checks); engine graph 44/51; genome CI runner |
| 21:21 | ventus-grid-engine | `e03d09d` (bot) | genome CI regenerated the graph unaided — runner works |
| 21:23 | gridatlas | `703337b` v9.116 gen 202609042123 | **V8 layers panel restored** beneath the menus; grid engine proven intact first |
| 21:40 | spiders | `69dcdbe` | shared estate menu, first publication (42 checks) |
| 21:47 | spiders | `fa3cc49` module gen 202609042147 | V8 wordmark centred, V8's own text, menus the only addition; VERSIONS.md ledger |
| 21:48 | spiders | `6d9055d` | ledger corrected — the stamp had been typed as 202609042305 |
| 21:55 | ventus-grid-engine | `742b988` | estate menu on the receiver (one `<script defer>` line) |
| 21:56 | gridatlas | `bb7eb7e` | stale arrival-identity corpus proof fixed (reads current.json; ancestor check); **suite 894 green, 0 failures** |
| 21:58 | spiders | `31d1d52` | genome-spider species + CI runner with `command` input; gridatlas lineage graph |
| 22:06 | spiders / cvaa | `fdb5037` / `4b17c41` | genome crawl receipt 202609042150; cvaa fleet study 202609042153, every finding classified. The cvaa study was first committed onto Codex's branch by mistake, moved to main, branch restored to `19a20ce` |
| 22:07 | spiders | `9ea1fd5` | VERIFICATION.md admits the antibody was right about the typed stamp |
| 22:10 | ventus-grid-engine | `3b7cc6f` | receiver reads lineage live from spiders' Pages |
| 22:10 | gridatlas | `c44ba11` on `candidate/v9.117-menu-contiguous` | six titles together beside centred wordmark; Scope tools alphabetical — **prepared, not cut** |
| 22:11 | spiders | `a0f2231` module gen 202609042211 | wordmark uppercased as V8; alphabetical non-version groups; no visible "estate"; 82 checks |
| 22:20–22:35 | gridatlas | 5 commits on `candidate/promotion-lane`, tip `3061dfc` | two cvaa contracts, build lane (contents:read), promotion lane (dispatch-only), proof 41/41 — **prepared, not merged** |
| 22:32 | spiders | `7dd87f3` | estate genome documents committed beside the spider |
| 22:37 | globalgrid2050 | `5260db10` | the homepage moves to its own repo; this page becomes the record and links to it |
| 22:50 | spiders | `82780de` | menus contiguous — **superseded**: it moved the logo left and reworded it, neither of which was asked for |
| 22:51 | ventus-grid-engine | `5fb5e13` | receiver loader made manifest-driven (was a hard-coded pair) |
| 23:20 | — | — | fourteen shipped links handed over, every one probed 200 first |
| 23:24 | — | — | fresh-homepage plan given; one question put to Vikram: sentinel **carry, repoint or retire** |
| 23:25:03 | — | — | Vikram: *"this is the main session do it here"* |
| **23:25:05** | — | — | **session limit. Nothing executed after this point.** |

## 2. Live now — re-probed 2026-09-05 01:20 UTC, all 200

- **GridAtlas v9.116** — https://ventusltd.github.io/gridatlas/atlas/ — `current.json` generation `202609042123`, previous `202609041957`
  - arrival test (Berwick Bank, the bucket that failed 100% the previous morning):
    https://ventusltd.github.io/gridatlas/atlas/?repd_ref=9873&technology=wind_offshore&latitude=56.05&longitude=-2.35&zoom=9
- **Grid engine receiver** — https://ventusltd.github.io/ventus-grid-engine/
  - engine maths graph (44 nodes / 51 evidenced edges): `?graph=engine-graph`
  - GridAtlas cartridge lineage, read live from the spider: `?graph=gridatlas-lineage`
  - genome page with legend: `/genome/`
- **Shared estate menu, gen 202609042211** — https://ventusltd.github.io/spiders/species/seer-spider/estate-menu/demo.html
  (module: `…/estate-menu/estate-menu.js`)
- **Genome spider receipts** — https://ventusltd.github.io/spiders/species/genome-spider/receipts/LATEST.json (crawl 202609042150: 19 repos, 1,198 nodes, 2,553 edges)
- **Pipeline News v9.7** — https://globalgrid2050.com/uk_renewables_pipeline/v9.7/ (the link 216 industry readers received)
- **Pipeline News intelligence** — https://globalgrid2050.com/pipelinenews_intelligence/202609032329/
- **globalgrid2050.com** — 200, **111,836 bytes: still the old page.** The homepage swap never ran.

## 3. Repository state — measured 2026-09-05 01:20–01:25 UTC

| repo | branch | state |
|---|---|---|
| gridatlas | main | clean at `bb7eb7e`; two candidate branches unmerged (`candidate/v9.117-menu-contiguous` `c44ba11`, `candidate/promotion-lane` `3061dfc`) |
| pipelinenews | main | `3335fe6`, 0 ahead / 0 behind; untracked `releases/202609010145-*` and `build/202609010145-*` artefacts from an earlier v8-fast candidate |
| globalgrid2050 | main | `5260db10`, 0/0; working tree has a modified `.github/workflows/catalogue-composition-refresh.yml.disabled` and untracked `scripts/test_catalogue_gridatlas_v9.py` |
| globalgrid2050-homepage | main | clean; `index.html` is 94 lines / 2,080 bytes |
| cvaa | `codex/202609012100-cvaa-mission` | **leave it on Codex's branch**; work on main via a worktree |

## 4. Resume point — the exact place the session stopped

Vikram had just said **"this is the main session do it here"** about replacing the homepage
at the domain. Then the limit hit. As of 2026-09-05 he has **parked the homepage work**:

> "It was another session not this, forget the home page matters for a while."

So the homepage is **not** the next job. It is recorded here only so nothing is lost.

### Two findings about the fresh homepage, discovered 2026-09-05 and not in any earlier log

1. **Its search box is dead.** `index.html` declares `#gridSearch` and the repo carries
   `assets/dashboard.js` written to drive it, but the page contains **no `<script>` tag** —
   the file has never been loaded, at either URL. Typing in the box does nothing.
2. **Its only link would become circular.** It points at
   `https://ventusltd.github.io/globalgrid2050/`, which after a swap *is* the page itself.
   It should point at the v036 archive snapshot instead — which is exactly the footnote
   Vikram asked for, so it resolves itself.

### The undecided question, if the homepage is ever resumed

`scripts/catalogue_gridatlas_v9.py` **fails closed** unless the V8_ENTRY sentinel appears
once byte-for-byte in `index.html` (exactly four leading spaces, inside the `{name,url,note}`
array), its route appears once, and the `GRIDATLAS_V9_AUTOMATION_START/END` markers survive
(they are at lines 239 and 241 of the current page). A fresh `index.html` carries none of
that, so `catalogue-gridatlas-v9.yml` goes red on its first run. Three acceptable outcomes —
**carry** the block verbatim, **repoint** the script at the archived snapshot, or **retire**
the workflow in a commit that says why. Recommendation on the night: retire, because the job
it did — listing Atlas versions on the homepage — is now done better by the estate menu's
FILE panel. **Vikram has not chosen.** Do not leave it silently red.

The CNAME stays in `globalgrid2050`, always. Every deep path lives in that repo and GitHub
Pages cannot redirect; moving it 404s Pipeline News v9.7 for 216 readers.

## 5. His open decisions — do not act without his word

1. **Website** — he wants to understand it longer; leave as is. First change when ready:
   give verified v9.106 its own pinned URL `…/gridatlas/atlas/v/<generation>/`. The homepage
   still says the link opens v9.106; it opens v9.116.
2. **Promotion lane activation** — create GitHub Environment `gridatlas-release-authority`
   with a required reviewer, add secret `GRIDATLAS_PROMOTION_TOKEN`, decide the three legacy
   workflows that still push main (`verify-live.yml`, two `overnight`), then merge
   `candidate/promotion-lane`. The first merge must be a direct push — the lane cannot
   promote itself.
3. **v9.117** — cut only through the lane, after (2). Candidate is `c44ba11`.
4. `solar-bess-topology-v6` / `-v7` financial sandboxes are live with the sizing
   double-count (211.2 MW where 105.6 is real). The fix exists in gridatlas; the change is
   governed by globalgrid2050.
5. `seer-spider/` as the estate menu's home — name to confirm.
6. Governed integrations of the estate menu on homepage / Pipeline News v9.7 / federation
   map — one tag each, per `INTEGRATION.md`.
7. **Licence.** Four of five core repos (`seed-data`, `globalgrid2050-homepage`, `gridatlas`,
   `spiders`) have `license: null`; only `globalgrid2050` has one. A CEng cannot rely on
   unlicensed material. Publishing a licence grants rights irrevocably — his choice, not mine.

## 6. Known real bugs, not yet fixed

- `cvaa/tools/selftest.mjs` crashes on a Windows path fault — identical on main and on
  Codex's branch.
- `cvaa/replay.mjs` crashes when `e.stdout` is null.
- cvaa antibody `disk-is-not-what-ships` never sees `.gitattributes` — false on all 9 repos.
- The fresh homepage's dead search box (§4).

## 7. Other outstanding work, from the "go there" handover

- **`Ventusltd/studies`** — four PDFs untracked on an empty initial commit. Commit the
  published record, then add `ERRATA.md`; do not alter the PDFs — a dated publication gets an
  erratum, not a rewrite. Two verified findings: the "realistic avg 1.5 TWh/year" summary
  figure is wrong by 50× (1.5 TWh is the full-fleet single charge; the body's own
  30M × 50 kWh × 50 weeks = 75 TWh/year is correct), and "EVs approximately 70 percent more
  efficient than ICE" understates his own case (70% vs 25% is 2.8× more efficient, ~64% less
  energy for the same work) while the number 70 does double duty in the paper. Neither
  correction touches the headline: the 70% cut stands on 1,644 → 500–700 TWh independently.
- **The GB load flow.** His papers assert a "90–100 GW peak load ceiling is manageable" and
  it has never been computed. The parts exist and have never been joined: network from
  `Ventusltd/data-grid-gb` (`chatgpt/derived/etys-2025.normalized.json`, 8 MB, SHA-256
  pinned — 1,392 circuits with r/x/b and four seasonal MVA ratings, 1,472 transformers,
  1,735 sites, 7,316 fault scenarios); injections from `data-gb-electricity` / Elexon BMRS;
  solver `Ventusltd/pandapower`. Publish with provenance, claim boundary and a receipt —
  measurement, no verdict. `pypdf` is installed, poppler is not.

## 8. Rules in force

- Proofs read **composed bytes**, never parts. A fix can exist in a part and never reach the
  served cartridge.
- Make a proof fail before trusting it.
- Stamps come from `date -u` **in the same command**, never typed. Verify UTC with
  `git log --format=%ct`, not `TZ=UTC` — Windows git ignores the flag.
- cvaa runs in CI on committed bytes, not on this laptop.
- Every tool gets a view he can open on his phone.
- V8's look stays; menus are the only addition.
- The 🕷 pill and the Sandbox are copied, never restyled.
- Menus alphabetical; versions current-first.
- Check `git branch --show-current` before committing anywhere — a study was once committed
  onto Codex's branch.
- Report measurements, never grade them.
