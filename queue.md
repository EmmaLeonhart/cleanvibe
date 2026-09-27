# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

---

## Active

**cleanvibe 2 (v2.0.0): the general-purpose rework.** Emma's spec is in `devlog.md` (2026-09-26, "cleanvibe 2 — the spec"). The goal is still vague at the start of most sessions, so v2 starts every session as a conversation: minimal assumptions, ask with AskUserQuestion when unclear, keep a running `INTENT.md` of what the user seems to be doing, and save transcripts into git. The 1.x modes stay available under `cleanvibe legacy <cmd>` (deprecated, with a warning). `replicate` stays top-level and unchanged, as a core, intentionally rigid use case. Emma asked for perfectionism, then a practice project she can open and try.

**Deadline: Emma has a scheduled job that runs cleanvibe at 10 PM Pacific (2026-09-26) to research the history of AI, fully automatically. It must work by then.** Her spec from the 7:15 PM voice note: cleanvibe sessions work from low information and may have no human present; a 30-minute data-lake intake; AskUserQuestion only when the user is clearly present; release 2.0.0 and install it locally. No AskUserQuestion to Emma about any of this.

1. **30-minute intake + low-information operation.** Committed stdlib script `.claude/scripts/data_lake_intake.py` in every v2 project. (a) Commit everything in the repo as found ("repository contents 30 minutes in, before moving into data_lake/"). (b) `git mv` every root-level entry that was not committed before (user drops, new directories), except the scaffold and workflow files, into `data_lake/`, and commit ("moved into data_lake/"). (c) Report the moves, the data-lake file list, and user engagement counted from `sessions/*.jsonl`. It records `intake_at` in `.cleanvibe.json` and runs once. The first-session prompt tells the agent to CronCreate a one-shot at +30 min that runs the script, analyzes `data_lake/` (specs/instructions there are followed unless the chat says otherwise), updates INTENT.md, plans work into queue.md when the purpose is clear, then starts the autonomous loop: immediately without substantial engagement, or via a one-shot at +60 min (90 min after start) with it. CLAUDE.md: the low-information philosophy, the data-lake rule (material goes into data_lake/ and is committed as part of the repo's history), the intake procedure. Tests.
2. **AskUserQuestion only when the user is clearly present.** Remove it as a default from v2 CLAUDE.md, the v2 prompts, the skills (`research-practice`, `autonomous-loop`) and the 1.x starting-prompt tail. Otherwise decide, and record assumptions in INTENT.md.
3. **Practice project for Emma.** Scaffold a v2 project in `tests/scratch/` with the real CLI and launch its session via the new launcher from this (agent) session. That is the exact child-session case. Confirm it is not a child session, its transcript lands in `sessions/`, and Remote Control is on, so Emma can pick it up and experiment. (The first attempt stopped at Claude Code's trust prompt; the pre-trust feature now covers that.)
4. **Docs + version 2.0.0.** README rewrite (v2 first, legacy section), CLAUDE.md (architecture + Key Decisions), site, `pages/updates.md` (skill changes for existing repos), memory. Then **release v2.0.0** (Emma gave full permission): GitHub release, confirm PyPI, and `pip install -U cleanvibe` so her local `cleanvibe` is 2.0.0.
5. **10 PM readiness check.** `cleanvibe --version` on PATH is 2.0.0; a dry run of the exact v2 flow succeeds; nothing is left uncommitted.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `2.0.0` (unreleased).
