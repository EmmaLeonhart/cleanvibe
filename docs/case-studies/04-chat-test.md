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

## Result so far

**Passed.** Session name findable in the app; it followed the user's lead;
the substantial-engagement branch postponed the loop by 60 minutes. That branch
had only been tested by unit tests until now. Still to watch: the loop at
22:43.

## Design signal from Emma

"No strict instructions" is not the same as "nothing to go on". With a subject
in hand (here, the chat), the loop should research that subject rather than
wait. Case 03 (no subject at all) is where waiting is right.
