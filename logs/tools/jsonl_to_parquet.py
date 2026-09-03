#!/usr/bin/env python
"""Convert a Claude Code session JSONL transcript into a compact, queryable Parquet file.

House conventions borrowed from Ventusltd/data-gb-electricity:
  - Parquet, zstd compression, no raw source committed alongside.
  - A machine-readable audit JSON written to a reports/ directory next to the data.
  - Verification is a read-back, not a successful write.

Grain: one row per *content block*, not one row per JSONL line. Every input line
produces at least one row, so `count(DISTINCT source_line)` reconciles exactly
against the input line count. Assistant turns that carry several blocks
(thinking + tool_use + text) become several rows, which is the whole point:
a query can filter to `content_kind = 'text'` without scanning tool payloads.

Usage:
    python logs/tools/jsonl_to_parquet.py <input.jsonl> <output.parquet> [--project NAME] [--session UUID]

Idempotent: rerunning over the same input rewrites the same output byte-for-byte
(no timestamps or run ids are embedded in the Parquet), and rewrites the audit JSON.

CROSS-SESSION STORE. Every session on this machine converts into its own Parquet in
logs/parquet/, and `read_parquet('logs/parquet/*.parquet')` unions them. Three columns
beyond the original 22 make a row attributable and filterable across that union:

    project              the Claude Code project directory the transcript came from,
                         e.g. `C--Users-vikra`. Defaults to the input file's parent
                         directory name; override with --project.
    sensitivity          ok | opinion_about_person | credential  (see classify_sensitivity)
    sensitivity_reason   short free text, empty when ok

Nothing is ever dropped. The `memory` view documented in logs/README.md selects
`WHERE sensitivity = 'ok'`, so the safe set is the default and the raw union stays
reachable for audit.

`session_id` is taken from the JSONL line as before, and falls back to the source
file's own session uuid when a bookkeeping line carries none -- otherwise a third of
the rows in the union would be unattributable to a session.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classify_sensitivity as sens  # noqa: E402

# ---------------------------------------------------------------------------
# Redaction. Credential VALUES only. Paths, SHAs, emails, repo names are kept.
# ---------------------------------------------------------------------------

REDACTED = "[REDACTED CREDENTIAL]"

REDACTION_PATTERNS = [
    ("github_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("bearer", re.compile(r"(?i)(Authorization\s*:\s*Bearer\s+)([A-Za-z0-9._\-+/=]{8,})")),
    # The value class here deliberately excludes backslashes, parens and quotes, and
    # demands 8+ characters. A looser rule (any 3+ non-space run) fires on shell text
    # like  sed -n 's/^password=\(.*\)/\1/p'  and redacts a *command*, not a secret.
    # Six such fragments exist in this transcript; none is a credential.
    ("password_kv", re.compile(r"(?i)(password\s*=\s*)([A-Za-z0-9_\-+/=.~!@#$%^&:]{8,})")),
]

_redaction_counts: Counter = Counter()


def redact(text):
    """Return (text, hits). `hits` names the patterns that fired, so the row can be
    labelled `credential` and the audit can say which rule matched."""
    if not text:
        return text, []
    hits = []
    for name, rx in REDACTION_PATTERNS:
        if rx.groups >= 2:
            text, n = rx.subn(lambda m: m.group(1) + REDACTED, text)
        else:
            text, n = rx.subn(REDACTED, text)
        if n:
            _redaction_counts[name] += n
            hits.extend([name] * n)
    return text, hits


# ---------------------------------------------------------------------------
# Content extraction
# ---------------------------------------------------------------------------

# Metadata line kinds whose useful payload is a single short string.
META_TEXT_FIELDS = {
    "ai-title": "aiTitle",
    "last-prompt": "lastPrompt",
    "mode": "mode",
    "permission-mode": "permissionMode",
    "atis-latch": "atis",
    "queue-operation": "content",
    "file-history-delta": "trackingPath",
    "frame-link": "frameUrl",
}


def flatten_tool_result(content):
    """tool_result content is a str, or a list of {text|image|tool_reference} blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if not isinstance(b, dict):
                parts.append(str(b))
            elif b.get("type") == "text":
                parts.append(b.get("text") or "")
            elif b.get("type") == "image":
                src = b.get("source") or {}
                parts.append("[image %s]" % (src.get("media_type") or "unknown"))
            else:
                parts.append("[%s]" % b.get("type", "block"))
        return "\n".join(p for p in parts if p)
    if content is None:
        return None
    return json.dumps(content, ensure_ascii=False, sort_keys=True)


