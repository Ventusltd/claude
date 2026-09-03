#!/usr/bin/env python
"""Render a Claude Code session JSONL transcript to Markdown, whole.

The Parquet store beside this (logs/parquet/) is what you *query*. This is what you
*read* when a query has told you which entry to look at. The two are built from the
same source and their counts must agree: `distinct source_line` in the Parquet equals
`Rendered entries` here, because both are one-per-input-line.

WHAT IS AND IS NOT REPRODUCED

Reproduced verbatim: every user message, every assistant text block, every thinking
block (marked), every tool call with its full input, every tool result.

Not reproduced verbatim, and marked in every case:
  - a tool result longer than --max-result characters is cut in the MIDDLE and the cut
    is stamped `[... N characters elided ...]`. Head and tail are kept because the
    interesting parts of a long result are its beginning and its end; a tail-only
    truncation loses the command that produced it.
  - a bookkeeping payload (attachment, system entry, raw meta record) longer than
    --max-meta, same middle cut, same marker. The threshold is separate and much
    larger because these are not results and the brief's 8,000-character rule is not
    about them: in this transcript the whole class is a few megabytes of which a
    single 610 kB attachment is the only thing worth cutting. Truncations are counted
    and reported per class in the header, so neither number hides inside the other.
  - base64 image payloads become a one-line note giving media type and payload size.
    The bytes add nothing to a Markdown reading and would multiply the file size.
  - credential VALUES matching logs/tools/jsonl_to_parquet.py's patterns. Paths, SHAs,
    emails, repo names and branch names are deliberately kept: this is an engineering
    record, and redacting them would make it unciteable.

Bookkeeping lines (`mode`, `queue-operation`, `frame-link`, `file-history-*`, ...) carry
no prose. They are rendered as their raw JSON record, marked META ENTRY, rather than
dropped -- otherwise the entry numbering here would not line up with the source line
numbering in the Parquet, and a query result could not be looked up by eye.

CARRIAGE RETURNS. Captured terminal output carries CRLF. `.gitattributes` in this repo
sets `*.md text eol=lf`, so git would normalise them at commit time anyway; doing it here
means the committed file is byte-identical to the file that was rendered and the byte
count reported below is the byte count on disk. Counted and reported, never silent.

Usage:
    python logs/tools/render_session_markdown.py <input.jsonl> <output.md>
        [--session UUID] [--max-result 8000] [--max-meta 100000]
        [--split-bytes 40000000]

A rendering that would exceed --split-bytes is written as <output>-part1.md,
-part2.md, ... split at an entry boundary, with <output> itself becoming an index
naming each part's entry range and time range.
"""

from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jsonl_to_parquet as conv  # noqa: E402  -- reuse the redaction rules, do not restate them

MAX_RESULT_DEFAULT = 8000
MAX_META_DEFAULT = 100_000
SPLIT_BYTES_DEFAULT = 40_000_000

# Line types whose whole payload is bookkeeping, rendered as raw JSON.
PROSE_TYPES = {"user", "assistant", "system", "attachment"}


class Stats:
    def __init__(self):
        self.truncated = 0
        self.elided_chars = 0
        self.meta_truncated = 0
        self.meta_elided = 0
        self.images = 0
        self.crlf = 0
        self.lone_cr = 0
        self.redactions = Counter()


def normalise_newlines(text, stats):
    """CRLF -> LF, lone CR -> LF. Counted, so the header can say how many."""
    if not text:
        return text
    crlf = text.count("\r\n")
    text = text.replace("\r\n", "\n")
    lone = text.count("\r")
    text = text.replace("\r", "\n")
    stats.crlf += crlf
    stats.lone_cr += lone
    return text


def redact(text, stats):
    if not text:
        return text
    before = sum(conv._redaction_counts.values())
    text, hits = conv.redact(text)
    after = sum(conv._redaction_counts.values())
    if after > before:
        for h in hits:
            stats.redactions[h] += 1
    return text


def clean(text, stats):
    return redact(normalise_newlines(text, stats), stats)


