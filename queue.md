# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

---

## Active

**cleanvibe 2 (v2.0.0): the general-purpose rework.** Emma's spec is in `devlog.md` (2026-09-26, "cleanvibe 2 — the spec"). The goal is still vague at the start of most sessions, so v2 starts every session as a conversation: minimal assumptions, ask with AskUserQuestion when unclear, keep a running `INTENT.md` of what the user seems to be doing, and save transcripts into git. The 1.x modes stay available under `cleanvibe legacy <cmd>` (deprecated, with a warning). `replicate` stays top-level and unchanged, as a core, intentionally rigid use case. Emma asked for perfectionism, then a practice project she can open and try.

1. **`tests/scratch/.gitkeep`.** Emma expects the practice directory to exist in the repo. Track `.gitkeep` and ignore everything else in it.
2. **Docs + version 2.0.0.** README rewrite (v2 first, legacy section), CLAUDE.md (architecture + Key Decisions), site, `pages/updates.md` (skill changes for existing repos), memory. Not released; that is Emma's call.
3. **Practice project for Emma.** Scaffold a v2 project in `tests/scratch/` with the real CLI and launch its session via the new launcher from this (agent) session. That is the exact child-session case. Confirm it is not a child session, its transcript lands in `sessions/`, and Remote Control is on, so Emma can pick it up and experiment.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.18.0` (v2.0.0 in progress).
