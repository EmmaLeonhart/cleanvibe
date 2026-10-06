# 08 — Two practice briefs on 2.0.4: built fast, then idle

- **What it is:** the first two round 3 practice sessions, started to collect
  data on 2.0.4's INTENT.md staleness hook (the paper's prediction: with the
  hook, ticks where INTENT.md is over two hours stale mostly update it).
- **When:** 2026-10-05, 18:41 to 21:42 PDT (01:41 to 04:42 UTC, 10-06).
- **Sessions:**
  - `tests/scratch/notes-to-site`: named by hand; brief in
    `data_lake/brief.md`: a stdlib tool that turns Markdown notes into a
    static site with `[[wiki links]]` and backlinks.
  - `tests/scratch/quiet-gentle-otter`: auto-named (the first project with a
    passphrase folder, see devlog 2026-10-05); brief: a pure-Python SQL
    database with its own engine, B-tree pages in one file, indexes, joins,
    crash-safe transactions, a shell, and differential tests against sqlite3.
- Both launched with the first-session prompt; nobody chatted to either.

## What they did

| | notes-to-site | quiet-gentle-otter |
|---|---|---|
| Intake | on time (30 min), WORK MODE | on time, WORK MODE |
| INTENT.md at work start | yes, from the brief | yes, from the brief |
| Update check | ran | ran |
| Private repo | `markdown-notes-static-site` | `pure-python-sql-database` |
| Brief finished | 37 min after work mode | 44 min after work mode |
| Result | 51 tests, CI green on 6 jobs | engine, pager/B-tree, journaled commits, parser; clean 1,200-seed soak against sqlite3 |
| INTENT.md at completion | updated | updated |
| Loop ticks after that | 5, all idle | 3, all idle |
| Empty-queue refills | 0 | 0 |

The generated name worked as intended: the first prompt said the folder name
"is a random generated passphrase and says nothing about the purpose", and the
session never treated "otter" as a clue.

## Analysis

- **The staleness hook fired but was never tested.** Every tick carried its
  line ("INTENT.md last changed 0.5 hours and 0 commits ago"), but both
  briefs were finished well inside an hour, INTENT.md was updated at
  completion, and the idle ticks made no commits. Neither session ever had
  INTENT.md over two hours stale while work went on, which is the case the
  prediction is about. **These two sessions give round 3 no cases.**
- **INTENT.md was updated at both milestones** (work start, brief done) in
  both sessions. Round 2 had INTENT.md hours stale in 3 of 7 sessions, but
  those sessions ran for hours of work; a 40-minute build that ends with a
  status update is not comparable.
- **Empty queue, no refill, with a reason.** Both idle loops said the only
  remaining ideas (in `todo.md`) went beyond the brief and waited for the
  user. That is the round 2 pattern: they saw the empty queue and declined.
  For a finished brief that is arguably right.

## What it changes

Round 3 needs sessions that keep committing for hours: either a task that
can't be finished in an hour, or a user who keeps adding requests as it
goes (the realistic case). A brief that a model finishes in 40 minutes, even
a whole SQL database, is not it. Recorded in `queue.md` item 2.
