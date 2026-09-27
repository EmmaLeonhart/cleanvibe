---
name: autonomous-loop
description: Use when the user wants a long stretch of autonomous work (hours, overnight, or while they are away) — set up one local cron that every half hour commits and pushes everything and keeps working the queue. Also use when deciding whether that cron should keep running.
---

# Autonomous loop — one cron, every half hour

When the user wants you to keep working on your own for a long stretch (hours,
overnight, while they are away), set up **one** local `CronCreate` job:

- **Schedule:** `7,37 * * * *` (every half hour, off the busy :00/:30 marks),
  recurring.
- **Prompt:** `[cleanvibe cron] Commit and push any and all changes, then
  continue working on the queue.`

That's the whole loop. Each time it fires:

1. **Commit and push** everything that has changed, with messages that say what
   and why. Push only if the repo has a remote. No empty commits.
2. **Continue working on the queue.** Take the top item in `queue.md` you can
   do and do it, then the next, for as long as it makes sense. Delete finished
   items from `queue.md` and log them in `devlog.md` in the same commit.
3. **When the queue runs dry, refill it before idling.** In a research project,
   take the top open question in `research/SUMMARY.md`, plan it into
   `queue.md`, and work it. Otherwise take the next `todo.md` item that is
   unblocked, bounded and checkable. If there is truly nothing, the tick is
   **idle**: say so in one line. An idle tick is normal, not a problem to solve.

The job is session-local (`durable: false`): it fires only while this session
runs, so a later session sets it up again if the user still wants autonomous
work.

## The work keeps the project's normal standards
- Claim something works only after running it. Never weaken, skip or delete a
  test to get green; record the defect instead.
- If you don't understand something well enough to do it, write the question
  down (a queue item, or `INTENT.md`) instead of guessing.

These are how the work is done, not reasons to stop the loop.

## Keep it running
- **Do not turn the cron off yourself.** Not because the queue is empty, not
  because a tick failed, not because something looks risky, and not at the
  end of a burst of work. Only the user stops it (directly, or through the
  `emergency-stop` skill).
- If something goes wrong, say so plainly in your next message and carry on
  with whatever is still safe to do.
- In a cleanvibe project, the thirty-minute intake in CLAUDE.md decides when
  the loop starts. Elsewhere, start it when the user asks for autonomous work.

**Why one cron:** earlier versions ran separate hourly work, flush and status
crons. In practice the flushes and status reports weren't useful, and one
item per hour left long idle stretches (case study 05). One half-hourly
"commit, push, keep going" does the work with less ceremony.

Replication projects (`cleanvibe replicate`) are bounded jobs and do not use
the loop.
