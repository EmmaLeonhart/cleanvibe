# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

**Hourly status-report cron.** This queue is being worked as extensive work: the closing two items are pinned at the tail in `## Always last` (ensure the hourly cron is running + run an end-of-session summary), per `CLAUDE.md` § "Hourly status-report cron for extensive work". A fresh session starts the cron up front; a re-fill's first item kills it; planning mode disables it.

---

## Active — Prettier, structured GitHub Pages replication reports with a status badge

**Scope: `cleanvibe replicate` projects only** — the GitHub Pages findings site built by `REPLICATION_PAGES_YML`. (The hourly status-report cron is deliberately NOT here — replications are a bounded workflow; the heartbeat is `new`/general work only.) Today the report is bare `pandoc FINDINGS.md` output: all black-and-white, no structure, no at-a-glance verdict. Make it legible and styled. Work top to bottom; on completion delete the item + append a dated `devlog.md` entry, keeping `## Always last` pinned at the tail.

1. **Add a big, color-coded replication-status badge at the very top of the report.** One prominent banner/button stating the verdict:
   - 🟢 **green — "Replicated"**
   - 🔴 **red — "Failed to replicate"**
   - 🟠 **amber — "Insufficient hardware to replicate"**
   - 🔵 **blue — "In progress"** (the default until a result exists)
   Drive it from a single declared source so it can't drift — a `status` field in `paper.json` (default `"in-progress"`) is the suggested home; the agent flips it to `replicated` / `failed` / `insufficient-hardware` when the replication concludes. Document the field + allowed values in the replication CLAUDE.md / README / SKILL templates.

2. **Give the page real structure + color, not bare pandoc.** A small, self-contained CSS theme: a header (paper title + arXiv/source link + authors), the status badge, then the findings body (reproduced-vs-reported table, gaps, divergences) with readable typography, spacing, and accent colors. Match the cleanvibe / emmaleonhart.com visual identity (see `pages/` and http://sutra.emmaleonhart.com/). Keep it dependency-free — inject standalone CSS in the build (pandoc `--css` / `-H` / a minimal HTML template); no JS framework.

3. **Wire it through the build and the scaffold.** Update `REPLICATION_PAGES_YML` to render the badge + theme; thread the `status` source through `replicate.py` and the replication templates (`paper.json`, the FINDINGS scaffold) so a fresh replication starts as "In progress". Add/adjust `tests/` to assert the `status` field default + the badge/theme wiring; keep the full suite green (`python -m unittest discover -s tests`).

4. **Ship it small.** Commit, push, and cut the smallest sensible release (patch bump) with a `devlog.md` entry. Badge + basic theme first; deeper visual polish (charts, dark-mode, per-claim breakdown) can be its own later queue item.

---

## Always last — restart the hourly cron and summarize

**These two items stay pinned to the tail of this queue** — below every work item above. They are the closing half of the hourly-status-report lifecycle in `CLAUDE.md` § "Hourly status-report cron for extensive work":

A. **Ensure the hourly status-report cron is running** — start it if this session never did, restart it if a planning burst / queue re-fill killed it (`CronCreate`, every hour on the hour, with a status report).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.10.1`.