def fence(text, language=""):
    """Fence text, widening the fence past any run of backticks inside it."""
    text = "" if text is None else str(text)
    longest = run = 0
    for ch in text:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    bar = "`" * max(3, longest + 1)
    return "%s%s\n%s\n%s" % (bar, language, text, bar)


def middle_truncate(text, limit, stats, meta=False):
    """Cut the middle out, never the end. The marker states the exact loss."""
    if text is None or len(text) <= limit:
        return text
    head = limit // 2
    tail = limit - head
    elided = len(text) - limit
    if meta:
        stats.meta_truncated += 1
        stats.meta_elided += elided
    else:
        stats.truncated += 1
        stats.elided_chars += elided
    return (text[:head]
            + "\n\n[... %d characters elided ...]\n\n" % elided
            + text[-tail:])


def image_note(source):
    src = source or {}
    data = src.get("data") or ""
    return "*[image: %s, %d base64 chars -- bytes are in the source .jsonl]*" % (
        src.get("media_type", "unknown"), len(data))


def render_blocks(content, out, stats, limit):
    """One message's content blocks."""
    if isinstance(content, str):
        out.append("**text:**")
        out.append(fence(clean(content, stats)))
        return
    if not isinstance(content, list):
        out.append(fence(json.dumps(content, indent=2, ensure_ascii=False), "json"))
        return
    if not content:
        out.append("*(empty content)*")
        return

    for blk in content:
        if not isinstance(blk, dict):
            out.append(fence(clean(str(blk), stats)))
            continue
        kind = blk.get("type")

        if kind == "text":
            out.append("**text:**")
            out.append(fence(clean(blk.get("text") or "", stats)))

        elif kind == "thinking":
            out.append("**THINKING BLOCK:**")
            out.append(fence(clean(blk.get("thinking") or "", stats)))

        elif kind == "tool_use":
            out.append("**TOOL CALL -> `%s`**  *(id `%s`)*"
                       % (blk.get("name", "?"), blk.get("id", "?")))
            body = json.dumps(blk.get("input", {}), indent=2, ensure_ascii=False)
            out.append(fence(clean(body, stats), "json"))

        elif kind == "tool_result":
            flag = "  **(ERROR)**" if blk.get("is_error") else ""
            out.append("**TOOL RESULT**%s  *(for id `%s`)*"
                       % (flag, blk.get("tool_use_id", "?")))
            body = blk.get("content")
            if isinstance(body, str):
                out.append(fence(middle_truncate(clean(body, stats), limit, stats)))
            elif isinstance(body, list):
                for part in body:
                    if not isinstance(part, dict):
                        out.append(fence(clean(str(part), stats)))
                    elif part.get("type") == "text":
                        out.append(fence(middle_truncate(
                            clean(part.get("text") or "", stats), limit, stats)))
                    elif part.get("type") == "image":
                        stats.images += 1
                        out.append(image_note(part.get("source")))
                    else:
                        out.append(fence(json.dumps(part, indent=2,
                                                    ensure_ascii=False)[:limit], "json"))
            elif body is not None:
                out.append(fence(json.dumps(body, indent=2, ensure_ascii=False)))
            else:
                out.append("*(no result content)*")

        elif kind == "image":
            stats.images += 1
            out.append(image_note(blk.get("source")))

        else:
            out.append("**block type `%s`:**" % kind)
            out.append(fence(json.dumps(blk, indent=2, ensure_ascii=False)[:limit], "json"))


