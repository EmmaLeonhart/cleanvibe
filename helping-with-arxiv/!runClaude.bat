@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Claude Code - scratch-2026-09-25

REM Written by pc-manager\startup\Initialize-NewRepo.ps1.
REM The BOOT_PROMPT line below is copied VERBATIM from pc-manager\startclaude.bat.
REM Do not retype it -- nine launchers on this machine must hash identically,
REM and Test-RepoInvariants.ps1 check B is what keeps them that way.

REM USERPROFILE is not guaranteed to be set; rebuild it rather than dying on
REM an empty path. Measured 2026-08-28: Start-Process -UseNewEnvironment hands
REM a degenerate block with USERPROFILE empty and System32 off PATH, which made
REM the fallback below resolve to "\.local\bin" and read as a broken install.
if not defined USERPROFILE (
    if defined HOMEDRIVE if defined HOMEPATH set "USERPROFILE=%HOMEDRIVE%%HOMEPATH%"
)
if not defined USERPROFILE if defined SystemDrive set "USERPROFILE=%SystemDrive%\Users\%USERNAME%"
if not exist "%USERPROFILE%\" (
    echo ERROR: degenerate environment - USERPROFILE could not be resolved.
    pause
    exit /b 1
)

set "CLAUDE_EXE="
where claude >nul 2>&1
if %errorlevel% equ 0 (
    set "CLAUDE_EXE=claude"
) else if exist "%USERPROFILE%\.local\bin\claude.exe" (
    set "CLAUDE_EXE=%USERPROFILE%\.local\bin\claude.exe"
) else (
    echo ERROR: claude.exe not found on PATH or in %USERPROFILE%\.local\bin
    pause
    exit /b 1
)

set "BOOT_PROMPT=Read queue.md and work its FIRST item, on its own, never combined with another item. Do not skip it, even if it says it is waiting on Emma or blocked: if it is stuck on a question, make the call yourself, do it, and record the decision and why in devlog.md. Only when it is done go on to the next item, the new first one. Follow the queue-driven-workflow skill: finish an item, delete it from queue.md, append a dated devlog.md entry in the same commit, then push. Ask me before anything destructive."

REM Remote Control with an EXPLICIT name: the flag takes an optional value, so a
REM bare --remote-control before the prompt would swallow the prompt as the name.
"%CLAUDE_EXE%" --remote-control "scratch-2026-09-25" "%BOOT_PROMPT%"

echo.
echo Claude Code exited with code %errorlevel%.
pause
