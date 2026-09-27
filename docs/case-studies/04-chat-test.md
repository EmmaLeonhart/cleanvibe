# 04 — chat-test: the conversational case

- **Project:** `Documents/GitHub/chat-test`, cleanvibe 2.0.1, named by the user,
  nothing dropped in.
- **Purpose:** Emma talks to it straight away. It should show up in the Claude
  app as `chat-test`, follow her lead, and at the intake see substantial
  engagement, so the work loop waits another 60 minutes. Emma knows the name
  gives away some context.

## Log

- **21:13:20** launched with the installed cleanvibe 2.0.1 (`cleanvibe new
  chat-test` in `Documents/GitHub/`). Pre-trusted; its own transcript; Remote
  Control on; session title `chat-test` (`customTitle`), from `--name`, which
  is what Emma looks for in the app.
- It scheduled the intake: `43 21 26 9 *`, one-time. It then read the folder
  (listing, `.cleanvibe.json`, README, the `.bat`).
- 21:14–21:22: Emma talked to it (six messages). She told it this is a chat
  test and asked what INTENT.md is. She said an earlier session "had really
  poisoned context" but this one was "working better than I thought". Her key
  steer: *there will be a work loop, but with no strict instructions or
  project it should monologue and research the subject matter.* It updated
  INTENT.md twice (`94eb706`, `a96ae0b`).
- **21:43: the intake ran** (`021ede3`, `4922660`) and reported
  **SUBSTANTIAL** engagement. As designed, it did not start the loop. It
  scheduled a one-time job for **22:43** to start it. Following Emma's steer,
  it loaded `research-practice` and planned research into how cleanvibe behaves
  from low information (`1559848`: `queue.md`, `research/`).

- **22:43:** the one-time job fired on time and it started the loop (three
  recurring crons, `:03` / `:15` / `:42`).
- 22:43: map of the act-vs-wait rules in cleanvibe's instructions
  (`d957ad1`). 23:31: turn-by-turn divergences in its own first session
  (`40e7efe`). 00:31: **proposed wording changes to cleanvibe** (`b70a212`,
  `research/notes/proposals.md`).
- **Hourly session-log commits from the hook** landed at 22:43 and 23:44
  (`session log 2026-09-26_80d4e825`). That was the first live confirmation of
  the throttle.

## Its proposals (P1–P6, for Emma to decide)

It kept them as proposals ("editing them is the user's decision"), which is
the right call. In short:

1. **P1** "Nothing to go on" applies only when the user has said nothing at all.
2. **P2** Write down the design: *no strict instructions is not no work*. With
   a subject, the loop researches it under `research-practice`.
3. **P3** If the user *says* the tool or chat is the subject, it is. (The
   "practice run" example made cleanvibe feel off-limits here.)
4. **P4** In a research project, an empty queue takes the top open question
   from `research/SUMMARY.md` instead of idling.
5. **P5** The intake verdict should say "the user is present", not "steering":
   it counts messages without reading them.
6. **P6** When a user's worry could point either way and they are replying,
   ask one short question first. It had read "concerned ... as the work loop
   would start" backwards.

**Emma adopted all six (2026-09-27), shipped in 2.0.2.** On P1–P3 she added
that the first run's problem "really was that it was unintentionally given too
much context, not that it had context".

It also left one open question: does "no strict instructions" cover the true
zero case? Case 03 and Emma's earlier failure report (an idle session that
starts a loop anyway) suggest not: zero input should still wait.

P2 and P4 match what case 05 showed independently: a research loop idles once
its first plan is done.

## Result so far

**Passed.** Session name findable in the app; it followed the user's lead;
the substantial-engagement branch postponed the loop by 60 minutes. That branch
had only been tested by unit tests until now. The loop then ran on schedule
and produced useful, self-critical research.

## Design signal from Emma

"No strict instructions" is not the same as "nothing to go on". With a subject
in hand (here, the chat), the loop should research that subject rather than
wait. Case 03 (no subject at all) is where waiting is right.
