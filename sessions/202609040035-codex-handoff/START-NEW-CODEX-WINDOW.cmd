@echo off
setlocal
set "GG_ROOT=C:\Users\vikra\OneDrive\Documents\GitHub"
set "GG_HANDOFF=C:\Users\vikra\OneDrive\Documents\GitHub\.codex-worktrees\claude-cto-handoff\sessions\202609040035-codex-handoff\01-FINAL-HANDOFF.md"
start "Codex Overnight CEO" /D "%GG_ROOT%" cmd.exe /k codex --yolo -C "%GG_ROOT%" "Read %GG_HANDOFF% first. Continue the overnight CEO loop autonomously from the recorded exact heads. Use subagents for bounded work, keep promotions serial, and do not ask for trivial approvals."
endlocal
