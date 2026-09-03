# logs — the session transcript store

Session transcripts used to arrive here as multi-megabyte Markdown. Markdown is fine to
read and useless to query: to answer "which Bash calls errored" you scan seven megabytes
of prose. This directory holds the same transcripts as **Parquet**, one row per transcript
entry, so a question is a `WHERE` clause instead of a scroll.

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
| audit artefact | `reports/latest_parquet_audit.json` — a machine-readable record of rows, bytes and key checks | `logs/reports/session_5b94bee7_audit.json` |
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
  parquet/session_5b94bee7.parquet       the store
  reports/session_5b94bee7_audit.json    counts, bytes, reconciliation
  tools/jsonl_to_parquet.py              the converter
  202609030940-full-session-5b94bee7.md  Markdown rendering (separate work, left alone)
```

`.gitattributes` at the repo root already carries `*.parquet binary`. That line is
load-bearing: this repo sets `* text=auto eol=lf`, and line-ending translation inside a
Parquet file corrupts it silently and the corruption survives the commit.

## Sizes, measured

Measured 2026-09-03, against session `5b94bee7-197b-4cfd-944b-d4cf3aa02d18` as it stood
at its last row, `2026-09-03 09:43:27.802+00`.

| artefact | bytes | vs Parquet |
|---|---:|---|
| source JSONL (not committed) | 11,650,249 | **15.2x** larger |
| Markdown rendering `202609030940-full-session-5b94bee7.md` | 7,131,299 | **9.3x** larger |
| **`logs/parquet/session_5b94bee7.parquet`** | **765,501** | — |

So the Parquet costs about 750 KB against the Markdown's 7.1 MB, and it is queryable.
That is a real win but a bounded one: the transcript is mostly unique prose and shell
output, which no scheme compresses away. The 15x against JSONL is flattered by the JSONL
repeating a large per-line envelope (`cwd`, `sessionId`, `gitBranch`, `version`, uuids) on
every one of 5,092 lines; dictionary encoding collapses exactly that. The prose itself
compresses at roughly what you would expect from zstd on English and shell output.

## Running the queries

Every query below was executed against `logs/parquet/session_5b94bee7.parquet` and the
output shown under it is real, trimmed only in width. Run them **from the repository
root**, so the relative glob resolves.

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

```sql
SELECT count(*) AS rows,
       count(DISTINCT source_line) AS distinct_source_lines,
       min(ts) AS first_ts,
       max(ts) AS last_ts
FROM read_parquet('logs/parquet/*.parquet');
```

```
┌───────┬───────────────────────┬────────────────────────────┬────────────────────────────┐
│ rows  │ distinct_source_lines │          first_ts          │          last_ts           │
├───────┼───────────────────────┼────────────────────────────┼────────────────────────────┤
│  5092 │                  5092 │ 2026-09-02 18:29:52.377+00 │ 2026-09-03 09:43:27.802+00 │
└───────┴───────────────────────┴────────────────────────────┴────────────────────────────┘
```

The source JSONL had 5,092 non-blank lines, 0 of which failed to parse. Nothing was
dropped. `first_ts` and `last_ts` match the earliest and latest `timestamp` in the source.

## Schema

`DESCRIBE SELECT * FROM read_parquet('logs/parquet/*.parquet');` returns 22 columns.

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
| `session_id` | VARCHAR *(dict)* | Session this row came from. Meaningful once the store holds more than one session. |
| `cwd`, `git_branch`, `cli_version` | VARCHAR *(dict)* | Working directory, branch, and CLI version at the time of the entry. |
| `is_sidechain` | BOOLEAN | True for subagent traffic. |
| `redacted` | BOOLEAN | True if a credential value was replaced in this row's `content`. |
| `content_len` | INTEGER | Character length of `content`, 0 when NULL. Filter on this to find the big payloads without reading them. |
| `content` | VARCHAR | The payload. Prose for `text`/`thinking`; the tool's input as compact JSON for `tool_use`; the flattened result text for `tool_result`. |

*(dict)* marks the ten columns written with dictionary encoding. Verified in the file:
those ten carry `RLE_DICTIONARY` and a dictionary page; `content` deliberately does not,
because it is high-cardinality prose where a dictionary would only add a page.

### What is in there, by kind

```sql
SELECT content_kind, count(*) AS rows, sum(content_len) AS chars
FROM read_parquet('logs/parquet/*.parquet')
GROUP BY content_kind
ORDER BY chars DESC;
```

```
┌──────────────┬───────┬─────────┐
│ content_kind │ rows  │  chars  │
├──────────────┼───────┼─────────┤
│ tool_use     │   649 │ 1064996 │
│ tool_result  │   649 │  598748 │
│ text         │   409 │  472269 │
│ meta         │  2013 │  408940 │
│ attachment   │   815 │  236338 │
│ thinking     │   478 │    6881 │
│ system       │    79 │    2842 │
└──────────────┴───────┴─────────┘
```

Tool traffic is 1.66 M of the 2.79 M characters. Splitting it into its own `content_kind`
is the difference between searching 470 KB of prose and searching the whole transcript.

### Nulls in `ts`

```sql
SELECT entry_type, count(*) AS rows_without_ts
FROM read_parquet('logs/parquet/*.parquet')
WHERE ts IS NULL
GROUP BY entry_type
ORDER BY rows_without_ts DESC;
```

```
┌───────────────────────────┬─────────────────┐
│        entry_type         │ rows_without_ts │
├───────────────────────────┼─────────────────┤
│ ai-title                  │             232 │
│ bridge-session            │             232 │
│ permission-mode           │             232 │
│ mode                      │             232 │
│ atis-latch                │             232 │
│ last-prompt               │             231 │
│ file-history-snapshot     │              33 │
│ artifact-autoreact-ledger │              12 │
│ artifact-comment-monitor  │               7 │
└───────────────────────────┴─────────────────┘
```

1,443 of 5,092 rows have no timestamp because the source line has no `timestamp` field.
These are session bookkeeping, not conversation. They are kept so line counts reconcile,
and they are cheap: `meta` rows store one short field, never the whole snapshot blob.
**Add `WHERE content_kind <> 'meta'` when you want the conversation.**

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

The converter takes an input JSONL and an output Parquet path and prints its own
reconciliation. Session JSONLs live under
`C:\Users\vikra\.claude\projects\C--Users-vikra\<session-uuid>.jsonl`.

```bash
cd C:/Users/vikra/OneDrive/Documents/GitHub/claude
pip install duckdb pyarrow          # once

