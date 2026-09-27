# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

---

## Active

Emma's decisions (2026-09-27, after the case studies):

1. **One simple loop: every 30 minutes, commit + push, keep working the queue.** Replace the three-cron `autonomous-loop` (hourly work, flush, status reports) with a single recurring cron every half hour whose prompt is just: commit and push any and all changes, then continue working on the queue. No status or flush crons (Emma: the reports and flushes weren't useful; the complicated loop helped earlier, when agents made up problems more and her work was hard and well-defined, but now it's worse). Keep: only the user stops it; an idle tick is fine; P4's research refill. Update the skill, the v2 CLAUDE.md intake step 5, this repo's CLAUDE.md cron section, tests.
2. **Adopt all six chat-test proposals** (case study 04). P1: "nothing to go on" means the user has said nothing at all. P2: no strict instructions is not no work. P3: if the user says the tool or chat is the subject, it is (Emma: the first run's problem was being given too much context by accident, not having context). P4: a research queue refills from `research/SUMMARY.md` open questions. P5: the intake says the user is "present", not "steering". P6: ask one short question when a present user's worry could point either way.
3. **Ship it:** tests, `pages/updates.md` (full new skill text), release 2.0.2, upgrade the local install, note the outcome in case study 04.
---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `2.0.1`.