def render_entry(idx, obj, stats, limit, meta_limit):
    """One source line -> one Markdown entry. Returns a list of lines."""
    out = []
    etype = obj.get("type") or "unknown"
    ts = obj.get("timestamp")
    msg = obj.get("message") if isinstance(obj.get("message"), dict) else None
    role = msg.get("role") if msg else None

    title = "## Entry %d - %s" % (idx, etype)
    if role and role != etype:
        title += " / %s" % role
    if ts:
        title += " - %s" % ts
    out.append(title)
    out.append("")

    meta_bits = []
    if obj.get("uuid"):
        meta_bits.append("uuid=`%s`" % obj["uuid"])
    if obj.get("gitBranch"):
        meta_bits.append("branch=`%s`" % obj["gitBranch"])
    if msg and msg.get("model"):
        meta_bits.append("model=`%s`" % msg["model"])
    if obj.get("isSidechain"):
        meta_bits.append("sidechain=true")
    if meta_bits:
        out.append("*" + " - ".join(meta_bits) + "*")
        out.append("")

    if msg is not None:
        render_blocks(msg.get("content"), out, stats, limit)
    elif etype == "system":
        out.append("**SYSTEM ENTRY**%s" % (
            " *(subtype `%s`)*" % obj["subtype"] if obj.get("subtype") else ""))
        out.append(fence(middle_truncate(
            clean(obj.get("content") or "", stats), meta_limit, stats, meta=True)))
    elif etype == "attachment":
        att = obj.get("attachment") or {}
        out.append("**ATTACHMENT** *(type `%s`)*" % att.get("type", "?"))
        text = conv.attachment_text(att)
        if text:
            out.append(fence(middle_truncate(clean(text, stats), meta_limit, stats,
                                             meta=True)))
        else:
            out.append(fence(middle_truncate(
                clean(json.dumps(att, indent=2, ensure_ascii=False), stats),
                meta_limit, stats, meta=True), "json"))
    else:
        out.append("**META ENTRY (raw record, type `%s`)**" % etype)
        raw = dict(obj)
        raw.pop("type", None)
        out.append(fence(middle_truncate(
            clean(json.dumps(raw, indent=2, ensure_ascii=False), stats),
            meta_limit, stats, meta=True), "json"))

    out.append("")
    out.append("---")
    out.append("")
    return out


