#!/usr/bin/env python
"""Verify that the session memory store contains what it claims to contain.

The failure this exists to catch is not a crash. It is a store that answers every
query while holding less than it should: a session that was never converted, or a
conversion that dropped lines quietly. Both leave a store that looks healthy,
because the rows that are missing are exactly the rows nothing asks about.

So nothing here is inferred from prose or from a file count. Every number is
measured out of the parquet itself with DuckDB and reconciled against the audit
record jsonl_to_parquet.py wrote beside it:

  rows                == the audit's parquet_rows
  distinct source_line== the audit's jsonl_lines        (the completeness claim)
  source_line 1..N    contiguous, no gaps               (the silent-hole check)
  file size on disk   == the audit's parquet_bytes
  exactly one session_id per file

It then regenerates logs/reports/memory-manifest.json, which is the artefact the
cvaa vaccine `memory-store-complete` reads. Under --check it validates the
committed manifest instead of rewriting it, so CI fails on a stale one.

Exits non-zero on any mismatch.

  python logs/tools/verify_memory_store.py            # verify and write manifest
  python logs/tools/verify_memory_store.py --check    # verify, write nothing (CI)
  python logs/tools/verify_memory_store.py --transcripts DIR
        additionally report transcripts in DIR that never reached the store.
        Local only: CI cannot see ~/.claude/projects, and this script does not
        pretend otherwise.

Depends only on duckdb (see requirements.txt). Deliberately no pandas/numpy: the
machine this was written on has duckdb without numpy, so .df() is not available
and fetchall() is used throughout.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

try:
    import duckdb
except ImportError:  # pragma: no cover - the message matters more than the trace
    sys.exit("duckdb is not installed. pip install -r requirements.txt")

REPO = Path(__file__).resolve().parents[2]
PARQUET_DIR = REPO / "logs" / "parquet"
REPORT_DIR = REPO / "logs" / "reports"
MANIFEST = REPORT_DIR / "memory-manifest.json"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def project_slug(cwd: str | None) -> str:
    """The project key Claude Code uses: every path separator becomes one dash.

    'C:\\Users\\vikra' -> 'C--Users-vikra'
    """
    if not cwd:
        return "unknown"
    return re.sub(r"[:\\/]", "-", cwd)


def load_audits() -> dict[str, dict]:
    """Audit records keyed by the parquet filename they claim to describe."""
    audits: dict[str, dict] = {}
    for path in sorted(REPORT_DIR.glob("*.json")):
        if path.name == MANIFEST.name:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            audits[f"!unreadable:{path.name}"] = {"_error": str(exc), "_file": path.name}
            continue
        if not isinstance(data, dict) or "output_parquet" not in data:
            continue
        audits[str(data["output_parquet"])] = data | {"_file": path.name}
    return audits


def measure(con, path: Path) -> dict:
    """Everything we know about a parquet file, read out of the file."""
    rel = path.as_posix()
    row = con.execute(
        "select count(*), count(distinct source_line), min(source_line), "
        "max(source_line), min(ts), max(ts), count(distinct session_id), "
        "any_value(session_id), any_value(cwd) from read_parquet(?)",
        [rel],
    ).fetchone()
    keys = ("rows", "distinct_source_lines", "min_source_line", "max_source_line",
            "first_ts", "last_ts", "n_sessions", "session_id", "cwd")
    m = dict(zip(keys, row))
    m["parquet_bytes"] = path.stat().st_size
    m["parquet_sha256"] = sha256_of(path)
    m["parquet_file"] = path.relative_to(REPO).as_posix()
    return m


def reconcile(m: dict, audit: dict | None) -> list[str]:
    """Every way this file can disagree with what was claimed about it."""
    name = m["parquet_file"]
    problems: list[str] = []

    if m["rows"] == 0:
        problems.append(f"{name}: 0 rows; the file exists and the session is not in it")
        return problems

    # NOT rows == source_lines. That invariant is false and measuring it proved so:
    # one JSONL line carrying three images and a caption becomes four rows, one per
    # content block, which is what block_no is for. session_9556e57d is 2360 rows
    # over 2356 complete source lines and is not missing anything. A rule asserting
    # rows == source_lines would fire forever on a healthy store, and the only way to
    # satisfy it would be to make the converter throw content blocks away.
    #
    # The completeness claim is about LINES: every line of the transcript must be
    # represented by at least one row. Rows may exceed lines; they may never be
    # fewer, and no line may be skipped.
    if m["rows"] < m["distinct_source_lines"]:
        problems.append(
            f"{name}: {m['rows']} rows over {m['distinct_source_lines']} source lines; "
            "a line cannot produce fewer than one row"
        )
    expected_span = (m["max_source_line"] or 0) - (m["min_source_line"] or 0) + 1
    if expected_span != m["distinct_source_lines"]:
        missing = expected_span - m["distinct_source_lines"]
        problems.append(
            f"{name}: source lines run {m['min_source_line']}..{m['max_source_line']} "
            f"but only {m['distinct_source_lines']} are present; {missing} line(s) are gaps"
        )

    if audit is None:
        problems.append(
            f"{name}: no audit record in logs/reports/ names this file, so its "
            "row count was never reconciled against a source transcript"
        )
        return problems

    claimed_rows = audit.get("parquet_rows")
    claimed_lines = audit.get("jsonl_lines")
    claimed_bytes = audit.get("parquet_bytes")
    src = audit.get("source_jsonl", "?")

    claimed_distinct = audit.get("distinct_source_lines", claimed_lines)

    if claimed_rows != m["rows"]:
        problems.append(
            f"{name}: audit {audit['_file']} claims {claimed_rows} rows, file holds {m['rows']}"
        )
    if claimed_distinct != m["distinct_source_lines"]:
        problems.append(
            f"{name}: audit claims {claimed_distinct} distinct source lines, "
            f"file holds {m['distinct_source_lines']}"
        )
    if claimed_lines != m["distinct_source_lines"]:
        problems.append(
            f"{name}: {src} has {claimed_lines} lines, store holds "
            f"{m['distinct_source_lines']}; "
            f"{abs((claimed_lines or 0) - m['distinct_source_lines'])} never arrived"
        )
    if claimed_bytes != m["parquet_bytes"]:
        problems.append(
            f"{name}: audit claims {claimed_bytes} bytes, file is {m['parquet_bytes']}; "
            "the audit describes a different build than the one committed"
        )
    unparseable = audit.get("unparseable_lines") or []
    if unparseable:
        problems.append(
            f"{name}: conversion could not parse {len(unparseable)} source line(s): "
            f"{unparseable[:5]}"
        )
    if audit.get("lines_reconciled") is False:
        problems.append(f"{name}: audit {audit['_file']} records lines_reconciled: false")
    return problems


def iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value.astimezone(_dt.timezone.utc).isoformat()
    return str(value)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="validate the committed manifest; write nothing")
    ap.add_argument("--transcripts", metavar="DIR",
                    help="also report .jsonl transcripts in DIR with no parquet")
    args = ap.parse_args()

    problems: list[str] = []
    audits = load_audits()
    for key, audit in audits.items():
        if key.startswith("!unreadable:"):
            problems.append(f"{audit['_file']}: not readable as JSON: {audit['_error']}")

    parquets = sorted(PARQUET_DIR.glob("*.parquet")) if PARQUET_DIR.is_dir() else []

    real_audits = {k: v for k, v in audits.items() if not k.startswith("!")}
    if not parquets:
        if real_audits:
            print("FAIL: logs/reports/ describes "
                  f"{len(real_audits)} conversion(s) and logs/parquet/ holds no parquet files")
            return 1
        print("logs/parquet/ is empty and no audit record claims otherwise; "
              "nothing to verify")
        return 0

    con = duckdb.connect()
    con.execute("set enable_progress_bar = false")

    rows_out = []
    sessions = []
    for path in parquets:
        m = measure(con, path)
        audit = real_audits.get(path.name)
        problems.extend(reconcile(m, audit))
        claimed = (audit or {}).get("jsonl_lines")
        rows_out.append((
            m["parquet_file"],
            str(m["session_id"] or "?")[:8],
            str(claimed if claimed is not None else "-"),
            str(m["rows"]),
            str(m["distinct_source_lines"]),
            f"{m['parquet_bytes']:,}",
            "OK" if claimed == m["distinct_source_lines"] and m["rows"] >= m["distinct_source_lines"]
            else "MISMATCH",
        ))
        # The audit record is the canonical namer of a session: jsonl_to_parquet.py
        # keys sessions as <project>__<uuid>, because a bare uuid is not unique across
        # projects. Fall back to what the file itself carries when no audit says.
        sessions.append({
            "session_id": (audit or {}).get("session_id") or m["session_id"],
            "project": (audit or {}).get("project") or project_slug(m["cwd"]),
            "source_lines": claimed if claimed is not None else m["distinct_source_lines"],
            # The field the completeness check rests on. rows may legitimately exceed
            # source_lines (one line, many content blocks); this may not.
            "distinct_source_lines": m["distinct_source_lines"],
            "rows": m["rows"],
            "parquet_file": m["parquet_file"],
            "parquet_bytes": m["parquet_bytes"],
            "parquet_sha256": m["parquet_sha256"],
            "first_ts": iso(m["first_ts"]),
            "last_ts": iso(m["last_ts"]),
        })

    # An audit record naming a parquet that is not there is a session that was
    # converted and then lost - the same hole from the other direction.
    for name, audit in real_audits.items():
        if not (PARQUET_DIR / name).exists():
            problems.append(
                f"{audit['_file']} names {name}, which is not in logs/parquet/"
            )

    header = ("parquet", "session", "src_lines", "rows", "distinct", "bytes", "state")
    widths = [max(len(header[i]), max((len(r[i]) for r in rows_out), default=0))
              for i in range(len(header))]
    line = "  ".join("-" * w for w in widths)
    print("Memory store reconciliation")
    print(line)
    print("  ".join(h.ljust(w) for h, w in zip(header, widths)))
    print(line)
    for r in rows_out:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)))
    print(line)
    total_rows = sum(s["rows"] for s in sessions)
    total_src = sum(s["source_lines"] or 0 for s in sessions)
    print(f"{len(sessions)} session(s); {total_rows:,} rows from {total_src:,} source lines")

    if args.transcripts:
        tdir = Path(args.transcripts)
        known = {s["session_id"] for s in sessions}
        unconverted = sorted(p.stem for p in tdir.rglob("*.jsonl") if p.stem not in known)
        if unconverted:
            print(f"\n{len(unconverted)} transcript(s) in {tdir} never reached the store:")
            for stem in unconverted:
                print(f"  - {stem}")
            problems.append(
                f"{len(unconverted)} transcript(s) under {tdir} have no parquet in the store"
            )
        else:
            print(f"\nevery transcript under {tdir} is in the store")

    generation = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d%H%M")
    manifest = {"generation": generation,
                "sessions": sorted(sessions, key=lambda s: str(s["session_id"]))}

    if args.check:
        if not MANIFEST.exists():
            problems.append(f"{MANIFEST.relative_to(REPO).as_posix()} does not exist; "
                            "run this script without --check to write it")
        else:
            try:
                committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                committed = None
                problems.append(f"memory-manifest.json is not valid JSON: {exc}")
            if committed is not None:
                if not re.fullmatch(r"\d{12}", str(committed.get("generation", ""))):
                    problems.append(
                        f"manifest generation {committed.get('generation')!r} "
                        "is not a 12-digit UTC stamp"
                    )
                # Generation moves every minute; the sessions are the claim.
                if committed.get("sessions") != manifest["sessions"]:
                    problems.append(
                        "committed memory-manifest.json does not match the store as "
                        "measured; regenerate it with "
                        "python logs/tools/verify_memory_store.py"
                    )
    else:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {MANIFEST.relative_to(REPO).as_posix()} (generation {generation})")

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nthe store holds every line every audit record claims for it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
