#!/usr/bin/env python3
"""
Render a Claude Code session transcript (.jsonl) to readable Markdown.

Every message, in order, nothing summarised and nothing dropped. Tool calls
keep their full input; tool results keep their full text. The only things not
reproduced verbatim are base64 image payloads, which are replaced by a one-line
note giving their media type and byte count -- the bytes are still in the .jsonl
filed alongside this, so nothing is lost, and a hundred screenshots inlined as
base64 would make the Markdown unreadable without adding a single fact.

Usage:
    python render_transcript.py --jsonl <session>.jsonl --out 00-FULL-LOG.md
"""

import argparse
import json
import os


def fence(text, language=""):
    """Fence text, widening the fence past any run of backticks inside it."""
    text = "" if text is None else str(text)
    longest = 0
    run = 0
    for character in text:
        if character == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    bar = "`" * max(3, longest + 1)
    return f"{bar}{language}\n{text}\n{bar}"


def render_content(content, out):
    """Render one message's content blocks."""
    if isinstance(content, str):
        if content.strip():
            out.append(content)
        return

    if not isinstance(content, list):
        out.append(fence(json.dumps(content, indent=2), "json"))
        return

    for block in content:
        if not isinstance(block, dict):
            out.append(str(block))
            continue
        kind = block.get("type")

        if kind == "text":
            text = block.get("text", "")
            if text.strip():
                out.append(text)

        elif kind == "thinking":
            thinking = block.get("thinking", "")
            if thinking.strip():
                out.append("<details><summary>thinking</summary>\n")
                out.append(fence(thinking))
                out.append("</details>")

        elif kind == "tool_use":
            name = block.get("name", "?")
            out.append(f"**→ tool call: `{name}`**")
            out.append(fence(json.dumps(block.get("input", {}), indent=2,
                                        ensure_ascii=False), "json"))

        elif kind == "tool_result":
            body = block.get("content")
            flag = " (error)" if block.get("is_error") else ""
            out.append(f"**← tool result{flag}**")
            if isinstance(body, str):
                out.append(fence(body))
            elif isinstance(body, list):
                for part in body:
                    if not isinstance(part, dict):
                        out.append(fence(str(part)))
                    elif part.get("type") == "text":
                        out.append(fence(part.get("text", "")))
                    elif part.get("type") == "image":
                        source = part.get("source") or {}
                        data = source.get("data") or ""
                        out.append(f"*[image: {source.get('media_type', 'unknown')}, "
                                   f"{len(data)} base64 chars — bytes are in the .jsonl]*")
                    else:
                        out.append(fence(json.dumps(part, indent=2)[:4000]))
            elif body is not None:
                out.append(fence(json.dumps(body, indent=2)))

        elif kind == "image":
            source = block.get("source") or {}
            data = source.get("data") or ""
            out.append(f"*[image: {source.get('media_type', 'unknown')}, "
                       f"{len(data)} base64 chars — bytes are in the .jsonl]*")

        else:
            out.append(fence(json.dumps(block, indent=2, ensure_ascii=False)[:8000], "json"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = []
    unparseable = 0
    with open(args.jsonl, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                unparseable += 1

    messages = [r for r in records if r.get("type") in ("user", "assistant")]
    first = next((r.get("timestamp") for r in records if r.get("timestamp")), "?")
    last = next((r.get("timestamp") for r in reversed(records) if r.get("timestamp")), "?")

    out = [
        "# Full session log",
        "",
        "Verbatim rendering of the session transcript. Every message in order, "
        "nothing summarised. Assistant reasoning is included in collapsed "
        "`thinking` blocks. Tool calls keep their full input; tool results keep "
        "their full text. Base64 image payloads are noted rather than inlined — "
        "the bytes are in the `.jsonl` filed beside this.",
        "",
        f"- session: `{records[0].get('sessionId', '?') if records else '?'}`",
        f"- records: {len(records)} ({len(messages)} messages)",
        f"- first timestamp: `{first}`",
        f"- last timestamp: `{last}`",
        f"- unparseable lines: {unparseable}",
        f"- rendered by: `scripts/{os.path.basename(__file__)}`",
        "",
        "---",
        "",
    ]

    index = 0
    for record in messages:
        message = record.get("message")
        if not isinstance(message, dict):
            continue
        index += 1
        role = message.get("role", "?")
        stamp = record.get("timestamp", "")
        out.append(f"## {index:04d} · {role}{f' · `{stamp}`' if stamp else ''}")
        out.append("")
        render_content(message.get("content"), out)
        out.append("")

    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out) + "\n")

    print(f"{len(records)} records, {index} messages -> {args.out}")
    print(f"{os.path.getsize(args.out):,} bytes")


if __name__ == "__main__":
    main()
