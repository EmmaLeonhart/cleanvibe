"""Canonical cleanvibe skills — single source of truth.

These were previously inlined into every scaffolded CLAUDE.md (via templates.py).
They are now standalone Claude Code skills, written to ``.claude/skills/<slug>/SKILL.md``
both globally (~/.claude/skills/) and in every cleanvibe repo. ``write_skills`` is the
one function that materializes them; scaffold modes and the migration script both use it.

String-constant storage (not package-data files) mirrors templates.py and preserves the
zero-package-data / flat-layout packaging guarantee.
"""
from __future__ import annotations

from pathlib import Path

_EMERGENCY_STOP = """---
name: emergency-stop
description: Use when the user sends a continuous series of "stop" messages (e.g. "stop stop stop") or otherwise very explicitly demands an immediate halt — kill all running processes, background jobs, and GitHub Actions runs for this repo, then take no further actions.
---

# Emergency Stop Mode

If the user sends a continuous series of "stop" messages (e.g. "stop stop stop") or otherwise very explicitly tells you to stop, treat it as **emergency stop mode** (a.k.a. emergency exit mode). This OVERRIDES every other instruction, including CLAUDE.md and any other skill.

When in emergency stop mode:

- **Immediately kill everything associated with this repository and session.** Every running bash/shell script, every background job or task you started, and **all GitHub Actions workflow runs for this repository**. **Force-kill the GitHub Actions runs** (e.g. `gh run cancel <id>`, and `gh run delete <id>` if needed) for every in-progress run. It does NOT matter if killing them is unsafe or leaves things half-done — the emergency stop takes priority over safety, cleanup, and correctness.
- **Do not investigate. Do not reverse or undo anything.** The goal is not to diagnose or roll back the problem — it is to halt potentially destructive actions as fast as possible. Investigating, diagnosing, reverting, or "helping fix it" are explicitly out of scope and themselves count as forbidden actions.
- **Ignore repetitive messages.** Do not treat repeated "stop" messages as a request to do anything further. Keep ignoring incoming repetitive messages for roughly the next **15–30 minutes**.
- **You may answer direct questions, but you may NOT take actions.** Answer only from context you already have. Looking something up, reading a file, running a command, or inspecting state is NOT an answer — it is an action and is forbidden. If you cannot answer from context already in hand, do not answer.
- **Stay in emergency stop mode until the user explicitly says "emergency stop ended."** Only after that exact signal do you resume any normal work.
"""

_CRON_IS_LOCAL = """---
name: cron-is-local
description: Use when the user says "cron job", "cron", or asks to "schedule" a task — they mean the in-session CronCreate tool firing locally on their own running computer, with standing consent; just set it up.
---

# Cron jobs and scheduled work — LOCAL by default

**When the user says "cron job", "cron", or asks to "schedule" a task, they mean the in-session `CronCreate` tool** — a prompt scheduled to fire locally, inside this Claude Code session, on the user's own running computer. This is the default and the assumption. Do NOT interpret it as anything else unless the user explicitly names a different mechanism.

- **It is local and in-session — use the `CronCreate` tool.** A generic "cron" request is NOT an OS crontab, NOT a GitHub Actions / CI `schedule:` trigger, and NOT a cloud scheduler. (A repo may *also* contain its own GitHub Actions cron schedules — those are a separate thing and are not what the user means when they ask *you* to set up a cron.) The user leaves the computer on and this session running so the scheduled prompt can execute.
- **The user is deliberately away from the keyboard.** They schedule work precisely so it runs while they are out of the house and not physically present. Their absence is the normal, expected condition for these jobs — it is NEVER a reason to delay the work, ask "are you sure?", wait for them to return, or refuse to proceed.
- **Standing consent — just set it up.** Cron / `CronCreate` requests are pre-authorized. Create the job immediately and locally, then report what was scheduled. Do not block on confirmation or follow-up questions.
"""

_AUTONOMOUS_LOOP = """---
name: autonomous-loop
description: Use when the user wants a long stretch of autonomous work (hours, overnight, or while they are away) — set up one local cron that every half hour commits and pushes everything and keeps working the queue. Also use when deciding whether that cron should keep running.
---

# Autonomous loop — one cron, every half hour

When the user wants you to keep working on your own for a long stretch (hours,
overnight, while they are away), set up **one** local `CronCreate` job:

- **Schedule:** `7,37 * * * *` (every half hour, off the busy :00/:30 marks),
  recurring.
- **Prompt:** `[cleanvibe cron] Commit and push any and all changes, then
  continue working on the queue (refill it from the open questions if it is
  empty). Re-read INTENT.md and update it if your understanding has changed;
  fill in README.md if the purpose is now clear. Check the clock before
  writing any time down.`

That's the whole loop. Each time it fires:

1. **Commit and push** everything that has changed, with messages that say what
   and why. Push only if the repo has a remote. No empty commits.
2. **Continue working on the queue.** Take the top item in `queue.md` you can
   do and do it, then the next, for as long as it makes sense. Delete finished
   items from `queue.md` and log them in `devlog.md` in the same commit.
3. **When the queue runs dry, refill it before idling.** In a research project,
   take the top open question in `research/SUMMARY.md`, plan it into
   `queue.md`, and work it. Otherwise take the next `todo.md` item that is
   unblocked, bounded and checkable. "The remaining items are blocked" is not
   the same as "nothing to do": look for other open questions first. If there
   is truly nothing, the tick is **idle**: say so in one line.
   An idle tick is normal, not a problem to solve.
4. **Keep the standing files current.** Re-read `INTENT.md` and update it if
   your understanding has changed (including constraints the user gave in
   chat). Fill in `README.md` once the purpose is clear.

**Why the prompt names these duties:** in the study of cleanvibe's own
transcripts (case study 06), loop ticks did what the tick prompt named
(commit, work the queue) and skipped everything it didn't: no tick in 22 read
`INTENT.md`, which went stale for hours; the README stayed a stub; and an
empty queue was reported idle instead of refilled. Naming a duty in the
prompt is what makes it reliably happen.

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
"""

