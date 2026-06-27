# clawrxiv_clone — Work Queue

**This file is a queue of *concrete, executable steps*, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `devlog.md` (a dated entry) and `git log`; longer-horizon, *abstract* work lives in `todo.md` and gets decomposed into items here when it's ready to execute. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Do not add checkmarks, "done" markers, or status indicators in place. If an item is still here, it is not done.

**Why this file exists:** when a planning step (formal planning mode or just "think before doing") produces a plan, that plan is written here BEFORE execution starts. That way an interrupted session can pick up from the queue rather than from chat context that may be gone.

The purpose of this file is also to bound scope. If a task is not in this queue, it is not in scope for the current session. New ideas go at the bottom of the queue (or to `todo.md` if they are longer-term / architectural), not silently into whatever is being worked on.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

**Three-cron playbook.** Extensive work runs under three local `CronCreate` jobs — **work-loop at :03** (the engine that drains `queue.md` and refills it from `todo.md`), **auto-flush at :15** (commit/push backstop), and **status-report at :42** (heartbeat). On a fresh session they are **started** as the opening step (bootstrap step 1 below); on a mid-session **large-scale re-fill** of this queue the FIRST item worked is instead to **kill** the already-running crons. Either way the **last two items are always pinned at the tail** — ensure the three crons are running, then run an end-of-session summary (see the `## Always last` section below and `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook"). Entering planning mode also disables the crons; their restart lives at the end of the queue.

---

## Phase 1 — investigation: DONE (record)

The reverse-engineering of clawRxiv's AI peer review is complete; write-up in
`investigation/FINDINGS.md` with captured live-API evidence (`investigation/samples/`) and the
closest open artifact (`investigation/references/labclaw_peer_review_SKILL.md`). Headline: the
reviewer is a single **Gemini 3 Flash** call per submission returning a fixed JSON review
(`rating` tier, `summary`, 5 `pros`, 5 `cons`, `justification`); endpoint surface + both rubrics
documented. (This bullet is a pointer; the bootstrap section it replaced is in git history.)

## Phase 2 — core clone built (record)

Reviewer (Gemma) + schema + SQLite store + FastAPI publish/read/revise/review API, reviewer
wired to publish, 10 pytest tests green. Further surface (search, comments, vote, frontend,
execution sandbox) lives in `todo.md`; the perpetual crons (started by the pinned tail) will pull
and decompose those next.


---

## CLI enablement — DONE 2026-06-26 (drained; see devlog)

`scripts/review.py` now uses argparse (positional `paper_path` + `-o/--output`, resolves the
path, exits 2 with `error: no such file:` on a missing file); `src/clawrxiv_clone/extract.py`
adds `.tex`/`.pdf`/`.txt` extraction (pypdf added to deps, `tests/test_extract.py` green);
`scripts/review_paper.py` saves the review next to the paper. Experiments run: the Sutra FV
paper → Borderline (clarity 2) and latent-space-cartography → Borderline. Also fixed the
reviewer drifting to a summary on long papers (restate-task-after-paper). History in devlog.

1. **Follow-up: teach `parse_markdown_paper` to recognise a `## Abstract` section.** The
   latent-space-cartography paper uses a `## Abstract` header rather than a blank-line abstract
   block, so `parse_markdown_paper` currently grabs the author line as the abstract. The review
   still read sensibly (the body carries the content), but the `abstract` field handed to the
   reviewer is wrong. Make the parser prefer a `## Abstract` section's text when present.

---

## Always last — restart the three crons and summarize

**These two items stay pinned to the tail of the queue at all times** — below every bootstrap step and below every real work item. They are the closing half of the three-cron lifecycle described in `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook": the crons are **started** at the beginning of extensive work (a fresh session starts them as the opening item; a mid-session large-scale re-fill instead kills the already-running crons as its first item, and planning mode disables them), and these are always the LAST two, after everything else — they bring them back and sign off:

A. **Ensure the three crons are running** — start them if this session never did, restart them if a planning burst / queue re-fill killed them: work-loop (`3 * * * *`), auto-flush (`15 * * * *`), status-report (`42 * * * *`).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

(During first-session bootstrap these simply sit here at the bottom; they become load-bearing the moment the queue is filled with a large batch of created tasks.)

---

## Pointers

- Long-horizon backlog (abstract goals, source of future queue items): `todo.md`.
- Completed work (chronological, with releases): `devlog.md`.
- Narrative history: `git log`.
