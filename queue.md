# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

**Hourly status-report cron.** This queue is being worked as extensive work: the closing two items are pinned at the tail in `## Always last` (ensure the hourly cron is running + run an end-of-session summary), per `CLAUDE.md` § "Hourly status-report cron for extensive work". A fresh session starts the cron up front; a re-fill's first item kills it; planning mode disables it.

---

## Active

**cleanvibe 2 (v2.0.0): the general-purpose rework.** Emma's spec is in `devlog.md` (2026-09-26, "cleanvibe 2 — the spec"). The goal is still vague at the start of most sessions, so v2 starts every session as a conversation: minimal assumptions, ask with AskUserQuestion when unclear, keep a running `INTENT.md` of what the user seems to be doing, and save transcripts into git. The 1.x modes stay available under `cleanvibe legacy <cmd>` (deprecated, with a warning). `replicate` stays top-level and unchanged, as a core, intentionally rigid use case. Emma asked for perfectionism, then a practice project she can open and try.

1. **Skills.** Rewrite `autonomous-loop`: one loop for everything (no legacy split). Drop the kill/restart choreography that made agents anxious and switch the crons off; only the user stops them; an idle tick is fine. New `research-practice` skill for general, non-CS research (sources, notes, claims with citations, a living summary). Update `queue-driven-workflow` for v2 (queue/todo/devlog appear when work becomes multi-step, not up front). Update this repo's CLAUDE.md cron section to match.
2. **doctor for v2.** Recognize v2 projects (`.cleanvibe.json`): core files are CLAUDE.md/README.md/INTENT.md; queue.md/devlog.md are checked only when present. Fresh v2 scaffolds must audit clean.
3. **`tests/scratch/.gitkeep`.** Emma expects the practice directory to exist in the repo. Track `.gitkeep` and ignore everything else in it.
4. **Docs + version 2.0.0.** README rewrite (v2 first, legacy section), CLAUDE.md (architecture + Key Decisions), site, `pages/updates.md` (skill changes for existing repos), memory. Not released; that is Emma's call.
5. **Practice project for Emma.** Scaffold a v2 project in `tests/scratch/` with the real CLI and launch its session via the new launcher from this (agent) session. That is the exact child-session case. Confirm it is not a child session, its transcript lands in `sessions/`, and Remote Control is on, so Emma can pick it up and experiment.

---

## Always last — restart the hourly cron and summarize

**These two items stay pinned to the tail of this queue** — below every work item above. They are the closing half of the hourly-status-report lifecycle in `CLAUDE.md` § "Hourly status-report cron for extensive work":

A. **Ensure the hourly status-report cron is running** — start it if this session never did, restart it if a planning burst / queue re-fill killed it (`CronCreate`, every hour on the hour, with a status report).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.18.0` (v2.0.0 in progress).