python logs/tools/jsonl_to_parquet.py \
  "C:/Users/vikra/.claude/projects/C--Users-vikra/<session-uuid>.jsonl" \
  "logs/parquet/session_<first-8-of-uuid>.parquet"
```

Real output from the run that produced this store:

```
source JSONL bytes   : 11650249
parquet bytes        : 765501
compression ratio    : 15.22x
jsonl lines          : 5092 (blank skipped: 0)
parquet rows         : 5092
distinct source_line : 5092
lines reconciled     : True
unparseable lines    : 0 []
redactions           : 0 {}
rows by content_kind : {"attachment": 815, "meta": 2013, "system": 79, "text": 409, "thinking": 478, "tool_result": 649, "tool_use": 649}
audit written        : logs\reports\session_5b94bee7_audit.json
```

Then confirm the readback before committing — **a successful write is not the proof**:

```sql
SELECT count(*) AS rows, count(DISTINCT source_line) AS lines, min(ts), max(ts)
FROM read_parquet('logs/parquet/session_<first-8-of-uuid>.parquet');
```

`rows` must equal `lines` must equal the `jsonl lines` the converter printed, and the
timestamps must match the first and last `timestamp` in the JSONL.

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

For this session the redaction count is **0**, and that zero was checked rather than
assumed: an independent sweep of the source JSONL for `github_pat_`, `gh[pousr]_`,
`Authorization: Bearer`, `sk-ant-` and `AKIA…` returned zero matches for every pattern.

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

**Dictionary encoding** is where the structured columns collapse. `entry_type` has 16
distinct values across 5,092 rows; `cwd`, `session_id`, `git_branch` and `cli_version` are
effectively constant. The source JSONL repeats all of those on every line. Stored as a
dictionary plus RLE indices they cost a few hundred bytes total instead of a few hundred
kilobytes. That, not the prose, is most of the 15x against JSONL — which is why the
honest number against the Markdown rendering is the smaller 9.3x.

**GeoJSON is not used here and would be a mistake.** It is a spatial container: its schema
is `Feature` objects each carrying a `geometry` and a `properties` bag. A transcript has no
geometry. Storing it as GeoJSON would mean a null or dummy geometry on every one of 5,092
features, JSON text rather than typed columns, no compression, no column pruning and no
predicate pushdown — larger than the JSONL it came from and slower to query than the
Markdown. GeoJSON is the right container in this estate for site and grid features; it is
the wrong one for a conversation.

## Reproducing the audit

`logs/reports/session_5b94bee7_audit.json` is written by the converter on every run and
records source bytes, Parquet bytes, ratio, line and row counts, the reconciliation flag,
any unparseable lines with their line numbers, per-kind row counts, and redaction counts.
It is the machine-readable form of everything asserted above.
