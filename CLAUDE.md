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
3. `sessions/<latest>/06-corrections.md` — what an earlier session got wrong, and how it was caught
4. `sessions/<latest>/07-routing-table.md` — every open finding routed to the one file that owns it
5. `sessions/<latest>/08-decisions-for-the-architect.md` — what is blocked on a human answer

---

## THE MEASUREMENT RULE — read this before you measure anything

Four agents ran concurrently on 2026-09-03 and produced **twenty-plus corrections between them**.
Almost every one was the same mistake in a different place:

> **A measurement that does not name the commit, the branch, and the bytes it read is not a
> measurement.** In an estate several agents deep, nothing is ever at rest. You will measure a
> workspace mid-change and describe it as a state.

The four faces it wore in one night:

| | what was measured | what was reported |
|---|---|---|
| **dirty tree** | a working copy mid-edit by another agent | "CI went red on v9.82" — it had not |
| **dirty bytes** ×2 | a CRLF working copy | invented a `pointer-verifies` failure *and* concealed a real `on-ledger-commits` one |
| **wrong branch** | a Codex feature branch's first CI run | "gridatlas is red" — `main` was green |

**Concrete rules that follow:**

- **A git-clean tree is not a byte-clean tree.** `git status` compares *through* `.gitattributes`
  normalisation, so it reports clean while the disk holds CRLF and the blob holds LF. 15 of 18
  repos here are affected. Discriminator: `git ls-files --eol | grep -c w/crlf` — gridatlas 239,
  globalgrid2050 3,597.
- **For anything that depends on file bytes** — digests, checksum manifests, byte-identity, hashing
  a release — **use a clean clone, never the working tree.** A checksum manifest whose *own* lines
  are CRLF makes `sha256sum` hunt for filenames ending in a carriage return.
- **Filter CI sampling to the default branch.** Feature branches fail on their first run and that
  is not a defect.
- **Check `git status --porcelain` before AND after any gate run.** A tree can move mid-run. If it
  is dirty, either test the committed HEAD in a copy or report *unmeasurable* — a third state that
  can produce neither a red nor a green.

## A GREEN LIGHT THAT MEASURED NOTHING — the other half of the same disease

Three times in ninety minutes a gate reported success while executing nothing:

- A proof written as `node block.js && echo PASS` under `set -e`. The left side threw; the echo ran
  anyway. **A proof on the left of `&&` is not a gate.** Capture `rc=$?` on its own line.
- A proof that read a sibling repository the CI runner does not check out. The eight real-data
  checks were guarded by `if (PRODUCT_FILE)` and **skipped silently** when it was absent — so
  **675 of 735 checks had never run on a runner**, and the transformer fix had only ever been
  verified on a laptop where the repos happened to be neighbours.
- Two hard-coded constants in one `set -euo pipefail` step. The step aborted at the first, so a fix
  to the second could not possibly turn it green — same red before and after.

**Rules:** a missing input must FAIL, never skip. Reproduce the *step*, not the assertion.
**A check built only from cases the code already passes cannot fail.**

## THE GATE IS THE RUNNER'S CONCLUSION, NOT YOUR LOCAL RUN

Five generations shipped green-on-disk and red-on-runner before anyone noticed. Poll
`https://api.github.com/repos/Ventusltd/<repo>/actions/runs?head_sha=<sha>` and require
`conclusion: success` before the next cut.

## A CORRECTION CAN CREATE ITS OWN DEFECT

Three times a fix introduced a new fault. The general shape, worth carrying:

> **A guard changes what gets measured, and every summary computed downstream of it silently
> changes meaning.**

A dirty-tree guard correctly declined to measure three repos; the denominator moved 18→15; seven
vaccines appeared to improve and none had. **A wrong denominator is worse than a wrong finding,
because it gets quoted rather than checked.**

---

## Standing facts about this estate

- The **canonical repos** are under `OneDrive/Documents/GitHub/`. Directories in the home folder
  are **worktrees** — their `.git` is a file pointing back. Enumerate repos from the GitHub API,
  never from disk: one session scanned 15 when the account had 30, and 33 by morning.
- **No `gh` CLI — but there IS a token, and this note used to say there wasn't.** `gh` is not
  installed on this machine, in Bash or in PowerShell. The API, however, is not limited to 60
  requests an hour: every push already authenticates, so the credential helper holds a token and
  `git credential fill` hands it back. Use **`scripts/gh-api.sh`**.

  | | limit | measured 2026-09-03 04:33 UTC |
  |---|---|---|
  | unauthenticated | 60/hour | 35 remaining — nearly exhausted, as the old note predicted |
  | with the stored credential | **5000/hour** | 4994 remaining, same minute |

  **`/actions/runs/<id>/logs` returns 200, not 403.** The old note recorded a permanent 403 and
  concluded "reproduce failures locally instead". That is why a nine-command CI step was split
  into five named ones on 3 September — to read a failure's identity off the jobs API without
  log access. **CI logs are readable.** Reproducing locally is still better evidence when the
  failure is behavioural, but it is no longer the only route.

  The token is never printed and never written to disk; it lives in one variable for one curl.
  Do not echo it, do not put it on a command line, do not commit it.
