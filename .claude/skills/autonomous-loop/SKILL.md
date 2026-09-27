---
name: autonomous-loop
description: Use when the user wants a long stretch of autonomous work (hours, overnight, or while they are away) — set up three local hourly crons (work, flush, status) that keep the work moving, committed and readable. Also use when deciding whether those crons should keep running.
---

# Autonomous loop — three hourly crons

When the user wants you to keep working on your own for a long stretch (hours,
overnight, while they are away), set up three local `CronCreate` jobs. They are
session-local (`durable: false`): they fire only while this session runs and end
with it, so a later session sets them up again if the user still wants
autonomous work. Stagger the minutes so the ticks don't collide:

1. **Work, `3 * * * *`.** Each tick:
   - **Sync.** `git fetch`, then fast-forward or rebase. Never force-push, never
     `reset --hard`, never discard work from another machine or session.
   - **Work.** Take the top item in `queue.md` that you can do, and do it. If
     nothing in the queue is doable, take the next `todo.md` item that is
     unblocked, bounded and checkable, plan it into `queue.md`, then do it.
     If there is still nothing, the tick is **idle**: say so in one line and
     stop there. An idle tick is normal, not a problem to solve.
   - **Commit and push**, deleting finished items from `queue.md` and logging
     them in `devlog.md` in the same commit.
   - **Report** in one line: the commits, or `idle: <reason>`.
2. **Flush, `15 * * * *`.** Commit and push anything left uncommitted. No empty
   commits. (Session transcripts are committed by the session-log hook, not by
   this cron.)
3. **Status, `42 * * * *`.** Report only, no changes: what advanced since the
   last report (commits), the queue as it stands, anything blocked (with its
   not-done tag and the specific blocker), and test health.

## The work keeps the project's normal standards
- Claim something works only after running it. Never weaken, skip or delete a
  test to get green; record the defect instead. Check CI, not only local runs.
- If you don't understand something well enough to build it, write the question
  down (a queue item, or `INTENT.md`) instead of guessing.

These are how the work is done, not reasons to stop the loop.

## Keep the crons running
- **Do not turn the crons off yourself.** Not because the queue is empty, not
  because a tick failed, not because something looks risky, and not at the end
  of a burst of work. Only the user stops them (directly, or through the
  `emergency-stop` skill).
- When something goes wrong, the loop is how the user finds out: report it in
  the next status tick and carry on with whatever is still safe to do.
- If the queue is replanned mid-session, leave the crons alone; the next work
  tick picks up the new top item.
- Not sure the user wants the loop at all? Ask with AskUserQuestion rather than
  starting or stopping it on a guess.

**Why:** long autonomous stretches usually fail by quietly losing the thread.
The work tick keeps progress steady and committed, the flush makes sure nothing
is lost, and the status tick keeps the thread readable for when the user comes
back.

Replication projects (`cleanvibe replicate`) are bounded jobs and do not use
the loop.