_QUEUE_DRIVEN_WORKFLOW = """---
name: queue-driven-workflow
description: Use when the work in a cleanvibe project is software development or any other multi-step build — plan into queue.md first, the todo.md → queue.md → devlog.md flow, delete-don't-check completion, task-tool mirroring, and tests/CI discipline.
---

# Queue-driven workflow (development practice)

In a cleanvibe 2 project nothing is set up for this in advance. When the work
turns into building something over several steps, create `queue.md`, `todo.md`
and `devlog.md` if they don't exist yet, and work this way from then on.

## Workflow Rules
- **Commit early and often.** Every meaningful change gets a commit with a clear message explaining *why*, not just what.
- **Plan into `queue.md` first, then execute.** When entering planning mode (or doing any non-trivial multi-step work), the FIRST action is to write the plan into `queue.md` as concrete items. Only then begin executing. This means an interrupted session can resume from the queue — the plan does not live only in chat context.
- **Finishing an item = delete from `queue.md` + append to `devlog.md`, then commit and push.** When a queue item is done, **delete the item from `queue.md`** and **append a dated entry to `devlog.md`** recording what was completed, in the *same commit as the work*, then push (if the repo has a remote). Never mark an item done in place (no `[x]`, no "✓", no "DONE"). `queue.md` only ever holds not-yet-done work; `devlog.md` is where "done" lives.
- **Mirror `queue.md` into the task tool.** TaskCreate items as you add them to queue.md; mark `in_progress` when starting; `completed` when done. The two views must not drift.
- **Keep CLAUDE.md up to date.** As the project takes shape, record architectural decisions, conventions, and anything needed to work effectively in this repo.
- **Update README.md regularly.** It should always reflect the current state of the project for human readers.

## Queue and longer-horizon work
- **`queue.md`** — what's being worked on right now. Items get deleted on completion; do not leave checkmarks or status indicators behind. If it's not in `queue.md`, it's not in scope for the current session.
- **`todo.md`** — the **long-term horizon** of the project. Multi-session goals, architectural ambitions, future capabilities. Items in `todo.md` are *abstract*: they describe a destination, not a step. When work begins, an item is pulled from `todo.md`, decomposed into concrete executable steps in `queue.md`, mirrored into the task tool, and executed. As `queue.md` drains, refill it from the next `todo.md` item.
- **`devlog.md`** — where **"done" lives**. Every finished queue item is deleted from `queue.md` and appended as a dated entry here, in the same commit as the work. Releases (tag + one-line note) and notable milestones also go here.
- **Flow:** `todo.md` (abstract horizons) → `queue.md` (concrete steps) → task tool (in-flight work) → `devlog.md` + `git log` (history). Items only ever flow forward.
- **When to stop and hand back:** `queue.md` is empty, what is left in `todo.md` is still too abstract to break down, and tests (and CI, if the project has a remote) pass.

## Testing
- **Write unit tests early.** As soon as there is testable logic, create a test file. Use `pytest` for Python projects or the appropriate test framework for the language in use.
- **Set up CI once the project has a GitHub remote.** A `.github/workflows/ci.yml` that runs the test suite on push and pull request. Keep it simple — install dependencies and run tests.
- **Keep tests passing.** Do not commit code that breaks existing tests. If a change requires updating tests, update them in the same commit.
"""