- `python3` is a broken Windows Store stub. Use `python`.
- **A heredoc that expands `$STAMP` also expands backticks.** `<<MSGEOF` (unquoted) is needed to
  interpolate a stamp into a commit message, but it runs anything in backticks as a command — a
  message containing `` `if (!scopes.length) return []` `` lost that clause to command
  substitution and shipped mangled. Quoted `<<'MSGEOF'` is safe but interpolates nothing. Either
  compute the stamp into the text with a quoted heredoc plus `sed`, or keep backticks out of
  commit messages. Never amend a pushed commit to fix this; record the correction instead.
- **Escaping is the most repeated failure in this estate's tooling - five times in one night.**
  Heredoc-piped Python that would not parse; backticks in a commit message executed as
  commands; a carriage-return literal in a grep that killed the shell; an escaped newline
  flattened through three layers of quoting. Each cost a retry.

  **This entry was itself mangled by the defect it describes.** Written through an unquoted
  heredoc, it arrived with its own examples eaten and had to be repaired with a script. That
  is the argument rather than an anecdote: **when a string carries code, write it to a file
  with the Write/Edit tool and run the file - do not pipe it through a shell.** A warning
  about escaping is not exempt from escaping.
- **`MSYS_NO_PATHCONV` is a per-command flag, never an environment.** Git Bash rewrites anything
  that looks like a path, so `git show origin/main:.gitattributes` reached git as
  `origin\main;.gitattributes` — the colon became a semicolon, every lookup failed, and a sweep
  of all 18 repos reported "no `.gitattributes`" when **every one of them has it**. Setting
  `MSYS_NO_PATHCONV=1` fixes that call and breaks the next one: with conversion off, git resolves
  `/c/Users/...` against the MSYS root, so a clone destination silently lands somewhere else and
  `git clone` reports "already exists" for a directory `[ -d ]` says is absent. Set it inline for
  the one command that needs a refspec; use `C:/Users/...` for paths handed to git.
  **A sweep that returns the same answer for every repository is a broken instrument, not a
  finding** — that shape caught this one, and it is worth treating as a rule.
- 20 cores. `--shared` clones are instant. A full estate scan is under a minute. Multiprocessing
  workers must live in a real `.py` file with a `__main__` guard — heredoc-piped code crashes the
  pool on Windows.
- `Counter[400]` and `Counter[400.0]` are the **same key** in Python. This produced a false defect
  report once.
- `require()` picks its parser by extension: it reads a `.lock` as JavaScript and throws. Use
  `JSON.parse(readFileSync(...))`.
- A `git clone` of gridatlas on Windows needs `-c core.longpaths=true`, and **even then 12 files
  under `nightly/…/runs/` are silently absent** while git reports success.
- Stamps come from `date -u +%Y%m%d%H%M` **evaluated in the same command as the commit**. Reading
  BST off `git log` put five commits 29–50 minutes ahead; `monotonic-utc-generations` catches it.

## Editing globalgrid2050/index.html

1. `homepage_versions/README.md` requires a numbered snapshot with recorded line/word/char counts
   and a plain-English change intention **before** any edit. **Fetch before enumerating** — a
   session overwrote a real snapshot because it listed the folder before fast-forwarding.
2. `scripts/catalogue_gridatlas_v9.py` fails closed unless the V8 sentinel appears once byte for
   byte with four leading spaces, and its route appears once. The `GRIDATLAS_V9_AUTOMATION_START/END`
   markers must survive verbatim.
3. **The compiler cannot refresh the current-composition row.** `compile_root()` requires the
   catalogue URL to occur at most once and, when present, the whole entry line to match byte for
   byte. An `os-strip` banner added on 30 August carries the same href, so the compiler has been
   unable to run on that file since. That is why the version stamp drifted nine releases.

Verify before every commit: sentinel once, route once, both markers intact, every pre-existing
`name:` and `note:` string byte-identical, and `AREAS` re-evaluated with node so it still parses.

Ship live by default — stamp, commit, push, then poll the live URL and report the SHA-256 match.

## Standing discipline in this estate

- **Never amend a shipped generation.** New fault, new step, new version.
- **Report measurements, never grade them.**
- **A skip is not a pass.** A verdict may only say PASS when every check it names actually ran.
- **Never weaken a shared check to make your lane pass.** Make it more precise and say why.
- **Redact the payload, not the view.**
- **Measure the artefact, never the workspace.**

## Working alongside other agents

Several lanes run at once — Claude, Codex, Gemini, and subagents of each.

- **Never `git add -A` or `git add .` in this repo.** Stage by explicit path. A commit race here
  swept another session's in-progress files into an unrelated commit.
- Fetch immediately before every write, not once per phase. `atlas/current.json` and
  `index.html` are single files every generation must touch; git cannot merge them meaningfully.
- If a repo is mid-write by another lane, note it and move on. **Never treat a dirty tree as a
  defect.**
- If another lane already shipped a fix you were about to make, log it as covered and move on.

## How to add a session

Create `sessions/<YYYYMMDDHHMM>-<slug>/`. Do not rewrite an earlier session; a correction is a new
entry that names what it corrects. **Record what you got wrong** — most errors here were caught by
measuring again rather than by reasoning harder, and that is the transferable lesson.
