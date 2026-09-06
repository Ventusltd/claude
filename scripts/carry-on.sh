#!/usr/bin/env bash
# CARRY ON — print exactly what a fresh session needs to resume, and nothing more.
#
# WHY A SCRIPT. On 2026-09-04 a session log was written where the next morning's
# session could not find it. The rule that followed — every handover lives in
# this repository and CARRY-ON.md names the newest one — works, but it is a
# convention, and a convention is only as good as the next reader's memory of
# it. This turns it into one command. `/carry-on` in Claude Code runs it.
#
# WHAT IT PRINTS, IN ORDER
#   1. the top section of CARRY-ON.md      — the pointer, and the one-paragraph state
#   2. the newest session log's §0 and its "open" section
#                                           — where to resume, and what to take first
#   3. the HEAD of each estate repo, FETCHED NOW
#                                           — so a number in the log that has since
#                                             been overtaken is visible as overtaken,
#                                             which is the measurement rule in CLAUDE.md
#
# It reads. It never writes, fetches only, and never touches another lane's dirty
# tree — it reports the dirty count so you know one is there.
#
#   bash scripts/carry-on.sh            (from anywhere; it finds its own repo)
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO" || { echo "cannot cd to $REPO"; exit 1; }
git fetch -q origin 2>/dev/null || true   # fetch before enumerating — CLAUDE.md rule

printf '# CARRY ON   %s\n' "$(date -u +%Y-%m-%dT%H:%MZ)"
printf 'claude repo @ %s   %s dirty path(s) — other lanes'"'"' work, not yours; do not stage them\n\n' \
  "$(git rev-parse --short HEAD)" "$(git status --porcelain | wc -l | tr -d ' ')"

# ---- 1. the pointer: CARRY-ON.md, first '## ' section only -------------------
echo '## ---- CARRY-ON.md, top section ----'
awk '/^## /{n++} n==1{print} n==2{exit}' CARRY-ON.md
echo

# ---- 2. the newest log: the one the pointer names, else newest by stamp ------
LOG="$(grep -oE 'sessions/[0-9]{12}-[^/) ]+/00-LOG\.md' CARRY-ON.md | head -1)"
if [ -z "$LOG" ] || [ ! -f "$LOG" ]; then
  LOG="$(ls -d sessions/*/00-LOG.md 2>/dev/null | sort | tail -1)"
fi
echo "## ---- NEWEST LOG: $LOG ----"
# Print every section whose heading is "0." or contains "open"; that is the
# resume paragraph and the open-items list in every log written since 09-05.
# Older logs have neither, so fall back to the first forty lines.
PRINTED="$(awk '/^## /{h=$0} (h ~ /^## 0\./ || h ~ /[Oo]pen/) {print}' "$LOG")"
if [ -n "$PRINTED" ]; then printf '%s\n' "$PRINTED"; else head -40 "$LOG"; fi
echo

# ---- 3. estate heads, fetched now --------------------------------------------
echo '## ---- ESTATE HEADS (fetched now; compare with the log before quoting a number) ----'
GH="$HOME/OneDrive/Documents/GitHub"
for r in gridatlas-main-202609050200 gridatlas teleprinter gpu-drivers-for-global-grid \
         globalgrid2050 globalgrid2050-homepage spiders ventus-grid-engine testcode cvaa; do
  d="$GH/$r"
  [ -e "$d/.git" ] || continue
  (
    cd "$d" || exit 0
    git fetch -q origin 2>/dev/null || true
    printf '%-32s %s  %2s dirty  %s\n' "$r" "$(git rev-parse --short HEAD 2>/dev/null)" \
      "$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')" \
      "$(git log -1 --format=%s 2>/dev/null | cut -c1-64)"
  )
done
echo
echo "Next: read $LOG in full, then take its first open item unless told otherwise."
