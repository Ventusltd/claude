# For the next session

You have no memory of the sessions recorded here. Read this first, then the most recent
`sessions/*/00-LOG.md`.

## What this repository is

The learning of past Claude Code sessions on the GlobalGrid2050 estate. Not the builds — those
live in their own repositories. What is kept here is what would otherwise be lost: measurements,
defects and how they were found, theories that turned out wrong, and scripts that reproduce any
of it.

## Read in this order

1. `sessions/<latest>/00-LOG.md` — the narrative, including the wrong turns
2. `sessions/<latest>/01-findings.md` — open defects, with evidence
3. `sessions/<latest>/02-measurements.md` — the numbers, and the script that produced each

## Standing facts about this estate

- The **canonical repos** are under `OneDrive/Documents/GitHub/`. Directories in the home folder
  are **worktrees** — their `.git` is a file pointing back. Enumerate repos from the GitHub API,
  never from disk: a session scanned 15 and the account had 30.
- **No `gh` CLI, no token.** The GitHub API is unauthenticated: 60 req/hour, and
  `/actions/runs/<id>/logs` returns 403. CI failures must be **reproduced locally**, which is
  better evidence than a log anyway.
- `python3` is a broken Windows Store stub. Use `python`.
- 20 cores. `--shared` clones are instant; fetch only the delta. A full estate scan is under a
  minute. Multiprocessing workers must live in a real `.py` file with a `__main__` guard —
  heredoc-piped code crashes the pool on Windows.
- `Counter[400]` and `Counter[400.0]` are the **same key** in Python. This produced a false
  defect report once.

## Editing globalgrid2050/index.html

Two constraints are not visible in the file:

1. `homepage_versions/README.md` requires a numbered snapshot with recorded line/word/char counts
   and a plain-English change intention **before** any edit. **Fetch before enumerating** — a
   session overwrote a real snapshot because it listed the folder before fast-forwarding.
2. `scripts/catalogue_gridatlas_v9.py` fails closed unless the V8 sentinel appears once byte for
   byte with exactly four leading spaces, and its route appears once in the whole file. The
   `GRIDATLAS_V9_AUTOMATION_START/END` markers must survive verbatim.

Verify before every commit: sentinel once, route once, both markers intact, every pre-existing
`name:` and `note:` string byte-identical. `scripts/verify_homepage.py` in the latest session does
this.

Ship live by default — stamp `YYYYMMDDHHMM`, commit, push, then poll the live URL and report the
SHA-256 match. A change that is not on globalgrid2050.com does not exist to the architect.

## Standing discipline in this estate

- **Never amend a shipped generation.** A new fault is a new step and a new version. Published
  bytes are not edited in place.
- **Report measurements, never grade them.** No verdicts on whether a project can connect.
- **A skip is not a pass.** Only a live outcome counts as a version.
- **Redact the payload, not the view.** A session anonymised a page's rendering while the embedded
  JSON still carried every name — one View Source away.

## How to add a session

Create `sessions/<YYYYMMDDHHMM>-<slug>/` with the same file set. Do not rewrite an earlier
session; a correction is a new entry that names what it corrects. Record what you got wrong —
six of eight errors in the first session were caught by measuring again rather than reasoning
harder, and that is the transferable lesson.
