#!/bin/bash
# census.sh — full-estate CVAA census, emitting MEMBERS not cardinality (RH29).
# Measures all 32 cloned repos with the published cvaa, counts fail/warn/skip
# separately (RH28), and states the control for every rule (RH27).
set -uo pipefail
GH="C:/Users/vikra/OneDrive/Documents/GitHub"
SC="C:/Users/vikra/AppData/Local/Temp/claude/C--Users-vikra/5b94bee7-197b-4cfd-944b-d4cf3aa02d18/scratchpad"
CV="$GH/claude/sessions/202609030120-cicd-spider/.cvaa-clean"
OUT="${1:-$SC/census-$(date -u +%Y%m%d%H%M)}"; mkdir -p "$OUT"
git -C "$CV" fetch -q --no-tags origin main && git -C "$CV" reset -q --hard origin/main
echo "ruler: cvaa $(git -C "$CV" rev-parse --short HEAD)"
run(){ timeout 900 node "$CV/inoculate.mjs" "$1" --json --no-write > "$OUT/$2.json" 2>&1; }
for d in $(ls "$SC/estate" 2>/dev/null); do ( run "$SC/estate/$d" "$d" ) & while [ "$(jobs -r|wc -l)" -ge 6 ]; do wait -n; done; done
for d in chatgpt-audits claude codex-chatgpt companies cvaa data-centres-gb data-federation-map-for-globalgrid2050-all-repos data-gb-electricity data-grid-gb data-gridatlas data-interconnectors gb-electricity-ui gemini globalgrid2050 grid-distance-maths gridatlas pipelinenews spiders; do ( run "$GH/$d" "$d" ) & while [ "$(jobs -r|wc -l)" -ge 6 ]; do wait -n; done; done
wait
PYTHONIOENCODING=utf-8 python "$GH/claude/sessions/202609030120-cicd-spider/census.py" "$OUT"