def attachment_text(att):
    """Attachments carry their payload under one of a handful of keys."""
    for key in ("text", "content", "prompt", "snippet", "description"):
        v = att.get(key)
        if isinstance(v, str) and v:
            return v
    return None


def convert(jsonl_path: Path, out_path: Path, project=None, session=None):
    global _redaction_counts
    _redaction_counts = Counter()   # per-run, so a batch does not accumulate across sessions

    rows = []
    tool_names = {}          # tool_use_id -> tool name, so tool_result rows get a name too
    line_count = 0
    blank_lines = 0
    bad_lines = []           # (line_no, error)
    kind_counts = Counter()
    type_counts = Counter()
    sens_counts = Counter()
    flagged = []             # (source_line, sensitivity, reason, snippet) for the audit
    ordinal = 0

    if project is None:
        project = jsonl_path.parent.name
    # Bookkeeping lines carry no sessionId; fall back to the file's own uuid so every
    # row in the cross-session union is attributable. Pass --session when the input is
    # a snapshot copy whose filename is not the bare session uuid.
    session_fallback = session or jsonl_path.stem

    def emit(**kw):
        nonlocal ordinal
        content = kw.get("content")
        content, hits = redact(content)
        kw["content"] = content
        kw["redacted"] = bool(hits)
        kw["content_len"] = len(content) if content is not None else 0
        kw["ord"] = ordinal
        kw["project"] = project
        if not kw.get("session_id"):
            kw["session_id"] = session_fallback
        label, reason = sens.classify(content, hits)
        kw["sensitivity"] = label
        kw["sensitivity_reason"] = reason
        sens_counts[label] += 1
        if label != sens.OK:
            snippet = (content or "")[:300].replace("\n", " ")
            flagged.append((kw["source_line"], label, reason, snippet))
        ordinal += 1
        kind_counts[kw["content_kind"]] += 1
        rows.append(kw)

    with io.open(jsonl_path, "r", encoding="utf-8", errors="replace") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                blank_lines += 1
                continue
            line_count += 1
            try:
                obj = json.loads(line)
            except Exception as exc:  # noqa: BLE001 - record and continue, never abort
                bad_lines.append((line_no, str(exc)[:200]))
                emit(
                    source_line=line_no, block_no=0, ts=None, entry_type="unparseable",
                    subtype=None, role=None, content_kind="unparseable", tool_name=None,
                    tool_use_id=None, is_error=None, model=None, uuid=None,
                    parent_uuid=None, session_id=None, cwd=None, git_branch=None,
                    cli_version=None, is_sidechain=None, content=None,
                )
                continue

            etype = obj.get("type") or "unknown"
            type_counts[etype] += 1
            base = dict(
                source_line=line_no,
                ts=obj.get("timestamp"),
                entry_type=etype,
                subtype=obj.get("subtype"),
                uuid=obj.get("uuid"),
                parent_uuid=obj.get("parentUuid"),
                session_id=obj.get("sessionId") or obj.get("session_id"),
                cwd=obj.get("cwd"),
                git_branch=obj.get("gitBranch"),
                cli_version=obj.get("version"),
                is_sidechain=obj.get("isSidechain"),
            )

            msg = obj.get("message")
            if isinstance(msg, dict):
                role = msg.get("role")
                model = msg.get("model")
                content = msg.get("content")

                if isinstance(content, str):
                    emit(block_no=0, role=role, model=model, content_kind="text",
                         tool_name=None, tool_use_id=None, is_error=None,
                         content=content, **base)
                    continue

                if isinstance(content, list):
                    if not content:
                        emit(block_no=0, role=role, model=model, content_kind="empty",
                             tool_name=None, tool_use_id=None, is_error=None,
                             content=None, **base)
                        continue
                    for block_no, blk in enumerate(content):
                        if not isinstance(blk, dict):
                            emit(block_no=block_no, role=role, model=model,
                                 content_kind="text", tool_name=None, tool_use_id=None,
                                 is_error=None, content=str(blk), **base)
                            continue
                        btype = blk.get("type")
                        if btype == "text":
                            emit(block_no=block_no, role=role, model=model,
                                 content_kind="text", tool_name=None, tool_use_id=None,
                                 is_error=None, content=blk.get("text"), **base)
                        elif btype == "thinking":
                            emit(block_no=block_no, role=role, model=model,
                                 content_kind="thinking", tool_name=None,
                                 tool_use_id=None, is_error=None,
                                 content=blk.get("thinking"), **base)
                        elif btype == "tool_use":
                            tuid = blk.get("id")
                            name = blk.get("name")
                            if tuid:
                                tool_names[tuid] = name
                            emit(block_no=block_no, role=role, model=model,
                                 content_kind="tool_use", tool_name=name,
                                 tool_use_id=tuid, is_error=None,
                                 content=json.dumps(blk.get("input"),
                                                    ensure_ascii=False, sort_keys=True),
                                 **base)
                        elif btype == "tool_result":
                            tuid = blk.get("tool_use_id")
                            emit(block_no=block_no, role=role, model=model,
                                 content_kind="tool_result",
                                 tool_name=tool_names.get(tuid),
                                 tool_use_id=tuid, is_error=blk.get("is_error"),
                                 content=flatten_tool_result(blk.get("content")), **base)
                        else:
                            emit(block_no=block_no, role=role, model=model,
                                 content_kind=btype or "unknown_block", tool_name=None,
                                 tool_use_id=None, is_error=None,
                                 content=json.dumps(blk, ensure_ascii=False,
                                                    sort_keys=True), **base)
                    continue

                # message present but content is neither str nor list
                emit(block_no=0, role=role, model=model, content_kind="empty",
                     tool_name=None, tool_use_id=None, is_error=None, content=None,
                     **base)
                continue

            if etype == "attachment":
                att = obj.get("attachment") or {}
                base["subtype"] = att.get("type")
                base["ts"] = obj.get("timestamp")
                emit(block_no=0, role=None, model=None, content_kind="attachment",
                     tool_name=None, tool_use_id=att.get("toolUseID"), is_error=None,
                     content=attachment_text(att), **base)
                continue

            if etype == "system":
                emit(block_no=0, role=None, model=None, content_kind="system",
                     tool_name=None, tool_use_id=None, is_error=None,
                     content=obj.get("content"), **base)
                continue

            # Everything else is session bookkeeping. Keep the row (so line counts
            # reconcile) but store only a short field, never a whole snapshot blob.
            field = META_TEXT_FIELDS.get(etype)
            val = obj.get(field) if field else None
            emit(block_no=0, role=None, model=None, content_kind="meta",
                 tool_name=None, tool_use_id=None, is_error=None,
                 content=val if isinstance(val, str) else None, **base)

    table = build_table(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        table,
        out_path,
        compression="zstd",
        compression_level=9,
        use_dictionary=DICT_COLUMNS,
        write_statistics=True,
        row_group_size=8192,
        version="2.6",
        data_page_version="2.0",
    )
    return table, dict(
        line_count=line_count,
        blank_lines=blank_lines,
        bad_lines=bad_lines,
        kind_counts=dict(kind_counts),
        type_counts=dict(type_counts),
        redaction_counts=dict(_redaction_counts),
        sens_counts=dict(sens_counts),
        flagged=flagged,
        project=project,
    )


