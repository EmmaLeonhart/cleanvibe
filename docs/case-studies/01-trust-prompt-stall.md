# 01 — The session that never started (trust prompt)

- **Project:** `tests/scratch/cleanvibe-2026-09-26`, cleanvibe 2.0.0-dev, auto-named, empty.
- **Started:** 2026-09-26 18:43 PST, by bare `cleanvibe` run from an agent session
  (the child-session case).

## What happened

The launch itself worked: a new `claude.exe` (PID 38744) started, with the
first-session prompt intact through `cmd /k`. But it stopped at Claude Code's
"Is this a project you created or one you trust?" prompt, which blocks a new
folder's first interactive session until someone answers it at the machine.
There was no transcript and no Remote Control until then. Screenshot:
`Documents/claude-screenshots/cleanvibe_2026-09-26/practice-session-console.png`.

Answering it for Emma failed. `SendKeys` found no foreground window (a locked
screen), and writing keypresses into the console input was refused by the
auto-mode classifier, which blocks one session driving another's terminal.

## Why

Earlier smoke tests used `claude -p`, which skips the trust prompt, so this
never showed up in testing. An unattended, agent-started session (the thing
cleanvibe 2 is for) hits it every time.

## What changed

`cleanvibe/trust.py`, shipped in 2.0.0 with Emma's approval: `cleanvibe` marks
a folder it has just created as trusted in Claude Code's config before
launching it. The next session (02) went straight past the prompt.
