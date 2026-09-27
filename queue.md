# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

**Hourly status-report cron.** This queue is being worked as extensive work: the closing two items are pinned at the tail in `## Always last` (ensure the hourly cron is running + run an end-of-session summary), per `CLAUDE.md` § "Hourly status-report cron for extensive work". A fresh session starts the cron up front; a re-fill's first item kills it; planning mode disables it.

---

## Active

From Emma's 2026-09-26 AskUserQuestion answers. Raw `.jsonl` logs stay committed (no change). The general-purpose rework comes later today and is out of scope here.

1. **`cleanvibe chat` launches with Remote Control.** Emma meant a Remote Control start, not only an optional folder name. `_launch_claude(..., remote_control=True)` for chat → `claude "<prompt>" --remote-control`, unnamed. The flag goes AFTER the prompt: `--remote-control [name]` takes an optional value and would swallow a following prompt as the session name. Same in chat's `!runClaude.bat`. Tests + CLAUDE.md/README.
2. **Write the missing "Hourly status-report cron for extensive work" section in CLAUDE.md.** `queue.md`'s header references it and it does not exist. Base it on the `autonomous-loop` skill's status-report cron and the lifecycle the queue header already describes.
3. **Release v1.18.0.** After 1–2 land and CI is green: `gh release create v1.18.0` with notes from the devlog, then confirm `publish.yml` pushes it to PyPI.
4. **Refresh stale bits.** Website (`pages/index.html`): add `research` + `original` cards and check every claim against the code. Check the `pages/updates.md` scope line, README and CLAUDE.md for outdated assumptions. Version bump to 1.19.0 if anything user-facing changes.
5. **`cleanvibe doctor`** (from `todo.md`). A read-only audit of a cleanvibe repo for drift: ticked/"done" items left in queue.md, a queue.md version pointer that doesn't match the package, devlog missing releases that exist as git tags, missing CI workflow, missing scaffold files, CLAUDE.md references to sections that don't exist. `--fix` only for safe ones, if any. Tests, docs, remove from `todo.md`.

---

## Always last — restart the hourly cron and summarize

**These two items stay pinned to the tail of this queue** — below every work item above. They are the closing half of the hourly-status-report lifecycle in `CLAUDE.md` § "Hourly status-report cron for extensive work":

A. **Ensure the hourly status-report cron is running** — start it if this session never did, restart it if a planning burst / queue re-fill killed it (`CronCreate`, every hour on the hour, with a status report).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.18.0`.
