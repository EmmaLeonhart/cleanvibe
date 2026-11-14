@echo off
cd /d "%~dp0"

echo ==========================================
echo Launching Claude from repo root:
echo %CD%
echo ==========================================
echo.
REM --remote-control added 2026-10-06 at Emma's request: every launcher must start a session she can reach from her iPhone. The flag goes after the prompt because it takes an optional name.
REM The prompt starts the work loop first (Emma, 2026-11-09): crons end with the session, so a relaunch without it has no loop.
claude "Start the work loop now with the autonomous-loop skill, before anything else, as CLAUDE.md says. Then read INTENT.md and queue.md and carry on with the first item." --remote-control "cleanvibe"
