# Session recovery — `5b94bee7`, the last three hours were not in the store

**2026-09-03 22:44 BST.** The architect asked for the last session back. It was there, but
the committed copy stopped short.

## What was missing

`logs/202609031845-full-session-5b94bee7.md` was rendered at 19:46 and captured the session
up to **2026-09-03T18:34:11Z**. The session did not end there — it ran for another three
hours and seven minutes, to **21:40:57Z**, and those minutes contained the whole mobile-UI
reckoning and two shipped Atlas versions.

| | committed at 19:46 | recovered at 22:44 |
|---|---|---|
| source bytes | 15,405,496 | 17,821,918 |
| transcript lines | 6,491 | 7,288 |
| last entry | 2026-09-03T18:34:11Z | 2026-09-03T21:40:57Z |
| parquet rows | 6,493 | 7,290 |

**797 lines, 560 of them timestamped after the old cut, were one power cycle from being
lost.** They are not in git history anywhere else: the local JSONL was the only copy.

Rebuilt from the same source by the same two tools, so the counts still reconcile
(`distinct source_line` = `Rendered entries` = 7,288, 0 unparseable, 0 redactions):

- `logs/202609032244-full-session-5b94bee7.md` — the session whole, 6.8 MB
- `logs/parquet/session_5b94bee7.parquet` — rewritten, 9.94× compression
- `logs/reports/session_5b94bee7_audit.json` — rewritten

The 18:45 render and index are kept. They are not wrong, they are a shorter session.

## What happened in the recovered window

Eight architect instructions, in order, with the transcript line to read:

| line | Z | what was asked |
|---|---|---|
| 6494 | 18:35 | *"The UI sucked and it didn't work I don't believe you had proper 'eyes'"* — with a 1179×2556 phone screenshot |
| 6609 | 19:43 | how much context is left, checked in PowerShell |
| 6629 | 19:51 | *"If you have 15m tokens then BUILD YOURSELF. Ship and show proof"* |
| 6903 | 20:11 | **the acceptance rule** — *"what counts as tested is if at least two agents on different browsers clicked and checked that it works"* |
| 7147 | 20:36 | port all 63 layers into a dropdown and call it **Grid** |
| 7263 | 21:35 | give me test links |

What came out of it:

- **`familiars/summon.py`** (committed, `2e87f19`) — five scripted workers, 32.8 s, one screen.
- **`familiars/clicker.py`** (was uncommitted, committed now) — each clicker launches its own
  Chrome on its own port and profile, and refuses to report any measurement taken while
  `document.hidden`. That is the two-browser acceptance rule mechanised, and the answer to
  *"you didn't have proper eyes"*.
- **GridAtlas v9.95** — the mobile menu bar **withdrawn**. `adopt()` moved only direct
  children, so `#gridatlas-mobile-tray` (SCOPE and CLEAR) stayed inside the container that
  was hidden wholesale: buried, 0×0, and Radius Search left with nowhere to draw. Two
  independent clickers killed it. **104/104 checks had passed against exactly that screen** —
  the day's second proof that a check only tests what someone thought to assert.

## Open at the moment the session stopped

1. **`gridatlas/atlas/world/index.html` is dirty** — 232 insertions, a *Drifting Scope
   Product Card*, last written 21:25Z. Uncommitted, unbuilt, unverified. It is the only
   copy. **Do not ship it without the two-clicker rule.**
2. **The Grid menu — all 63 layers — is not in.** It was the live instruction at 20:36 and
   was explicitly flagged as not delivered in the handover: *"the Grid menu with all 63
   layers isn't in yet — that's next."*
3. Known and untouched: the mobile header pile-up in the top 44 px; `404` on
   `build_manifest.json` on every Atlas load from `ventusltd.github.io`; Pipeline News still
   carries the bad record counter and gauge arcs.

## The estate in the same 24 hours

222 commits across 18 repositories: `claude` 137, `gridatlas` 40, `pipelinenews` 12,
`cvaa` 14, `globalgrid2050` 7, `codex-chatgpt` 6, the rest 2 or fewer.

## The lesson, so it does not happen again

The store is written **on request**, and a session keeps running after it is written. Every
render is a snapshot with a cut, and the cut is invisible from inside the file unless you
compare `Last timestamp` against the live JSONL. Before trusting any session record, check
the mtime of `~/.claude/projects/<project>/<uuid>.jsonl` against the render's last
timestamp. They will disagree, and the difference is what you are missing.