SCHEMA = pa.schema([
    ("ord", pa.int64()),
    ("source_line", pa.int32()),
    ("block_no", pa.int32()),
    ("ts", pa.timestamp("us", tz="UTC")),
    ("entry_type", pa.string()),
    ("subtype", pa.string()),
    ("role", pa.string()),
    ("content_kind", pa.string()),
    ("tool_name", pa.string()),
    ("tool_use_id", pa.string()),
    ("is_error", pa.bool_()),
    ("model", pa.string()),
    ("uuid", pa.string()),
    ("parent_uuid", pa.string()),
    ("session_id", pa.string()),
    ("cwd", pa.string()),
    ("git_branch", pa.string()),
    ("cli_version", pa.string()),
    ("is_sidechain", pa.bool_()),
    ("redacted", pa.bool_()),
    ("content_len", pa.int32()),
    ("content", pa.string()),
    # --- cross-session additions. Appended, so the original 22 keep their order. ---
    ("project", pa.string()),
    ("sensitivity", pa.string()),
    ("sensitivity_reason", pa.string()),
])

# Low-cardinality columns. `content` and `sensitivity_reason` are deliberately absent:
# one is high-cardinality prose, the other is empty on all but a handful of rows.
DICT_COLUMNS = [
    "entry_type", "subtype", "role", "content_kind",
    "tool_name", "model", "session_id", "cwd", "git_branch", "cli_version",
    "project", "sensitivity",
]