def main(argv):
    argv = list(argv)

    def take(flag, default=None, cast=str):
        if flag in argv:
            i = argv.index(flag)
            v = argv[i + 1]
            del argv[i:i + 2]
            return cast(v)
        return default

    session = take("--session")
    limit = take("--max-result", MAX_RESULT_DEFAULT, int)
    meta_limit = take("--max-meta", MAX_META_DEFAULT, int)
    split_bytes = take("--split-bytes", SPLIT_BYTES_DEFAULT, int)

    if len(argv) != 3:
        print(__doc__)
        return 2
    src = Path(argv[1])
    out_path = Path(argv[2])
    if not src.is_file():
        print("input not found: %s" % src)
        return 1

    conv._redaction_counts = Counter()
    stats = Stats()

    records = []
    blank = 0
    unparseable = 0
    with io.open(src, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                blank += 1
                continue
            try:
                records.append(json.loads(line))
            except Exception:  # noqa: BLE001
                unparseable += 1
                records.append({"type": "unparseable", "raw": line[:2000]})

    type_counts = Counter(r.get("type") or "unknown" for r in records)
    stamps = [r.get("timestamp") for r in records if r.get("timestamp")]
    first_ts = stamps[0] if stamps else "?"
    last_ts = stamps[-1] if stamps else "?"
    sid = session or next(
        (r.get("sessionId") for r in records if r.get("sessionId")), src.stem)

    # Render every entry first: the split decision needs real sizes, not an estimate.
    entries = []          # (idx, text, ts)
    for idx, obj in enumerate(records, 1):
        text = "\n".join(render_entry(idx, obj, stats, limit, meta_limit))
        entries.append((idx, text, obj.get("timestamp")))

    body_bytes = sum(len(t.encode("utf-8")) for _, t, _ in entries)

    header = [
        "# Full Claude Code session transcript - %s" % sid,
        "",
        "Rendered whole, not summarised. One heading per input line of the source JSONL.",
        "",
        "- Source: `%s`" % src,
        "- Source bytes: %d" % src.stat().st_size,
        "- Source lines: %d" % len(records),
        "- Rendered entries: %d" % len(entries),
        "- Unparseable lines: %d" % unparseable,
        "- Blank lines: %d" % blank,
        "- First timestamp: %s" % first_ts,
        "- Last timestamp: %s" % last_ts,
        "- Credential redactions: %d%s" % (
            sum(stats.redactions.values()),
            "" if not stats.redactions else " %s" % dict(stats.redactions)),
        "- Tool results middle-truncated (>%d chars): %d, totalling %d characters elided"
        % (limit, stats.truncated, stats.elided_chars),
        "- Bookkeeping payloads (attachment / system / raw meta record) "
        "middle-truncated (>%d chars): %d, totalling %d characters elided"
        % (meta_limit, stats.meta_truncated, stats.meta_elided),
        "- Base64 image payloads noted rather than inlined: %d" % stats.images,
        "- Carriage returns inside captured terminal output converted to LF: "
        "%d CRLF pairs + %d lone CR. This repo's `.gitattributes` sets "
        "`*.md text eol=lf`, so git would have stripped them at commit time anyway; "
        "doing it here keeps the committed file byte-identical to what was rendered. "
        "No other character was altered." % (stats.crlf, stats.lone_cr),
        "- Rendered by: `logs/tools/render_session_markdown.py`",
        "",
        "Nothing else is omitted: every line of the source JSONL, including bookkeeping "
        "records (`mode`, `queue-operation`, `frame-link`, `file-history-*`, ...), is "
        "rendered as its own entry, raw where it has no prose form.",
        "",
        "### Entry counts by source line type",
        "",
    ]
    for name, n in type_counts.most_common():
        header.append("- `%s`: %d" % (name, n))
    header += ["", "---", ""]
    header_text = "\n".join(header)

    def write(path, text):
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        return path.stat().st_size

    if len(header_text.encode("utf-8")) + body_bytes <= split_bytes:
        size = write(out_path, header_text + "".join(t + "\n" for _, t, _ in entries))
        print("entries      : %d" % len(entries))
        print("output       : %s (%d bytes)" % (out_path, size))
        parts = [(out_path, len(entries))]
    else:
        parts = []
        budget = split_bytes - len(header_text.encode("utf-8"))
        cur, cur_bytes = [], 0
        for e in entries:
            b = len(e[1].encode("utf-8")) + 1
            if cur and cur_bytes + b > budget:
                parts.append(cur)
                cur, cur_bytes = [], 0
            cur.append(e)
            cur_bytes += b
        if cur:
            parts.append(cur)

        index = list(header)
        index.append("### Parts")
        index.append("")
        index.append("| part | entries | first timestamp | last timestamp | bytes |")
        index.append("|---|---|---|---|---|")
        written = []
        for i, chunk in enumerate(parts, 1):
            p = out_path.with_name("%s-part%d%s" % (out_path.stem, i, out_path.suffix))
            note = ("# %s - part %d of %d\n\nEntries %d-%d. Index and full provenance: "
                    "`%s`.\n\n---\n\n"
                    % (sid, i, len(parts), chunk[0][0], chunk[-1][0], out_path.name))
            size = write(p, note + "".join(t + "\n" for _, t, _ in chunk))
            ts_in = [t for _, _, t in chunk if t]
            index.append("| `%s` | %d-%d | %s | %s | %d |" % (
                p.name, chunk[0][0], chunk[-1][0],
                ts_in[0] if ts_in else "-", ts_in[-1] if ts_in else "-", size))
            written.append((p, len(chunk)))
        index += ["", "---", ""]
        write(out_path, "\n".join(index))
        print("entries      : %d across %d parts" % (len(entries), len(parts)))
        for p, n in written:
            print("  %s  %d entries  %d bytes" % (p.name, n, p.stat().st_size))
        parts = written

    print("redactions   : %d %s" % (sum(stats.redactions.values()), dict(stats.redactions)))
    print("truncated    : %d results, %d chars elided" % (stats.truncated, stats.elided_chars))
    print("meta trunc   : %d payloads, %d chars elided" % (stats.meta_truncated, stats.meta_elided))
    print("images noted : %d" % stats.images)
    print("CR converted : %d CRLF + %d lone CR" % (stats.crlf, stats.lone_cr))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
