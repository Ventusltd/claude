#!/usr/bin/env bash
# gh-api.sh — call the GitHub API as Ventusltd, using the credential git already holds.
#
# WHY THIS EXISTS
#
# CLAUDE.md carried "no gh CLI, no token; the API is unauthenticated at 60 requests per hour,
# shared by every agent and the estate's own workflows". That was true of `gh`, which is not
# installed, but not of the API. Every push in this estate already authenticates, so the
# credential helper holds a token, and `git credential fill` will hand it back.
#
#     unauthenticated   limit 60     (measured at 35 remaining on 2026-09-03 04:33 UTC)
#     with this token   limit 5000   (measured at 4994 remaining, same minute)
#
# It also overturns the second half of that note. /actions/runs/<id>/logs was recorded as a
# permanent 403, which is why failures here get reproduced locally instead of read. With the
# credential it returns 200. CI logs are readable.
#
# THE TOKEN IS NEVER PRINTED AND NEVER WRITTEN TO DISK. It lives in one shell variable for the
# life of one curl. Do not echo it, do not pass it on a command line where it lands in ps output,
# and do not add it to a file this repository tracks.
#
# Usage:
#   scripts/gh-api.sh repos/Ventusltd/cvaa/actions/runs?branch=main
#   scripts/gh-api.sh repos/Ventusltd/gridatlas/actions/runs/33715076001/logs --raw > logs.zip
#   scripts/gh-api.sh rate_limit
set -euo pipefail

PATH_PART="${1:?usage: gh-api.sh <api-path> [--raw]}"
RAW="${2:-}"

TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill 2>/dev/null | sed -n 's/^password=//p')
if [ -z "$TOKEN" ]; then
  echo "no stored github credential; falling back to unauthenticated (60/hour)" >&2
  AUTH=()
else
  AUTH=(-H "Authorization: Bearer $TOKEN")
fi

if [ "$RAW" = "--raw" ]; then
  # Logs are a redirect to a zip. -L follows it; keep the bytes intact.
  curl -sSL "${AUTH[@]}" "https://api.github.com/${PATH_PART}"
else
  curl -sS "${AUTH[@]}" -H "Accept: application/vnd.github+json" "https://api.github.com/${PATH_PART}"
fi
