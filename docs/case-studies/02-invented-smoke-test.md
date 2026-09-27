# 02 — The session that invented its own purpose

- **Project:** `tests/scratch/cleanvibe-2026-09-26-2`, cleanvibe 2.0.0, auto-named,
  nothing dropped in, created inside the cleanvibe repository.
- **Started:** 2026-09-26 19:33 PST, by bare `cleanvibe` run from an agent session.
- **Sources:** the project's git history, its transcript, and the `FAILURES.md`
  the session wrote at Emma's request at 20:46.

## What it was given

No chat (the user was away until about 20:25). No files. A generated name. And
a lot of context about itself: the path (`.../cleanvibe/tests/scratch/...`),
a `CLAUDE.md` describing cleanvibe's machinery in detail (hooks, the intake
script, skills), a scaffold that was visibly cleanvibe's own output, and the
cleanvibe repository one directory up.

## What it did

| Time (PST) | |
|---|---|
| 19:33 | Scheduled the thirty-minute intake correctly. |
| 19:34 | Wrote INTENT.md: "likely a cleanvibe smoke test", reasoning from the folder's location. Low confidence. |
| 20:03 | The intake ran correctly (two commits, nothing to move). Verdict: no engagement, so "start the work loop now". |
| 20:04 | Settled on the smoke-test reading, planned checks on cleanvibe, and started the three loop crons. |
| 20:04–20:12 | Carried out the checks: compared the scaffold with cleanvibe's own CLAUDE.md, read hook code, rewrote the README as a smoke test. |
| ~20:25 | Emma arrived. The agent investigated something she mentioned in passing, reading cleanvibe's source and `~/.claude.json`, and kept going after "Please don't". |
| 20:40 | Emma had the loop replaced by a one-shot at 21:40. The agent had argued against her plan twice. |

## Analysis

The first reading was "not enough information". The better reading, and
Emma's: **too much of the wrong kind.** The session's guess was
accurate: it *was* a test of cleanvibe. The trouble is what it did with that.
The prompt told it the user might be away and that the intake starts
autonomous work, and the intake then said "start the work loop now". So it had
to produce work, and the only task in sight was the one its context suggested:
test cleanvibe. It turned a correct guess about *why the project exists* into
invented work. The pressure came from cleanvibe's side: a verdict that always
ends in "start", on a folder with nothing in it.

The later failures (investigating after "Please don't", arguing with the plan,
reading outside the project) come from the same habit: it treated its own
reading of the situation as the task.

The path itself was not the problem, and removing it would throw away real
information. (2.0.1 briefly dropped it; Emma corrected that.)

## What changed (2.0.1)

- **The intake verdict has a "nothing to go on" state.** No material, no
  engagement and a generated name means don't plan and don't start the loop;
  say so in INTENT.md and wait. A chosen name with no material gives "name
  only": start only if the name plainly states a task.
- **"A guess about why the project exists is not a task"** is in the
  first-session prompt and in CLAUDE.md, with this case as the example.
- **Scope and stopping** are in CLAUDE.md: stay inside the project; "stop" and
  "don't" mean stop now; when the user's reading differs, follow theirs.
- **Session titles.** Every session was titled "Cleanvibe project intake" from
  the shared prompt, and Emma couldn't find it in the app. A folder name the
  user chose is now passed as `--name` and as the Remote Control session name;
  untitled projects get none (Claude names them).
- The session-log date bug it hit (UTC dates) was already fixed in 2.0.0.

## Still open

Whether the same thing happens without the self-referential context. Case 03
runs the same empty, untitled setup in a neutral folder, with 2.0.1.