_RESEARCH_PRACTICE = """---
name: research-practice
description: Use when the work in a project is research on any topic, not only computer science — pinning down the question, gathering and weighing sources, keeping notes with citations, and maintaining a living summary — whether it is a single question or a long-running inquiry.
---

# Research practice

For research on any subject: history, a technical field, a market, a hobby, a
health question, a policy debate. It suits a single question and a long-running
inquiry that grows over months. (Replicating one specific paper is a different
job; that is `cleanvibe replicate`.)

## Layout (create it when the research starts, not before)
- `research/SUMMARY.md`: the living answer. What is known now, how sure, what
  is contested, what is still open. Rewrite it as understanding changes; it
  should always make sense read on its own.
- `research/sources.md`: one entry per source, with the citation or link, date
  accessed, what kind of source it is (primary data, peer-reviewed, reporting,
  opinion, vendor material), what it contributes, and how far to trust it.
- `research/notes/`: one Markdown file per sub-question, with every claim tied
  to a source.
- Downloads and datasets you fetch for the research go in
  `data_lake/downloads/` (committed, kept apart from the user's own material
  in the rest of `data_lake/`); throwaway fetches go in `scratch/`.

## How to work
- **Pin the question down.** If the user is here and replying, ask them
  (AskUserQuestion is fine then): what they want to know, why, how deep to go,
  and what would count as an answer. If they are not, infer the question from
  the chat, the material in `data_lake/` and the project name, write it at the
  top of `SUMMARY.md` as a stated assumption, and start.
- **Survey wide, then go deep.** First map the main positions and the key
  sources; then dig into what matters for the user's question.
- **Every claim gets a source.** Keep what a source says separate from your own
  inference, and label the inference.
- **Weigh sources rather than counting them.** Prefer primary and established
  sources, note dates and conflicts of interest, and when sources disagree,
  record both positions and what would settle it instead of averaging them.
- **Say how sure you are**, in `SUMMARY.md` and when you report back: lead with
  the answer, then the confidence, then the evidence.
- **Long-running inquiries** get a dated "What changed" entry in `SUMMARY.md`
  each session, so the user can see how the picture moved.
- **Link, don't copy.** Quote briefly; never commit whole copyrighted texts.
"""

_WRITING_STYLE = """---
name: writing-style
description: Use when writing any prose — reports, commit messages, devlog entries, PR descriptions, documentation — to avoid the self-congratulatory "honest"/"frank"/"candid"/"transparent" move and name failures flatly instead.
---

# Writing style

Do not use "honest", "honesty", or "honestly" — and do not swap in "frank", "frankly", "candid", "candidly", or "transparently", which are the same self-congratulatory move in a different coat. When something failed, name the failure: "it didn't work", "I got that wrong", "this failed" — flat, no qualifier. Tagging a report "honest" implies the rest aren't, and couching a failure as honesty asks for credit for the admission, which is worse than the failure itself. Use a precise positive word ("accurate", "plainly", "truly") only when that is genuinely the meaning — never as a halo on a bad outcome.
"""

_CLEANVIBE_UPDATE_CHECK = """---
name: cleanvibe-update-check
description: Use at the start of a session in a cleanvibe-scaffolded project, at most weekly — fetch cleanvibe's updates page and refresh this repo's .claude/skills/ to the latest shipped versions.
---

# Check cleanvibe for skill updates (weekly)

This repo's `.claude/skills/` were vendored by **cleanvibe**. cleanvibe ships new and revised skills over time — when one lands, every cleanvibe-scaffolded project should pick it up.

**The check is weekly, not per-session.** At the top of a session, look at the *last cleanvibe update check* date recorded in this repo's CLAUDE.md `## Skills` section. If it has been more than 7 days:

1. **Fetch the current skill index** — `WebFetch https://cleanvibe.emmaleonhart.com/updates.md`. This is the canonical, hand-maintained page describing every skill cleanvibe ships, keyed by the cleanvibe version that introduced or revised it.
2. **Compare against the skills currently in `.claude/skills/`.** If the page lists newer skills or revisions, update the corresponding `.claude/skills/<slug>/SKILL.md` files to match. Match the wording from `updates.md`; don't paraphrase.
3. **Check that the parts agree.** Read the refreshed skills against CLAUDE.md and note any rule they state differently (loop schedule, where downloads go, what counts as outside the project). If they conflict, CLAUDE.md is the project's rule: say so in your report and add a line to `INTENT.md`, rather than following whichever text you read last.
4. **Update the last-check date** in CLAUDE.md's `## Skills` section. Commit with a message describing which skills were refreshed.

If the fetch fails (offline, DNS, page not yet up), leave the date alone and try next session — the check is opportunistic, not mandatory.
"""

SKILLS = {
    "emergency-stop": _EMERGENCY_STOP,
    "cron-is-local": _CRON_IS_LOCAL,
    "autonomous-loop": _AUTONOMOUS_LOOP,
    "queue-driven-workflow": _QUEUE_DRIVEN_WORKFLOW,
    "research-practice": _RESEARCH_PRACTICE,
    "writing-style": _WRITING_STYLE,
    "cleanvibe-update-check": _CLEANVIBE_UPDATE_CHECK,
}


def write_skills(dest_root, *, overwrite: bool = True) -> list:
    """Write every skill to ``dest_root/.claude/skills/<slug>/SKILL.md``.

    Returns the list of Paths written. With ``overwrite=False`` an existing
    SKILL.md is left untouched (used by non-destructive scaffold paths).
    """
    dest_root = Path(dest_root)
    written = []
    for slug, body in SKILLS.items():
        target = dest_root / ".claude" / "skills" / slug / "SKILL.md"
        if target.exists() and not overwrite:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        written.append(target)
    return written