def build_table(rows):
    cols = {}
    for field in SCHEMA:
        name = field.name
        values = [r.get(name) for r in rows]
        if name == "ts":
            # timestamps arrive as ISO-8601 strings; cast once, keep UTC.
            cols[name] = pa.array(
                [v if isinstance(v, str) else None for v in values], type=pa.string()
            ).cast(pa.timestamp("us", tz="UTC"))
        else:
            cols[name] = pa.array(values, type=field.type)
    return pa.table(cols, schema=SCHEMA)


def main(argv):
    argv = list(argv)
    project = None
    session = None
    if "--project" in argv:
        i = argv.index("--project")
        project = argv[i + 1]
        del argv[i:i + 2]
    if "--session" in argv:
        i = argv.index("--session")
        session = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) != 3:
        print(__doc__)
        return 2
    jsonl_path = Path(argv[1])
    out_path = Path(argv[2])
    if not jsonl_path.is_file():
        print("input not found: %s" % jsonl_path)
        return 1

    table, stats = convert(jsonl_path, out_path, project=project, session=session)

    src_bytes = jsonl_path.stat().st_size
    out_bytes = out_path.stat().st_size
    distinct_lines = len(set(table.column("source_line").to_pylist()))

    ts_vals = [t for t in table.column("ts").to_pylist() if t is not None]

    audit = {
        "source_jsonl": jsonl_path.name,
        "output_parquet": out_path.name,
        "project": stats["project"],
        "session_id": session or jsonl_path.stem,
        "first_ts": min(ts_vals).isoformat() if ts_vals else None,
        "last_ts": max(ts_vals).isoformat() if ts_vals else None,
        "source_bytes": src_bytes,
        "parquet_bytes": out_bytes,
        "compression_ratio": round(src_bytes / out_bytes, 3) if out_bytes else None,
        "jsonl_lines": stats["line_count"],
        "blank_lines_skipped": stats["blank_lines"],
        "parquet_rows": table.num_rows,
        "distinct_source_lines": distinct_lines,
        "lines_reconciled": distinct_lines == stats["line_count"],
        "unparseable_lines": [{"line": n, "error": e} for n, e in stats["bad_lines"]],
        "rows_by_content_kind": stats["kind_counts"],
        "lines_by_entry_type": stats["type_counts"],
        "redactions": stats["redaction_counts"],
        "redaction_total": sum(stats["redaction_counts"].values()),
        "rows_by_sensitivity": stats["sens_counts"],
        "flagged_rows": [
            {"source_line": ln, "sensitivity": lab, "reason": why, "snippet": snip}
            for ln, lab, why, snip in stats["flagged"]
        ],
        "flagged_pct": round(
            100.0 * (table.num_rows - stats["sens_counts"].get("ok", 0)) / table.num_rows, 4
        ) if table.num_rows else 0.0,
        "compression": "zstd level 9",
        "dictionary_encoded": DICT_COLUMNS,
        "row_group_size": 8192,
    }

    reports_dir = out_path.parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    audit_path = reports_dir / (out_path.stem + "_audit.json")
    with io.open(audit_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(audit, indent=2, sort_keys=True) + "\n")

    print("source JSONL bytes   : %d" % src_bytes)
    print("parquet bytes        : %d" % out_bytes)
    print("compression ratio    : %.2fx" % (src_bytes / out_bytes))
    print("jsonl lines          : %d (blank skipped: %d)" % (stats["line_count"], stats["blank_lines"]))
    print("parquet rows         : %d" % table.num_rows)
    print("distinct source_line : %d" % distinct_lines)
    print("lines reconciled     : %s" % (distinct_lines == stats["line_count"]))
    print("unparseable lines    : %d %s" % (len(stats["bad_lines"]), stats["bad_lines"][:5]))
    print("redactions           : %d %s" % (sum(stats["redaction_counts"].values()), dict(stats["redaction_counts"])))
    print("rows by sensitivity  : %s" % json.dumps(stats["sens_counts"], sort_keys=True))
    print("rows by content_kind : %s" % json.dumps(stats["kind_counts"], sort_keys=True))
    print("audit written        : %s" % audit_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
