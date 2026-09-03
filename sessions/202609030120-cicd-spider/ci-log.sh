#!/bin/bash
# ci-log.sh <owner/repo> <run_id> [grep-pattern]
# Reads a GitHub Actions run log. RH24: this endpoint returns 200 with the
# stored credential; the estate believed it was 403 for an entire night.
set -euo pipefail
REPO="$1"; RUN="$2"; PAT="${3:-}"
TOK=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill 2>/dev/null | sed -n 's/^password=//p')
[ -n "$TOK" ] || { echo "no credential"; exit 1; }
TMP=$(mktemp -d)
curl -sL -H "Authorization: token $TOK" \
  "https://api.github.com/repos/$REPO/actions/runs/$RUN/logs" -o "$TMP/logs.zip"
unzip -qo "$TMP/logs.zip" -d "$TMP/x" 2>/dev/null || { echo "not a zip"; head -c 200 "$TMP/logs.zip"; exit 1; }
if [ -n "$PAT" ]; then grep -rniE "$PAT" "$TMP/x" | sed "s|$TMP/x/||"; else
  find "$TMP/x" -type f -name '*.txt' | sed "s|$TMP/x/||" | sort; fi
rm -rf "$TMP"
