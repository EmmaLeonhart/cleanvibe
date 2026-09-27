# 03 — Untitled and empty, in a neutral folder

- **Project:** `Documents/GitHub/untitled-cleanvibe-project`, cleanvibe 2.0.1,
  untitled, nothing dropped in, not inside the cleanvibe repository.
- **Purpose:** the low-information test. Does the session wait when there is
  nothing to go on (the 2.0.1 "nothing to go on" verdict), or does it still
  invent work? Compare with case 02.
- **Emma:** not talking to this one.

## Log

- **21:13:15** launched with the installed cleanvibe 2.0.1 (bare `cleanvibe` in
  `Documents/GitHub/`, run from an agent session). Pre-trusted; its own
  transcript; Remote Control on (`bridge-session`); no `--name` passed, and
  Claude titled it "Untitled cleanvibe project intake".
- It scheduled the intake at once: `43 21 26 9 *`, one-time, with the exact
  `[cleanvibe cron]` prompt.
- 21:13: its first INTENT.md read was "nothing to go on yet" (`49949d9`). It
  did not guess from the path.
- **21:43: the intake ran** (`aa55c8a` snapshot, `071a905` move) and reported
  **NOTHING TO GO ON**. The agent recorded "still nothing to go on" in
  INTENT.md (`760fabe`) and stopped there: no plan, no `queue.md`, no work-loop
  crons.

- Checked again at 01:00: still nothing after 21:43. No crons, no commits,
  three hours of waiting. The "nothing to go on" state holds.

## Result

**Passed.** Same input as case 02 (empty, untitled, nobody talking), opposite
outcome. It waited instead of inventing a purpose. Two things changed together,
so this doesn't separate them: the location was neutral (not inside the
cleanvibe repo), and 2.0.1's verdict no longer pushes toward "start".
