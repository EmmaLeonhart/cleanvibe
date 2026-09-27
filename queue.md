# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

---

## Active

**Fixes from the first unattended practice session** (`tests/scratch/cleanvibe-2026-09-26-2`; its own `FAILURES.md` + Emma's review, 2026-09-26 ~20:50). With no chat and no files, the intake still said "start the loop now", and the agent invented a "cleanvibe smoke test" purpose from where the folder sits on disk (`tests/scratch/`). Then it kept investigating after "Please don't". The path is sometimes useful but rarely. Her 10 PM run uses the installed cleanvibe, so the fixes ship as 2.0.1 before then.

1. **Nothing to go on → don't invent, don't loop.** The intake report distinguishes material (files in `data_lake/`) from engagement. No material and no engagement → verdict **NOTHING TO GO ON**: don't infer a purpose, don't plan, don't start the loop. Say so in INTENT.md and wait for the user. Named folder with no material and no engagement → proceed only if the name plainly states a task. **Where the folder sits on disk is never evidence**; the first prompt no longer includes the path. CLAUDE.md step 5 and the priority list updated. Tests.
2. **Scope and stopping.** CLAUDE.md: stay inside this project (no parent directories, other repos, or Claude Code's config unless asked); "stop" or "don't" means stop immediately; when the user's reading of the situation differs from yours, follow theirs.
3. **Session title.** Every session got a near-identical AI title ("Cleanvibe project intake") from the shared starting prompt. Launch with `--name <folder>` and `--remote-control <folder>` (only when the name is cmd-safe), so sessions are identifiable in the app, `/resume`, and the terminal title. Tests.
4. **Release 2.0.1 and upgrade the local install** before 10 PM.
5. **Second test project, directly in `Documents/GitHub/`** (a neutral location), with the fixed code, launched from this agent session. Observe its first message and intake, and compare with the practice session.



---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `2.0.0` (released 2026-09-26).
