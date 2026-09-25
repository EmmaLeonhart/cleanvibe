# scratch-2026-09-25 — Devlog

**This file is where "done" lives.** `queue.md` is delete-only: when a queue
item is finished, the item is **deleted from `queue.md`** and a dated entry
is **appended here**, in the same commit as the work, then pushed. Never
tick a box in place — a checked box left in `queue.md` is the failure mode
this file exists to prevent.

Also record releases (tag + a one-line note), notable milestones, and
anything else worth a chronological trail. Newest entries at the bottom.

This is the **same convention as the cleanvibe repo's own `devlog.md`** —
every cleanvibe-scaffolded project gets one for the same reason.

See `CLAUDE.md` § "Workflow Rules" and `queue.md`'s preamble.

---

## 2026-09-25 — Project scaffolded

Scaffolded with `cleanvibe new` (cleanvibe v1.17.0). Future entries
land here as queue items get deleted.

## 2026-09-25 — Three-cron playbook started

Scheduled the three session-local crons via `CronCreate`: work-loop at
`:03`, auto-flush at `:15`, status-report at `:42`. They are session-only and
auto-expire after 7 days. No GitHub remote exists yet (that is bootstrap
step "Go live"), so pushes are a no-op until then.

## 2026-09-25 — Triage of user-supplied files (nothing to move)

Checked the repo root for user-dropped material. The only non-scaffold file is
`!runClaude.bat`, the launcher added in 3e8fc6d, which must stay at the root.
`data_lake/` stays empty (just `.gitkeep`); no zips, no LFS-sized files.

## 2026-09-25 — Quatrix LaTeX source rebuilt for arXiv (user-directed side task)

Rebuilt LaTeX source for "Quatrix: An Empirical Evaluation of Q-Compass and
SAVO" (Zenodo 10.5281/zenodo.19839718) from its PDF, because no source exists
publicly (Zenodo and github.com/Abd0r/* checked; 30 commits of the quatrix
repo contain only PDFs). Work is in `arxiv/quatrix/`, local only.

- The 18 figures are cropped from the original PDF as vector PDFs (`figs/`), so they
  match the original exactly. Text, equations, 11 tables and the 32 references are
  transcribed by hand (split across parallel subagents by section).
- `main.tex`: article 11pt A4, newtx, onehalfspacing, `[H]` floats (plus
  `[t]`/`[tbp]` where the original floated), which reproduces the original's
  32 pages. Figure/table pages match the original through p23; the rest are off by
  at most one page.
- Checked with `tools/ngramcheck.py`: every 8-word window of the original occurs
  in the rebuild and vice versa, except float seams and extraction spacing.
- `quatrix-arxiv.tar.gz` (main.tex, sections/, figs/, 00README.json)
  compiles cleanly on its own in a fresh folder. `SUBMISSION.md` has the form
  fields and a 1,754-char condensed metadata abstract (the original abstract,
  ~2,480 chars, exceeds arXiv's 1,920 limit) for the author to approve.
- The three hourly research crons were stopped for this task.
