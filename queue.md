# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

**Hourly status-report cron.** This queue is being worked as extensive work: the closing two items are pinned at the tail in `## Always last` (ensure the hourly cron is running + run an end-of-session summary), per `CLAUDE.md` § "Hourly status-report cron for extensive work". A fresh session starts the cron up front; a re-fill's first item kills it; planning mode disables it.

---

## Active — `cleanvibe original` smoke test

`cleanvibe original` shipped in v1.16.0 (see `devlog.md`). Remaining:

1. **Smoke test** — scaffold a real `cleanvibe original` run in a gitignored dir (`tests/scratch/`) with `--no-claude`, confirm the tree (incl. `topics/`), then move to running it for real (launch Claude into it).

---

## Always last — restart the hourly cron and summarize

**These two items stay pinned to the tail of this queue** — below every work item above. They are the closing half of the hourly-status-report lifecycle in `CLAUDE.md` § "Hourly status-report cron for extensive work":

A. **Ensure the hourly status-report cron is running** — start it if this session never did, restart it if a planning burst / queue re-fill killed it (`CronCreate`, every hour on the hour, with a status report).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.16.0`.
