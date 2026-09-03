# logs — the cross-session memory store

Session transcripts used to arrive here as multi-megabyte Markdown. Markdown is fine to
read and useless to query: to answer "which Bash calls errored" you scan seven megabytes
of prose. This directory holds the same transcripts as **Parquet**, one row per transcript
entry, so a question is a `WHERE` clause instead of a scroll.

**It now holds every Claude Code session on this machine, not one.** Eleven transcripts
across three project directories, 2026-08-30 to 2026-09-03, 30,684 rows. The point is
stated in the architect's words — *"retain long term memories for fault finding and
growing"*: a fresh session with no memory of any of this can query what earlier sessions
measured, broke, corrected and decided, instead of starting blind. Start at
[Bootstrapping a fresh session](#bootstrapping-a-fresh-session).

The Markdown rendering is not replaced by this and is not deleted by this. The two sit
side by side; sizes for both are recorded below so the choice of what to keep is a human
decision, not a side effect of this work.

## Conventions adopted from `Ventusltd/data-gb-electricity`

That repository is the estate's worked example of moving a bulky text format into compact
Parquet. What was copied from it:

| convention | as found there | as applied here |
|---|---|---|
| format | Parquet, never the raw source committed alongside | same — the JSONL is not committed |
| compression | `zstd` (`COMPRESSION zstd` on every `COPY`) | `zstd`, level 9 |
| audit artefact | `reports/latest_parquet_audit.json` — a machine-readable record of rows, bytes and key checks | `logs/reports/session_<short>_audit.json`, one per session |
| verification | `verify()` re-reads the written Parquet and checks declared invariants; a successful write is not the proof | readback with DuckDB, checking rows, distinct source lines, and first/last timestamps against the source JSONL |
| README shape | a "Parquet layout" section stating the path pattern, then a "Query examples" section of runnable SQL | same two sections, below |
| partition naming | Hive-style `dataset=…/year=…/month=…/data_0.parquet`, several physical files per partition allowed | **not adopted** — see below |

**Why the Hive partitioning was not copied.** There, partitioning by year and month prunes
a decade of half-hourly readings. A session transcript is one continuous run of a few
hours, so `year=2026/month=9` would be a single directory holding a single file — the
ceremony without the pruning. The natural partition key for this store is the *session*,
so the partition is the filename and the glob unions them:

```
logs/parquet/session_<short-session-id>.parquet
```

`read_parquet('logs/parquet/*.parquet')` reads the whole store; adding a session adds a
file and nothing else changes.

## Files

```
logs/
  README.md                              this file
  parquet/session_<short>.parquet        the store — 11 files, one per session
  reports/session_<short>_audit.json     counts, bytes, reconciliation, flagged rows
  tools/jsonl_to_parquet.py              the converter
  tools/classify_sensitivity.py          the sensitivity rule, with its self-test
  202609030940-full-session-5b94bee7.md  Markdown rendering (separate work, left alone)
```

The eleven sessions, in first-timestamp order:

| file | project | rows | from | to |
|---|---|---:|---|---|
| `session_b1c826bc.parquet` | `C--Users-vikra-OneDrive-Documents-GitHub` | 77 | 2026-08-30 | 2026-08-30 |
| `session_ed278f26.parquet` | `C--Users-vikra-OneDrive-Documents-GitHub` | 3,904 | 2026-08-30 | 2026-08-31 |
| `session_fb1f8db8.parquet` | `C--Users-vikra` | 1,370 | 2026-08-31 | 2026-08-31 |
| `session_ffe1875f.parquet` | `C--Users-vikra` | 933 | 2026-08-31 | 2026-08-31 |
| `session_fe663175.parquet` | `C--Users-vikra` | 11,236 | 2026-08-31 | 2026-09-01 |
| `session_0e09c52a.parquet` | `C--Users-vikra` | 118 | 2026-09-01 | 2026-09-01 |
| `session_dfac5e26.parquet` | `C--Users-vikra` | 3,075 | 2026-09-01 | 2026-09-01 |
| `session_9556e57d.parquet` | `C--Users-vikra` | 2,360 | 2026-09-01 | 2026-09-02 |
| `session_4114eb37.parquet` | `C--Windows-system32` | 320 | 2026-09-02 | 2026-09-02 |
| `session_bbe4731a.parquet` | `C--Users-vikra` | 2,132 | 2026-09-02 | 2026-09-03 |
| `session_5b94bee7.parquet` | `C--Users-vikra` | 5,159 | 2026-09-02 | 2026-09-03 |

`session_5b94bee7` is the session that built this store, so its transcript was still being
written while it was converted. It was **snapshotted first** and the snapshot converted:
5,159 JSONL lines, last row `2026-09-03 10:17:34.937+00`. Re-running the converter against
the live file later will pick up the rest; nothing else in the store moves.

`.gitattributes` at the repo root already carries `*.parquet binary`. That line is
load-bearing: this repo sets `* text=auto eol=lf`, and line-ending translation inside a
Parquet file corrupts it silently and the corruption survives the commit.

## Sizes, measured

Measured 2026-09-03 across all eleven transcripts.

| artefact | bytes | vs Parquet |
|---|---:|---|
| all 11 source JSONL transcripts (not committed) | 85,381,636 | **10.7x** larger |
| Markdown rendering of *one* session, `202609030940-full-session-5b94bee7.md` | 7,131,299 | 9.1x larger than that one session's Parquet |
| **`logs/parquet/*.parquet`, 11 files** | **7,954,308** | — |

The whole cross-session memory — four days, eleven sessions, 30,684 rows — costs under
8 MB, roughly what the Markdown rendering of a *single* session costs.

The ratio is not uniform, and the spread is the honest part of the number:

| session | source bytes | parquet bytes | ratio |
|---|---:|---:|---:|
| `bbe4731a` | 9,021,986 | 270,412 | **33.4x** |
| `5b94bee7` | 11,796,003 | 781,239 | 15.1x |
| `dfac5e26` | 6,346,082 | 491,549 | 12.9x |
| `fe663175` | 36,778,761 | 3,719,628 | 9.9x |
| `b1c826bc` | 128,825 | 24,660 | 5.2x |
| `9556e57d` | 6,569,948 | 1,320,265 | **5.0x** |

A session compresses in proportion to how much of its JSONL is repeated per-line envelope
(`cwd`, `sessionId`, `gitBranch`, `version`, uuids) rather than unique payload. `bbe4731a`
is many short entries and collapses 33x; `9556e57d` carries base64 image blocks and large
unique tool output and manages 5x. Neither figure is a property of Parquet — both are
properties of the transcript, and quoting the 33x as "the compression ratio" would be
exactly the flattering single number this estate keeps having to correct.

## The `memory` view — start here

Define this once per DuckDB connection. It is the safe default set: everything the
classifier judged neutral or publicly verifiable.

```sql
CREATE VIEW memory AS
SELECT * FROM read_parquet('logs/parquet/*.parquet')
WHERE sensitivity = 'ok';
```

```sql
SELECT count(*) AS memory_rows FROM memory;
```

```
┌─────────────┐
│ memory_rows │
├─────────────┤
│       30683 │
└─────────────┘
```

30,683 of 30,684 rows. **Nothing was deleted.** The raw union stays one query away, and
the whole point of the design is that a misclassification is recoverable:

```sql
-- everything the default view holds back, and the reason it was held back
SELECT session_id[1:8] AS session, source_line, sensitivity, sensitivity_reason,
       substr(replace(content, chr(10), ' '), 1, 60) AS snippet
FROM read_parquet('logs/parquet/*.parquet')
WHERE sensitivity <> 'ok';
```

```
┌──────────┬─────────────┬──────────────────────┬──────────────────────────────────────────────────────────────┬──────────────────────────────┐
│ session  │ source_line │     sensitivity      │                      sensitivity_reason                      │           snippet            │
├──────────┼─────────────┼──────────────────────┼──────────────────────────────────────────────────────────────┼──────────────────────────────┤
│ 9556e57d │         688 │ opinion_about_person │ judgement 'reckless' applied to person reference 'the owner' │ === quantumspawn-recovery ve │
└──────────┴─────────────┴──────────────────────┴──────────────────────────────────────────────────────────────┴──────────────────────────────┘
```

### The classification rule

The architect's words: *"Anything controversial like opinions about people, but keep all
data that is publicly verifiable or neutral."* `logs/tools/classify_sensitivity.py`
implements exactly that and nothing wider.

| label | rows | means |
|---|---:|---|
| `ok` | 30,683 | publicly verifiable or neutral. The default view. |
| `opinion_about_person` | 1 | a subjective judgement about an identifiable **human** — competence, character, motives, or the quality of their work as a person. |
| `credential` | 0 | a credential value was found and replaced in `content`. |

**FLAG, NEVER DELETE.** Every row is written whatever its label. Credentials are the one
place the *value* is replaced in `content` (the row still exists, and `redacted` is true).

The rule is deliberately narrow, because over-flagging would destroy the thing being
built. Technical findings, measurements, commit SHAs, code, error text, CI results, defect
analysis, an agent correcting itself, and one agent assessing another agent's *artefact*
are all neutral — and they are the entire value of this store. To flag, a sentence must
carry **both** a human reference and a judgement aimed at that human, and then survive
four vetoes, each of which fired on a real sentence in this corpus:

| veto | a real sentence it saved |
|---|---|
| technical sense | *"the loader asserts `payloadRequests === 0` at mount — lazy until the user acts"* |
| self-correction | *"I was careless with the denominator and the summary changed meaning"* |
| an agent, not a human | *"Codex's fix was sloppy and the digest did not match"* |
| an artefact, not a person | *"BETA reads as scope, not as a warning the number is unreliable"* |

Across 30,684 rows only **59 sentences** contained a judgement word at all; 55 of those had
no human reference anywhere near them. A sample of what stayed `ok`, and should have:

- `<dishonest>` — *"Two dishonest exits were available and are recorded as **rejected**: raise the boundary because my own lane needed it…"* — the agent judging its own options.
- `<flaky>` — *"It isn't flaky; it's a contradiction between the trigger set and the only condition the gate accepts."* — a CI diagnosis.
- `<careless>` — *"A scope that counts substations near a blank patch of farmland is one careless sentence away from reading as 'there is capacity here'…"* — a judgement of a *sentence*.
- `<stupid>` — *"also open relationship evidence has stupid information, look at it in chrome"* — the architect judging a UI panel's content, not a person.
- `<meticulous>` — *"The v2 product is meticulous — 'included, never complete', exact period identities…"* — praise of a data product.
- `<unqualified>` — *"**2 abandonments**: `BOSO`/`BOSW` both released the unqualified 'Barrow' feature (20 m from the 132 kV network)."* — a data-quality term.

The self-test is a real gate, not a formality — a check built only from cases the code
already passes cannot fail, so it carries seven sentences that **must** flag alongside
nineteen real corpus sentences that must not:

```bash
python logs/tools/classify_sensitivity.py
```

```
positive controls (must flag)     : 7
negative controls (must not flag) : 19
failures: 0
```

### The one flagged row, and why it is probably wrong

It is a cvaa vaccine specification. The sentence:

> *"Here, personality means the durable working character evidenced by repository
> behaviour: curious, evidence-led, self-falsifying, autonomous without being **reckless**,
> direct with **the owner**, collaborative through receipts…"*

"reckless" is negated (`without being`) and describes the *agent's* desired character;
"the owner" is a nearby human reference the co-occurrence window caught. This is a false
positive and it is left in place deliberately rather than tuned away in the same run that
found it — tightening a rule until the one case it caught disappears is how a gate stops
measuring. It costs one row out of 30,684, the row is still in the store, and overturning
it is one predicate:

```sql
CREATE OR REPLACE VIEW memory AS
SELECT * FROM read_parquet('logs/parquet/*.parquet')
WHERE sensitivity = 'ok'
   OR (session_id LIKE '9556e57d%' AND source_line = 688);
```

The narrower fix, if the architect wants it in the classifier rather than the view, is to
veto a judgement preceded by `without being` / `never` / `rather than` — a negated
judgement is a specification, not an accusation.

## Running the queries

Every query below was executed against the real store and the output shown under it is
real, trimmed only in width. Run them **from the repository root**, so the relative glob
resolves.

The DuckDB CLI is **not installed on this machine**, so these were run through the Python
binding. Either route works:

```bash
# Route A — the CLI, if you have it (https://duckdb.org/docs/installation/)
duckdb -c "SET TimeZone='UTC'; SELECT count(*) FROM read_parquet('logs/parquet/*.parquet');"

# Route B — the Python binding, which is what produced the output below
pip install duckdb
python -c "import duckdb; duckdb.execute(\"SET TimeZone='UTC'\"); duckdb.sql(open('q.sql').read()).show()"
```

On Windows, prefix Route B with `PYTHONIOENCODING=utf-8` or DuckDB's box-drawing output
raises `'charmap' codec can't encode`.

All timestamps are stored UTC. `SET TimeZone='UTC';` only affects how they are *rendered*;
without it DuckDB prints them in your local zone, which is the same instant.

### 1. Read the file

```sql
SELECT ord, ts, entry_type, content_kind, tool_name, content_len
FROM read_parquet('logs/parquet/*.parquet')
LIMIT 5;
```

```
┌───────┬──────┬───────────────────────┬──────────────┬───────────┬─────────────┐
│  ord  │  ts  │      entry_type       │ content_kind │ tool_name │ content_len │
├───────┼──────┼───────────────────────┼──────────────┼───────────┼─────────────┤
│     0 │ NULL │ mode                  │ meta         │ NULL      │           6 │
│     1 │ NULL │ permission-mode       │ meta         │ NULL      │           4 │
│     2 │ NULL │ atis-latch            │ meta         │ NULL      │           0 │
│     3 │ NULL │ bridge-session        │ meta         │ NULL      │           0 │
│     4 │ NULL │ file-history-snapshot │ meta         │ NULL      │           0 │
└───────┴──────┴───────────────────────┴──────────────┴───────────┴─────────────┘
```

The first rows are session bookkeeping, which is why they carry no timestamp. That is not
a defect — see *Nulls in `ts`* below.

### 2. Reconciliation — rows against source lines

`source_line` restarts at 1 in every session, so reconciliation is **per session**.
Counting distinct `source_line` across the union would answer a different question.

```sql
SELECT project, session_id[1:8] AS sess, count(*) AS rows,
       count(DISTINCT source_line) AS src_lines,
       min(ts) AS first_ts, max(ts) AS last_ts
FROM read_parquet('logs/parquet/*.parquet')
GROUP BY project, sess ORDER BY first_ts;
```

```
┌──────────────────────────────────────────┬──────────┬───────┬───────────┬────────────────────────────┬────────────────────────────┐
│                 project                  │   sess   │ rows  │ src_lines │          first_ts          │          last_ts           │
├──────────────────────────────────────────┼──────────┼───────┼───────────┼────────────────────────────┼────────────────────────────┤
│ C--Users-vikra-OneDrive-Documents-GitHub │ b1c826bc │    77 │        77 │ 2026-08-30 21:26:58.944+00 │ 2026-08-30 21:34:41.547+00 │
│ C--Users-vikra-OneDrive-Documents-GitHub │ ed278f26 │  3904 │      3904 │ 2026-08-30 21:45:35.143+00 │ 2026-08-31 14:06:26.989+00 │
│ C--Users-vikra                           │ fb1f8db8 │  1370 │      1370 │ 2026-08-31 14:07:40.946+00 │ 2026-08-31 16:17:13.154+00 │
│ C--Users-vikra                           │ ffe1875f │   933 │       933 │ 2026-08-31 16:18:06.527+00 │ 2026-08-31 17:41:30.921+00 │
│ C--Users-vikra                           │ fe663175 │ 11236 │     11230 │ 2026-08-31 17:42:40.516+00 │ 2026-09-01 17:53:19.247+00 │
│ C--Users-vikra                           │ 0e09c52a │   118 │       118 │ 2026-09-01 12:10:15.253+00 │ 2026-09-01 12:15:47.435+00 │
│ C--Users-vikra                           │ dfac5e26 │  3075 │      3075 │ 2026-09-01 17:54:31.137+00 │ 2026-09-01 22:22:42.792+00 │
│ C--Users-vikra                           │ 9556e57d │  2360 │      2356 │ 2026-09-01 22:23:50.787+00 │ 2026-09-02 00:50:01.859+00 │
│ C--Windows-system32                      │ 4114eb37 │   320 │       320 │ 2026-09-02 16:05:52.454+00 │ 2026-09-02 17:48:26.274+00 │
│ C--Users-vikra                           │ bbe4731a │  2132 │      2132 │ 2026-09-02 17:10:36.412+00 │ 2026-09-03 01:04:26.492+00 │
│ C--Users-vikra                           │ 5b94bee7 │  5159 │      5159 │ 2026-09-02 18:29:52.377+00 │ 2026-09-03 10:17:34.937+00 │
└──────────────────────────────────────────┴──────────┴───────┴───────────┴────────────────────────────┴────────────────────────────┘
```

`src_lines` equals the non-blank JSONL line count of every source file, exactly, for all
eleven. **0 lines failed to parse in 85 MB.** Two sessions show `rows > src_lines` —
`fe663175` by 6 and `9556e57d` by 4 — which is the grain working as designed, not loss:
those lines carry an `image` content block alongside text, and one line becomes two rows.
The reconciliation key is `count(DISTINCT source_line)`, and it matches everywhere.

```sql
SELECT count(*) AS total_rows, count(DISTINCT session_id) AS sessions,
       count(DISTINCT project) AS projects, min(ts) AS first_ts, max(ts) AS last_ts
FROM read_parquet('logs/parquet/*.parquet');
```

```
┌────────────┬──────────┬──────────┬────────────────────────────┬────────────────────────────┐
│ total_rows │ sessions │ projects │          first_ts          │          last_ts           │
├────────────┼──────────┼──────────┼────────────────────────────┼────────────────────────────┤
│      30684 │       11 │        3 │ 2026-08-30 21:26:58.944+00 │ 2026-09-03 10:17:34.937+00 │
└────────────┴──────────┴──────────┴────────────────────────────┴────────────────────────────┘
```

## Schema

`DESCRIBE SELECT * FROM read_parquet('logs/parquet/*.parquet');` returns **25 columns** —
the original 22, unchanged and in their original order, plus three appended for the
cross-session store (`project`, `sensitivity`, `sensitivity_reason`). No column was
renamed, so every query written against the single-session store still runs.

| column | type | holds |
|---|---|---|
| `ord` | BIGINT | Global ordinal, 0-based and contiguous. **Order the transcript by this**, not by `ts` — bookkeeping rows have no timestamp. |
| `source_line` | INTEGER | 1-based line number in the source JSONL. The reconciliation key. |
| `block_no` | INTEGER | Index of the content block within its line. 0 unless one line carried several blocks. |
| `ts` | TIMESTAMP WITH TIME ZONE | Entry timestamp, UTC. NULL on session-bookkeeping rows that have none. |
| `entry_type` | VARCHAR *(dict)* | Raw JSONL `type`: `user`, `assistant`, `attachment`, `system`, `mode`, `ai-title`, `queue-operation`, … |
| `subtype` | VARCHAR *(dict)* | `system.subtype` (`turn_duration`, `away_summary`, `compact_boundary`) or the attachment's own type (`total_tokens_reminder`, `queued_command`, `edited_text_file`, …). |
| `role` | VARCHAR *(dict)* | `user` or `assistant`. NULL on non-message rows. |
| `content_kind` | VARCHAR *(dict)* | **The discriminator.** One of `text`, `thinking`, `tool_use`, `tool_result`, `attachment`, `system`, `meta`. This is what lets a query skip tool payloads. |
| `tool_name` | VARCHAR *(dict)* | Tool name. Set on `tool_use` rows and **also back-filled onto the matching `tool_result`** by `tool_use_id`, so results can be grouped by tool without a join. |
| `tool_use_id` | VARCHAR | Links a `tool_use` row to its `tool_result` row. |
| `is_error` | BOOLEAN | The tool result's error flag. NULL when not a tool result. |
| `model` | VARCHAR *(dict)* | Model id on assistant rows. |
| `uuid`, `parent_uuid` | VARCHAR | Entry identity and its parent, for reconstructing the tree. |
| `session_id` | VARCHAR *(dict)* | Session this row came from. Taken from the JSONL line; where a bookkeeping line carries none it falls back to the source file's own session uuid, so **every row in the union is attributable**. |
| `cwd`, `git_branch`, `cli_version` | VARCHAR *(dict)* | Working directory, branch, and CLI version at the time of the entry. |
| `is_sidechain` | BOOLEAN | True for subagent traffic. |
| `redacted` | BOOLEAN | True if a credential value was replaced in this row's `content`. |
| `content_len` | INTEGER | Character length of `content`, 0 when NULL. Filter on this to find the big payloads without reading them. |
| `content` | VARCHAR | The payload. Prose for `text`/`thinking`; the tool's input as compact JSON for `tool_use`; the flattened result text for `tool_result`. |
| `project` | VARCHAR *(dict)* | The Claude Code project directory the transcript came from: `C--Users-vikra`, `C--Users-vikra-OneDrive-Documents-GitHub`, `C--Windows-system32`. |
| `sensitivity` | VARCHAR *(dict)* | `ok`, `opinion_about_person`, or `credential`. **The `memory` view filters on this.** |
| `sensitivity_reason` | VARCHAR | Why the row was flagged. Empty string when `ok`. |

*(dict)* marks the **twelve** columns written with dictionary encoding — the original ten
plus `project` and `sensitivity`. Verified by reading the written files back, not assumed:
across all 11 files and all 12 row groups, every one of those twelve column-chunks carries
`RLE_DICTIONARY`, and 0 fail the check. `content` and `sensitivity_reason` deliberately do
not — one is high-cardinality prose, the other is empty on 30,683 of 30,684 rows, and a
dictionary would only add a page to each.

### What is in there, by kind

```sql
SELECT content_kind, count(*) AS rows, sum(content_len) AS chars
FROM memory
GROUP BY content_kind
ORDER BY chars DESC;
```

```
┌──────────────┬───────┬─────────┐
│ content_kind │ rows  │  chars  │
├──────────────┼───────┼─────────┤
│ tool_use     │  4776 │ 7484001 │
│ tool_result  │  4774 │ 5360370 │
│ image        │    10 │ 4804215 │
│ attachment   │  5309 │ 1690814 │
│ meta         │ 10486 │ 1596735 │
│ text         │  2226 │ 1320753 │
│ system       │   236 │   10942 │
│ thinking     │  2866 │    6881 │
└──────────────┴───────┴─────────┘
```

Tool traffic is 12.8 M of the 22.3 M characters. Splitting it into its own `content_kind`
is the difference between searching 1.3 MB of prose and searching everything.

Two things worth knowing before you trust a `sum(content_len)` here. **`image` is ten rows
holding 4.8 M characters** — base64 screenshot payloads, 4.5% of the store's text in
0.03% of its rows; exclude it or one `LIKE` scan dominates your query time. And
**`thinking` is 2,866 rows carrying 6,881 characters total** — a mean of 2.4 characters.
Thinking blocks are almost all empty in these transcripts, so "the model's reasoning" is
not in this store in any useful quantity; do not build a query on the assumption that it is.

### Nulls in `ts`

```sql
SELECT entry_type, count(*) AS rows_without_ts
FROM memory
WHERE ts IS NULL
GROUP BY entry_type
ORDER BY rows_without_ts DESC
LIMIT 10;
```

```
┌───────────────────────────┬─────────────────┐
│        entry_type         │ rows_without_ts │
├───────────────────────────┼─────────────────┤
│ bridge-session            │            1470 │
│ mode                      │            1458 │
│ atis-latch                │            1458 │
│ permission-mode           │            1458 │
│ ai-title                  │            1457 │
│ last-prompt               │            1455 │
│ file-history-snapshot     │             150 │
│ artifact-autoreact-ledger │              22 │
│ cost-state                │              22 │
│ artifact-comment-monitor  │              13 │
└───────────────────────────┴─────────────────┘
```

8,963 of the view's 30,683 rows have no timestamp: the source line has no `timestamp` field.
These are session bookkeeping, not conversation. They are kept so line counts reconcile,
and they are cheap: `meta` rows store one short field, never the whole snapshot blob.
**Add `WHERE content_kind <> 'meta'` when you want the conversation.**

`ord` is per-session, restarting at 0 in each file. Within one session `ORDER BY ord`
still reconstructs the transcript exactly. **Across sessions, order by `ts`** and accept
that the bookkeeping rows drop out — or order by `session_id, ord`.

## Searching across all sessions at once

This is what the union buys. One `WHERE` clause reaches four days and eleven sessions.

**Where has a topic ever been discussed, and by which session?**

```sql
SELECT session_id[1:8] AS session, project, count(*) AS mentions, min(ts)::DATE AS first_day
FROM memory
WHERE content ILIKE '%gridatlas%'
GROUP BY session, project
ORDER BY mentions DESC;
```

```
┌──────────┬──────────────────────────────────────────┬──────────┬────────────┐
│ session  │                 project                  │ mentions │ first_day  │
├──────────┼──────────────────────────────────────────┼──────────┼────────────┤
│ fe663175 │ C--Users-vikra                           │     1241 │ 2026-08-31 │
│ ed278f26 │ C--Users-vikra-OneDrive-Documents-GitHub │      909 │ 2026-08-30 │
│ 5b94bee7 │ C--Users-vikra                           │      611 │ 2026-09-02 │
│ dfac5e26 │ C--Users-vikra                           │      582 │ 2026-09-01 │
│ 9556e57d │ C--Users-vikra                           │      487 │ 2026-09-01 │
│ bbe4731a │ C--Users-vikra                           │      237 │ 2026-09-02 │
│ fb1f8db8 │ C--Users-vikra                           │      115 │ 2026-08-31 │
│ 4114eb37 │ C--Windows-system32                      │       39 │ 2026-09-02 │
│ ffe1875f │ C--Users-vikra                           │       33 │ 2026-08-31 │
│ b1c826bc │ C--Users-vikra-OneDrive-Documents-GitHub │       24 │ 2026-08-30 │
│ 0e09c52a │ C--Users-vikra                           │       23 │ 2026-09-01 │
└──────────┴──────────────────────────────────────────┴──────────┴────────────┘
```

**When did a specific idea first appear?** The CRLF problem, in first-mention order:

```sql
SELECT session_id[1:8] AS session, ts::DATE AS day, content_kind,
       substr(replace(content, chr(10), ' '), 1, 78) AS snippet
FROM memory
WHERE content ILIKE '%core.autocrlf%' OR content ILIKE '%w/crlf%'
ORDER BY ts LIMIT 6;
```

```
┌──────────┬────────────┬──────────────┬────────────────────────────────────────────────────────────────────────────────┐
│ session  │    day     │ content_kind │                                    snippet                                     │
├──────────┼────────────┼──────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ ed278f26 │ 2026-08-31 │ tool_use     │ {"command": "du -sh . 2>/dev/null | head -1 && echo \"cloning with LF working  │
│ ed278f26 │ 2026-08-31 │ tool_use     │ {"command": "\\\necho \"=== confirm my releases and .gitattributes are gone == │
│ fb1f8db8 │ 2026-08-31 │ tool_use     │ {"command": "cd \"C:/Users/vikra/OneDrive/Documents/GitHub/globalgrid2050\"; g │
│ fe663175 │ 2026-08-31 │ tool_use     │ {"command": "C=atlas/cartridges/202608311910-neon-substation-links-v9-6.js\nec │
│ fe663175 │ 2026-08-31 │ tool_use     │ {"command": "cd /c/Users/vikra/OneDrive/Documents/GitHub/.claude-worktrees/gri │
│ fe663175 │ 2026-08-31 │ tool_use     │ {"command": "cd /c/Users/vikra/OneDrive/Documents/GitHub/.claude-worktrees/gri │
```

Add `AND content_kind IN ('text','thinking')` to search only what was *said* rather than
what was run. Add `AND content_kind <> 'image'` to any broad `ILIKE` — ten base64 rows hold
4.8 M characters and will otherwise dominate the scan.

## Bootstrapping a fresh session

**This is the section that makes the store worth keeping.** A new session has no memory of
any of the eleven. These six queries hand it the accumulated history in a few seconds.
Every one was run against this store and the output below is real.

Define the view first (see [The `memory` view](#the-memory-view--start-here)).

### 1. What sessions exist, when, and how rough were they?

```sql
SELECT session_id[1:8] AS session, project, count(*) AS rows,
       min(ts)::DATE AS from_day, max(ts)::DATE AS to_day,
       count(*) FILTER (WHERE is_error) AS errors
FROM memory
GROUP BY session, project
ORDER BY min(ts);
```

```
┌──────────┬──────────────────────────────────────────┬───────┬────────────┬────────────┬────────┐
│ session  │                 project                  │ rows  │  from_day  │   to_day   │ errors │
├──────────┼──────────────────────────────────────────┼───────┼────────────┼────────────┼────────┤
│ b1c826bc │ C--Users-vikra-OneDrive-Documents-GitHub │    77 │ 2026-08-30 │ 2026-08-30 │      0 │
│ ed278f26 │ C--Users-vikra-OneDrive-Documents-GitHub │  3904 │ 2026-08-30 │ 2026-08-31 │     22 │
│ fb1f8db8 │ C--Users-vikra                           │  1370 │ 2026-08-31 │ 2026-08-31 │      5 │
│ ffe1875f │ C--Users-vikra                           │   933 │ 2026-08-31 │ 2026-08-31 │      6 │
│ fe663175 │ C--Users-vikra                           │ 11236 │ 2026-08-31 │ 2026-09-01 │     54 │
│ 0e09c52a │ C--Users-vikra                           │   118 │ 2026-09-01 │ 2026-09-01 │      0 │
│ dfac5e26 │ C--Users-vikra                           │  3075 │ 2026-09-01 │ 2026-09-01 │     18 │
│ 9556e57d │ C--Users-vikra                           │  2359 │ 2026-09-01 │ 2026-09-02 │     12 │
│ 4114eb37 │ C--Windows-system32                      │   320 │ 2026-09-02 │ 2026-09-02 │      0 │
│ bbe4731a │ C--Users-vikra                           │  2132 │ 2026-09-02 │ 2026-09-03 │     20 │
│ 5b94bee7 │ C--Users-vikra                           │  5159 │ 2026-09-02 │ 2026-09-03 │     21 │
└──────────┴──────────────────────────────────────────┴───────┴────────────┴────────────┴────────┘
```

### 2. Which tools fail, and is the failure recurrent or a one-off?

A failure seen in one session is an incident. A failure seen in eight is a property of this
machine, and worth reading before repeating it.

```sql
SELECT tool_name, count(*) AS failures, count(DISTINCT session_id) AS sessions
FROM memory
WHERE is_error
GROUP BY tool_name
ORDER BY failures DESC
LIMIT 10;
```

```
┌────────────────────────────────────────┬──────────┬──────────┐
│               tool_name                │ failures │ sessions │
├────────────────────────────────────────┼──────────┼──────────┤
│ Bash                                   │      114 │        8 │
│ mcp__claude-in-chrome__javascript_tool │       13 │        4 │
│ mcp__claude-in-chrome__computer        │        8 │        2 │
│ mcp__claude-in-chrome__navigate        │        8 │        4 │
│ PowerShell                             │        6 │        4 │
│ Edit                                   │        6 │        5 │
│ Read                                   │        1 │        1 │
│ WebFetch                               │        1 │        1 │
│ Write                                  │        1 │        1 │
└────────────────────────────────────────┴──────────┴──────────┘
```

157 failed tool calls in four days, 114 of them `Bash`. The Chrome tools fail across four
separate sessions, which matches the standing note about backgrounded tabs.

### 3. What *kind* of error keeps coming back?

```sql
SELECT lower(regexp_extract(content,
         '(command not found|no such file or directory|permission denied|fatal: [a-z ]+|ENOENT|ModuleNotFoundError|SyntaxError|non-fast-forward)', 1)) AS failure,
       count(*) AS hits, count(DISTINCT session_id) AS sessions
FROM memory
WHERE is_error
  AND regexp_matches(content, '(command not found|no such file or directory|permission denied|fatal: [a-z ]+|ENOENT|ModuleNotFoundError|SyntaxError|non-fast-forward)')
GROUP BY failure
ORDER BY hits DESC;
```

```
┌───────────────────┬───────┬──────────┐
│      failure      │ hits  │ sessions │
├───────────────────┼───────┼──────────┤
│ syntaxerror       │    12 │        5 │
│ enoent            │     3 │        2 │
│ command not found │     1 │        1 │
│ non-fast-forward  │     1 │        1 │
└───────────────────┴───────┴──────────┘
```

`SyntaxError` in five of eleven sessions is the single most repeated named failure in the
store, and it is the escaping problem `CLAUDE.md` warns about at length: code piped through
a shell that mangles it. The memory confirms the warning rather than restating it.

### 4. What did an earlier session get wrong and correct?

The corrections are the most transferable thing in here — most were caught by measuring
again, not by reasoning harder.

```sql
SELECT session_id[1:8] AS session, ts::DATE AS day,
       substr(replace(content, chr(10), ' '), 1, 100) AS correction
FROM memory
WHERE content_kind IN ('text','thinking')
  AND regexp_matches(content, '(?i)(I was wrong|my diagnosis was wrong|that was wrong|correction[,:]|this corrects|I had it backwards)')
ORDER BY ts DESC
LIMIT 6;
```

```
┌──────────┬────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ session  │    day     │                                              correction                                              │
├──────────┼────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 5b94bee7 │ 2026-09-03 │ The spider is right and I was wrong. D5 is **not** closed. Four repos carry GitHub's default `* text │
│ bbe4731a │ 2026-09-02 │ Redone in Pipeline News' own format. It's live in Chrome now at **http://127.0.0.1:8791/wider-fleet- │
│ 4114eb37 │ 2026-09-02 │ Yes — these fill the 8.5-hour hole completely. And they explain the 8AM thing precisely.  ## It didn │
│ ed278f26 │ 2026-08-31 │ **Straight answer: no, I hadn't. I'd built an analytical page *about* your data, not the next versio │
│ ed278f26 │ 2026-08-31 │ Correction: the `MAP ATLAS` nav link **does** still exist (line 37) — it's been repointed to the bro │
└──────────┴────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Drop the `substr(...)` to read the whole correction — that is where the evidence lives.

### 5. What has the architect actually asked for, most recent first?

Decisions and instructions arrive as user text. This is the fastest way to inherit intent.

```sql
SELECT ts::DATE AS day, session_id[1:8] AS session,
       substr(replace(content, chr(10), ' '), 1, 96) AS ask
FROM memory
WHERE role = 'user' AND content_kind = 'text' AND content_len BETWEEN 25 AND 400
ORDER BY ts DESC
LIMIT 8;
```

```
┌────────────┬──────────┬──────────────────────────────────────────────────────────────────────────────────────────────────┐
│    day     │ session  │                                               ask                                                │
├────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2026-09-03 │ 5b94bee7 │ And install duckdb and parquet in the Claude repo and force the README to enable this discipline │
│ 2026-09-03 │ 5b94bee7 │ I want to query all conservations ever with anything controversial excluded but re programme I w │
│ 2026-09-03 │ 5b94bee7 │ to be clear the CI/CD agent with constantly use my laptop compute WHICH IS POWERFUL by the way t │
│ 2026-09-03 │ 5b94bee7 │ and setup 1 agent that just does the CI CD automation checks on your logic that changes dynamica │
│ 2026-09-03 │ bbe4731a │ and write code to summon other pipeline items within the atlas after clicking the map, write is  │
│ 2026-09-03 │ bbe4731a │ now show me the journey in chrome extesnsion                                                     │
│ 2026-09-03 │ bbe4731a │ file a log of this session, not summary, but the entire log here C:\Users\vikra\OneDrive\Documen │
│ 2026-09-03 │ bbe4731a │ gemini has done the same in folder C:\Users\vikra\OneDrive\Documents\GitHub\gemini               │
└────────────┴──────────┴──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6. What changed most recently, and where is the work concentrated?

```sql
SELECT max(ts)::DATE AS last_touched, count(*) AS edits,
       regexp_extract(content, '"file_path": ?"([^"]+)"', 1) AS file
FROM memory
WHERE content_kind = 'tool_use' AND tool_name IN ('Write','Edit')
GROUP BY file
HAVING count(*) > 4
ORDER BY max(ts) DESC
LIMIT 6;
```

```
┌──────────────┬───────┬──────────────────────────────────────────────────────────────────────────────────────────┐
│ last_touched │ edits │                                           file                                           │
├──────────────┼───────┼──────────────────────────────────────────────────────────────────────────────────────────┤
│ 2026-09-03   │     5 │ C:\\Users\\vikra\\...\\GitHub\\claude\\CLAUDE.md                                         │
│ 2026-09-03   │    22 │ C:\\Users\\vikra\\...\\claude\\sessions\\202609030422-handover\\00-HANDOVER.md           │
│ 2026-09-02   │    10 │ C:\\Users\\vikra\\...\\pipelinenews\\tools\\overnight\\202609012300-shift.mjs            │
│ 2026-09-02   │    21 │ C:\\Users\\vikra\\...\\gridatlas\\tools\\overnight\\steps\\202609012350-owner-boundary.mjs │
│ 2026-09-01   │     6 │ C:\\Users\\vikra\\...\\gridatlas\\tools\\recompose.mjs                                    │
│ 2026-09-01   │     8 │ C:\\Users\\vikra\\...\\gridatlas\\tools\\overnight\\steps\\202609012330-grid-at-point.mjs │
```

Paths are shown as stored: `content` holds the tool's input as JSON, so backslashes are
JSON-escaped and the middle of each path is elided above for width only.

And where the work happened at all:

```sql
SELECT regexp_extract(cwd, 'GitHub.([A-Za-z0-9_.-]+)', 1) AS repo,
       count(DISTINCT session_id) AS sessions, count(*) AS rows, max(ts)::DATE AS last_seen
FROM memory
WHERE cwd IS NOT NULL AND contains(cwd, 'GitHub')
GROUP BY repo
ORDER BY rows DESC
LIMIT 8;
```

```
┌─────────────────────┬──────────┬───────┬────────────┐
│        repo         │ sessions │ rows  │ last_seen  │
├─────────────────────┼──────────┼───────┼────────────┤
│ .claude-worktrees   │        4 │  5226 │ 2026-09-01 │
│ pipelinenews        │        9 │  4206 │ 2026-09-03 │
│ gridatlas           │        6 │  3255 │ 2026-09-03 │
│ globalgrid2050      │        8 │  2077 │ 2026-09-03 │
│ claude              │        2 │   778 │ 2026-09-03 │
│ cvaa                │        5 │   421 │ 2026-09-03 │
│ data-grid-gb        │        3 │   280 │ 2026-09-03 │
│ data-gb-electricity │        3 │   121 │ 2026-09-01 │
└─────────────────────┴──────────┴───────┴────────────┘
```

`.claude-worktrees` at the top is the standing fact that the canonical repos are under
`OneDrive/Documents/GitHub/` and the worktrees are not — 5,226 rows of work happened in a
worktree, and a session that measures one of those and calls it the repository will be
measuring the wrong tree.

**A caution on reading this store as truth.** It records what a session *said*, not what
was true. A row asserting a gate is green is evidence that a claim was made, at a time, by
a session — the same corpus contains the corrections of several such claims. Use it to find
where to look, then measure the artefact.

## Query examples

### Full-text search across the transcript

```sql
SELECT ord, ts, content_kind, substr(content, 1, 70) AS snippet
FROM read_parquet('logs/parquet/*.parquet')
WHERE content ILIKE '%vaccine%'
ORDER BY ord
LIMIT 5;
```

```
┌───────┬──────────────────────┬──────────────┬──────────────────────────────────────────────────────────────────────┐
│  ord  │          ts          │ content_kind │                               snippet                                │
├───────┼──────────────────────┼──────────────┼──────────────────────────────────────────────────────────────────────┤
│   638 │ 2026-09-02 18:57:3…  │ tool_result  │ ---\r\nname: globalgrid2050-homepage-governance\r\ndescription: Rule…│
│  2289 │ 2026-09-03 01:17:3…  │ tool_result  │ === cvaa ===\nc18cc13 202609012310: a vaccine CVAA cannot yet carry,…│
│  2298 │ 2026-09-03 01:17:3…  │ tool_use     │ {"command": "cd /c/Users/vikra/OneDrive/Documents/GitHub/cvaa && echo│
│  2299 │ 2026-09-03 01:17:4…  │ tool_result  │ === cvaa.json ===\n{\r\n  "legacy_workflows": 2,\r\n  "allow": [\r\n…│
│  2302 │ 2026-09-03 01:17:5…  │ text         │ CVAA is exactly the right substrate — 28 named vaccines, `immune`/`WA│
└───────┴──────────────────────┴──────────────┴──────────────────────────────────────────────────────────────────────┘
```

To search only what was actually said, add `AND content_kind IN ('text', 'thinking')`.

### Filter by role

```sql
SELECT role, content_kind, count(*) AS rows
FROM read_parquet('logs/parquet/*.parquet')
WHERE role IS NOT NULL
GROUP BY role, content_kind
ORDER BY role, rows DESC;
```

```
┌───────────┬──────────────┬───────┐
│   role    │ content_kind │ rows  │
├───────────┼──────────────┼───────┤
│ assistant │ tool_use     │   649 │
│ assistant │ thinking     │   478 │
│ assistant │ text         │   338 │
│ user      │ tool_result  │   649 │
│ user      │ text         │    71 │
└───────────┴──────────────┴───────┘
```

Tool results are carried on `user` rows by the protocol. That is why `role` alone is not
enough and `content_kind` exists.

### Filter by tool name

```sql
SELECT tool_name,
       count(*) FILTER (WHERE content_kind = 'tool_use')             AS calls,
       count(*) FILTER (WHERE is_error)                              AS errors,
       sum(content_len) FILTER (WHERE content_kind = 'tool_result')  AS result_chars
FROM read_parquet('logs/parquet/*.parquet')
WHERE tool_name IS NOT NULL
GROUP BY tool_name
ORDER BY calls DESC
LIMIT 8;
```

```
┌────────────────────────────────────────┬───────┬────────┬──────────────┐
│               tool_name                │ calls │ errors │ result_chars │
├────────────────────────────────────────┼───────┼────────┼──────────────┤
│ Bash                                   │   460 │     16 │       521983 │
│ Write                                  │    48 │      0 │        10023 │
│ SendMessage                            │    27 │      0 │         4622 │
│ Edit                                   │    26 │      2 │         5916 │
│ mcp__claude-in-chrome__javascript_tool │    19 │      0 │        13130 │
│ Agent                                  │    11 │      0 │        11704 │
│ mcp__claude-in-chrome__navigate        │     9 │      2 │         4430 │
│ mcp__claude-in-chrome__computer        │     9 │      0 │         3001 │
└────────────────────────────────────────┴───────┴────────┴──────────────┘
```

Every failed tool call in the session, in order:

```sql
SELECT ord, ts, tool_name, substr(replace(content, chr(10), ' '), 1, 80) AS err
FROM read_parquet('logs/parquet/*.parquet')
WHERE is_error
ORDER BY ord;
```

### Filter by time range

```sql
SELECT date_trunc('hour', ts) AS hour, count(*) AS rows
FROM read_parquet('logs/parquet/*.parquet')
WHERE ts BETWEEN TIMESTAMPTZ '2026-09-03 00:00:00+00'
             AND TIMESTAMPTZ '2026-09-03 04:00:00+00'
GROUP BY hour
ORDER BY hour;
```

```
┌──────────────────────────┬───────┐
│           hour           │ rows  │
├──────────────────────────┼───────┤
│ 2026-09-03 00:00:00+00   │   140 │
│ 2026-09-03 01:00:00+00   │   463 │
│ 2026-09-03 02:00:00+00   │   303 │
│ 2026-09-03 03:00:00+00   │   387 │
└──────────────────────────┴───────┘
```

### Reconstruct a readable slice of the conversation, in order

```sql
SELECT ord, role, content_kind, coalesce(tool_name, '') AS tool,
       substr(replace(content, chr(10), ' '), 1, 58) AS text
FROM read_parquet('logs/parquet/*.parquet')
WHERE content_kind IN ('text', 'thinking', 'tool_use')
  AND role IS NOT NULL
  AND ord BETWEEN 485 AND 495
ORDER BY ord;
```

```
┌───────┬───────────┬──────────────┬─────────┬────────────────────────────────────────────────────────────┐
│  ord  │   role    │ content_kind │  tool   │                            text                            │
├───────┼───────────┼──────────────┼─────────┼────────────────────────────────────────────────────────────┤
│   485 │ user      │ text         │         │ show the dashboard again i lost it                         │
│   488 │ assistant │ text         │         │ **GlobalGrid2050 Build Telemetry** — https://claude.ai/cod │
│   493 │ user      │ text         │         │ its too complicated, stick to dark terminal theme and list │
└───────┴───────────┴──────────────┴─────────┴────────────────────────────────────────────────────────────┘
```

Drop `substr(...)` for the full text. To dump a readable stretch to a file:

```sql
COPY (
  SELECT ord, ts, role, content_kind, tool_name, content
  FROM read_parquet('logs/parquet/*.parquet')
  WHERE content_kind IN ('text', 'thinking')
  ORDER BY ord
) TO 'slice.csv' (HEADER, DELIMITER ',');
```

Order by `ord`, never by `ts` — 1,443 rows have no timestamp.

## Adding the next session

**One command per session.** The converter takes an input JSONL and an output Parquet path
and prints its own reconciliation. Session JSONLs live under
`C:\Users\vikra\.claude\projects\<project>\<session-uuid>.jsonl`, where `<project>` is one
of `C--Users-vikra`, `C--Users-vikra-OneDrive-Documents-GitHub`, `C--Windows-system32`.

```bash
cd C:/Users/vikra/OneDrive/Documents/GitHub/claude
pip install duckdb pyarrow          # once

python logs/tools/jsonl_to_parquet.py \
  "C:/Users/vikra/.claude/projects/C--Users-vikra/<session-uuid>.jsonl" \
  "logs/parquet/session_<first-8-of-uuid>.parquet"
```

`project` defaults to the input file's parent directory name and `session_id` falls back to
its filename stem, which is right when reading the live location. Pass `--project NAME` and
`--session UUID` when converting a **snapshot copy** whose filename is not the bare uuid —
otherwise the fallback writes the snapshot's filename into `session_id` and the store
appears to contain more sessions than it does. (That happened on the first build of this
store: 22 sessions reported where there were 11.)

To rebuild the entire store — all sessions, every project directory:

```bash
for d in C--Users-vikra C--Users-vikra-OneDrive-Documents-GitHub C--Windows-system32; do
  for f in "C:/Users/vikra/.claude/projects/$d"/*.jsonl; do
    u=$(basename "$f" .jsonl)
    python logs/tools/jsonl_to_parquet.py "$f" "logs/parquet/session_${u:0:8}.parquet" \
      --project "$d" --session "$u"
  done
done
```

Real output from one session of the run that produced this store:

```
source JSONL bytes   : 11796003
parquet bytes        : 781239
compression ratio    : 15.10x
jsonl lines          : 5159 (blank skipped: 0)
parquet rows         : 5159
distinct source_line : 5159
lines reconciled     : True
unparseable lines    : 0 []
redactions           : 0 {}
rows by sensitivity  : {"ok": 5159}
rows by content_kind : {"attachment": 822, "meta": 2043, "system": 82, "text": 419, "thinking": 485, "tool_result": 654, "tool_use": 654}
audit written        : logs\reports\session_5b94bee7_audit.json
```

**Converting the session you are running in.** Its JSONL grows while you read it. Copy it
first, convert the copy, and record the line count you converted — otherwise the row count
in the audit describes a file that no longer exists.

Then confirm the readback before committing — **a successful write is not the proof**:

```sql
SELECT count(*) AS rows, count(DISTINCT source_line) AS lines, min(ts), max(ts)
FROM read_parquet('logs/parquet/session_<first-8-of-uuid>.parquet');
```

`lines` must equal the `jsonl lines` the converter printed, and the timestamps must match
the first and last `timestamp` in the JSONL. `rows` may exceed `lines` where a line carried
several content blocks; `lines` is the reconciliation key, not `rows`.

Run the classifier's self-test too, whenever the rule is touched:

```bash
python logs/tools/classify_sensitivity.py
```

And run the store-wide verifier, which reconciles **every** parquet against the audit
record written beside it and exits non-zero on any mismatch:

```bash
python logs/tools/verify_memory_store.py
```

```
logs/parquet/session_0e09c52a.parquet  0e09c52a  118        118    118       35,288     OK
logs/parquet/session_9556e57d.parquet  9556e57d  2356       2360   2356      1,320,265  OK
logs/parquet/session_fe663175.parquet  fe663175  11230      11236  11230     3,719,628  OK
...
11 session(s); 30,684 rows from 30,674 source lines

the store holds every line every audit record claims for it
```

30,684 rows from 30,674 source lines — the 10-row surplus is the multi-block grain, in the
two sessions with image blocks, and the verifier deliberately does **not** assert
`rows == source_lines` for exactly that reason.

Stage by explicit path. Several agents write to this repo:

```bash
git add logs/parquet/session_<first-8-of-uuid>.parquet \
        logs/reports/session_<first-8-of-uuid>_audit.json
```

There is no append step. Each session is its own file and the `*.parquet` glob unions
them, which means re-running a session is idempotent — it overwrites one file and touches
nothing else. Re-running is also byte-stable: no run timestamp or run id is written into
the Parquet.

### Redaction

The converter replaces credential **values** with `[REDACTED CREDENTIAL]` before writing:
`github_pat_…`, the `ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_` token family, the token after
`Authorization: Bearer`, and the value after `password=`. Paths, SHAs, emails, repo names
and URLs are left alone.

**Across all eleven transcripts the redaction count is 0**, and that zero was checked
rather than assumed. An independent sweep of all 85,381,636 source bytes — before
conversion, against the raw JSONL — looked for thirteen credential shapes and found none:
`github_pat_`, the `gh[pousr]_` family, `Authorization: Bearer`, `password=`, `sk-ant-`,
OpenAI `sk-…`, AWS `AKIA…`, Google `AIza…`, Slack `xox[baprs]-`, `-----BEGIN … PRIVATE
KEY-----`, `npm_…`, and basic-auth credentials embedded in a URL.

That is a real result rather than a lucky one: this estate's standing rule is that the
GitHub token lives in one variable for one `curl`, is never echoed and never written to
disk, and the transcripts show that rule holding for four days.

A looser earlier `password=` rule (any 3+ non-space run) fired 5 times on shell text —
`sed -n 's/^password=\(.*\)/\1/p'` inside a `git credential fill` pipeline — and would have
redacted a *command*, not a secret. The rule now requires 8+ characters from a
credential-shaped character class that excludes backslashes, parens and quotes. Six such
fragments exist in this transcript; none is a credential.

## Why Parquet, and why not GeoJSON

**Parquet** is columnar. `WHERE tool_name = 'Bash'` reads the `tool_name` column and the
row groups its statistics say could match — it does not touch `content` at all. In JSONL
or Markdown every question costs a full scan.

**ZSTD** does the work on `content`, which is unique prose and shell output and has no
structure left to exploit. It is a good general compressor at a reasonable speed; there is
no trick here, just a better algorithm than none.

**Dictionary encoding** is where the structured columns collapse. Across the whole
30,684-row store `entry_type` has 17 distinct values, `cwd` 160, `cli_version` 4,
`session_id` 11 and `project` 3 — and within any one file most are constant. The source
JSONL repeats all of them on every line. Stored as a dictionary plus RLE indices they cost
a few hundred bytes per file instead of a few hundred kilobytes. That, not the prose, is
most of the ratio against JSONL — which is why the honest number against the Markdown
rendering of a session is the smaller 9.1x.

`sensitivity` is the extreme case and the reason it is dictionary-encoded rather than left
plain: one distinct value in ten of the eleven files, two in the eleventh.

**GeoJSON is not used here and would be a mistake.** It is a spatial container: its schema
is `Feature` objects each carrying a `geometry` and a `properties` bag. A transcript has no
geometry. Storing it as GeoJSON would mean a null or dummy geometry on every one of 30,684
features, JSON text rather than typed columns, no compression, no column pruning and no
predicate pushdown — larger than the JSONL it came from and slower to query than the
Markdown. GeoJSON is the right container in this estate for site and grid features; it is
the wrong one for a conversation.

## Reproducing the audit

`logs/reports/session_<short>_audit.json` — one per session, eleven of them — is written by
the converter on every run and records the project and session id, source bytes, Parquet
bytes, ratio, first and last timestamp, line and row counts, the reconciliation flag, any
unparseable lines **with their line numbers**, per-kind row counts, redaction counts, rows
by sensitivity, the flagged percentage, and every flagged row with its reason and a
300-character snippet. It is the machine-readable form of everything asserted above.

To check the whole store's audit trail at once:

```bash
python -c "import json,glob; [print(f, json.load(open(f))['lines_reconciled'], json.load(open(f))['unparseable_lines']) for f in sorted(glob.glob('logs/reports/*_audit.json'))]"
```

All eleven report `True` and `[]`.

---

## What is required, and what checks it

Everything above describes *how* the store is built and queried. This section is the part
that is not optional.

**A session is not closed until it is in the store and the store has been verified.**
Converting a transcript is half the job; a conversion nobody reconciled is a claim, not a
record. The failure this guards against is not a crash — it is a store that answers every
query while holding less than it should, because the rows that are missing are exactly the
rows nothing asks about.

Three requirements, in order:

1. **Convert the session.** `logs/tools/jsonl_to_parquet.py` writes the Parquet and its
   `logs/reports/session_<short>_audit.json` beside it.
2. **Verify, and regenerate the manifest.** This must exit 0:

   ```bash
   python logs/tools/verify_memory_store.py
   ```

   It reads every Parquet with DuckDB, reconciles each against its audit record — rows,
   distinct source lines, byte size, and that `source_line` runs 1..N with no gaps — and
   rewrites `logs/reports/memory-manifest.json`. Any mismatch is a non-zero exit.
3. **Commit the regenerated manifest with the Parquet.** The manifest is derived state. A
   store whose manifest was not regenerated fails CI on the next push.

### The checks, and what each one can see

```bash
python logs/tools/verify_memory_store.py --check          # writes nothing; what CI runs
python logs/tools/verify_memory_store.py --transcripts ~/.claude/projects
pip install -r requirements.txt                           # duckdb 1.3.2, pyarrow 25.0.1
```

`--check` validates the committed manifest instead of rewriting it, so a **stale** manifest
fails rather than being silently refreshed. It is what
`.github/workflows/202609031030-verify-memory-store.yml` runs on every push touching
`logs/`, on pull requests, and on cron every six hours. That workflow is the loop.

`--transcripts` is the only check that can see a session which was **never converted at
all** — the manifest-based checks compare the store against what the store claims, which
cannot reveal an absence. It compares against what exists outside the store, so CI cannot
run it: a runner has no access to `~/.claude/projects`. Run it locally before closing a
session. Measured here: 34 transcripts on disk, 11 sessions, 23 subagent `agent-*`
sidechains that are outside scope and are reported rather than failed.

Repo-external enforcement lives in `Ventusltd/cvaa` as the vaccine
**`memory-store-complete`**, which reads `memory-manifest.json` structurally and asserts
that every session's `distinct_source_lines` equals its `source_lines`, that no session has
zero rows, that every `parquet_file` named exists, and that `generation` is a 12-digit UTC
stamp. If the manifest is absent while `logs/parquet/` holds files, it returns a **skip**
naming what it needs — not `immune`, which it has not earned.

**It does not assert `rows == source_lines`, and neither should anything else.** One
transcript line carrying three images and a caption becomes four rows; `fe663175` and
`9556e57d` are complete at 11236/11230 and 2360/2356. The reconciliation key is
`count(DISTINCT source_line)`, as the section above sets out. A check written against the
row count would fail forever on a healthy store, and the only way to satisfy it would be to
make the converter throw content blocks away.
