#!/usr/bin/env bash
# Read-only. Shows the newest checkpoint from every lane, flags a stopped lane,
# and lists what may be taken from it. Writes nothing, fetches only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE" || exit 1
git fetch -q origin 2>/dev/null || true

NOW_EPOCH=$(date -u +%s)
STALE_MINUTES=${LANES_STALE_MINUTES:-90}

echo "=== lanes  (now $(date -u +%Y-%m-%dT%H:%M:%SZ), stale after ${STALE_MINUTES}m) ==="
for lane in claude codex; do
  newest="$(ls -1 lanes/*-"$lane".json 2>/dev/null | sort | tail -1)"
  if [ -z "$newest" ]; then
    printf '%-8s no checkpoint yet\n' "$lane"
    continue
  fi
  python - "$newest" "$NOW_EPOCH" "$STALE_MINUTES" <<'PY'
import json, sys, datetime
path, now_epoch, stale_min = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d = json.load(open(path, encoding='utf-8'))
hb = d.get('heartbeatUTC', '')
try:
    age = (now_epoch - int(datetime.datetime.strptime(hb, '%Y-%m-%dT%H:%M:%SZ')
           .replace(tzinfo=datetime.timezone.utc).timestamp())) // 60
except Exception:
    age = None
state = 'unknown age' if age is None else (f'STOPPED {age}m ago' if age > stale_min else f'live {age}m ago')
print(f"{d.get('lane','?'):8} {state:20} {d.get('model','?')}  {path}")
for r in d.get('repos', []):
    dirty = f" {r['dirty']} dirty" if r.get('dirty') else ''
    print(f"           {r['name']:22} {r.get('branch','?'):34} {r.get('head','?')}{dirty}")
for k in ('did', 'blocked', 'handoff'):
    for line in d.get(k, []):
        print(f"           [{k}] {line}")
for o in d.get('open', []):
    mark = 'TAKEABLE' if o.get('takeable') else 'held    '
    if age is not None and age > stale_min and o.get('takeable'):
        mark = 'TAKE NOW'
    print(f"           [{mark}] {o.get('item','')}")
PY
  echo
done
echo "Rule: a checkpoint is a claim about the past; the commit history is the fact."
