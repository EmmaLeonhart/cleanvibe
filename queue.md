# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

**Hourly status-report cron.** This queue is being worked as extensive work: the closing two items are pinned at the tail in `## Always last` (restart the hourly cron + run an end-of-session summary), per `CLAUDE.md` § "Hourly status-report cron for extensive work". A re-fill's first item kills the cron; planning mode disables it.

---

## Active — Make generated projects actually START the hourly status-report cron

**Problem (why this queue exists).** v1.9.0 added the hourly-status-report *vision* to the generated templates — `claude_md()` has the section, `queue_md()` has the preamble note and the pinned `## Always last` section — but it is never wired to actually fire. A freshly scaffolded project's bootstrap sequence (steps 1–7) has **no step that creates the `CronCreate` job**, and the pinned tail says "**restart** the hourly cron" when nothing ever started one. So on a real `cleanvibe new` run the hourly reports never happen. These items make the vision real: the cron is *started* as the opening bookend, killed only on a mid-session re-fill, and restarted + summarized at the tail. Work top to bottom; delete each item in the commit that completes it and append a dated `devlog.md` entry. Mirror into the task tool.

1. **Add a "start the hourly status-report cron" opening step to the bootstrap `queue_md()` template** (`cleanvibe/templates.py`). Make it the new bootstrap **step 1** (renumber the existing 1–7 down): *"Start the hourly status-report cron — `CronCreate`, fires every hour on the hour, prompt = a short status report of where the work stands (what's done, what's in flight, what's next). This monitors the whole bootstrap run so a long autonomous session can't silently lose the thread."* Leave the pinned `## Always last` section at the tail.

2. **Make the `## Always last` pinned section read as a coherent closing bookend** (`queue_md()`). Reword item A from "Restart the hourly updates cron job" to *"Ensure the hourly status-report cron is running — start it if this session never did, restart it if a planning burst / queue re-fill killed it."* so it makes sense whether or not a cron was already running.

3. **Reconcile the `claude_md()` lifecycle so "start" and "kill-first" stop contradicting.** In § "Hourly status-report cron for extensive work", state the full lifecycle explicitly: (a) **START** the cron at the beginning of any extensive work session; (b) when you do a mid-session **large-scale queue re-fill** (a planning burst), the FIRST item of that fill kills the cron and the pinned tail restarts it; (c) entering planning mode disables it; (d) the last two queue items always restart + summarize. The current text only says "the first item kills it," which is nonsensical on a fresh session with no cron yet.

4. **Update bootstrap step "Replace this bootstrap queue with the real project queue"** (`queue_md()`) so it tells the agent: the real queue's first item should *start* the hourly cron (or, on a re-fill, kill it), and the `## Always last` section stays pinned at the bottom.

5. **Mirror the same start-bookend correction into this repo's own `CLAUDE.md`** § "Hourly status-report cron for extensive work", so cleanvibe dogfoods the corrected lifecycle.

6. **Update `tests/test_scaffold.py`.** Add assertions that the generated `queue.md` bootstrap contains a "start the hourly … cron" step, and that `claude_md()` mentions *starting* (not only killing/restarting) the cron. Keep every existing assertion green: `python -m unittest discover -s tests` (currently 75 tests, all must pass).

7. **Release v1.10.0.** Bump `cleanvibe/__init__.py` + `pyproject.toml` to `1.10.0`, add a `devlog.md` entry, run the full suite, commit, tag `v1.10.0`, push `main` + tag, and `gh release create v1.10.0` (triggers the PyPI publish). Verify CI and Publish-to-PyPI both go green.

---

## Always last — restart the hourly cron and summarize

**These two items stay pinned to the tail of this queue** — below every work item above. They are the closing half of the hourly-status-report lifecycle in `CLAUDE.md` § "Hourly status-report cron for extensive work":

A. **Ensure the hourly status-report cron is running** — start it if this session never did, restart it if a planning burst / queue re-fill killed it (`CronCreate`, every hour on the hour, with a status report).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.9.1`.
