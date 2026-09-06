Resume the previous session on the GlobalGrid2050 estate.

Run this first and read its whole output:

    bash "C:/Users/vikra/OneDrive/Documents/GitHub/claude/scripts/carry-on.sh"

It prints the top of `CARRY-ON.md`, the resume and open sections of the newest
session log, and the current HEAD of every estate repo — fetched at that
moment, so any number in the log that the estate has since moved past shows up
as moved past.

Then open the log it names and read it completely before acting. Take its
first open item unless Vikram says otherwise.

Rules that apply from the first command:

- Every number in a log names the generation or commit it was measured
  against. Re-measure before quoting one — the estate moves under you.
- Never `git add -A` in the `claude` repo. Stage by explicit path, stage and
  commit in the same shell call, message written to a file first.
- Stamps come from `date -u` in the same command as the commit, never typed.
- Never edit a published version; a fix goes in a new timestamped generation.
- Report measurements, never grade them. A skip is not a pass.
- Measure the artefact that ships, not the source it came from.
- A permission denial means stop and ask. Never route around it.
- Vikram's clock is BST, UTC+1.

(This copy lives in the repo so it survives the machine. The one Claude Code
loads from any directory is `~/.claude/commands/carry-on.md` — keep them the
same.)
