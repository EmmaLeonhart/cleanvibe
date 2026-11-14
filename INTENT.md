# What this project is for

_Maintained by Claude: a running read of what the user is trying to do. It is
analysis, not a transcript, and it changes as understanding improves._

## Current understanding

cleanvibe is Emma's tool for running long-lived, mostly unattended Claude Code
sessions, and the practice that goes with it. Three things are going on here:

1. **The tool.** `pip install cleanvibe`: bare `cleanvibe` / `cleanvibe new`
   starts a project as an open-ended session that works from low information
   (the user may say little or be away), keeps `INTENT.md`, and runs a
   half-hourly work loop over `queue.md`. Released on PyPI; currently 2.0.8.
2. **The practice, learned from running many sessions at once.** Rules come
   from observed failures, with Emma's words recorded (`devlog.md`,
   `docs/case-studies/`). Recent ones: work the first queue item only; a
   graceful stop ends one window, not the work; the data lake is a staging
   area; `--no-claude` removed because projects created without their first
   session were unusable.
3. **The research.** A paper on the practice, for arXiv endorsement via a
   clawRxiv paper that reviews well (`paper/`, `paper-replay/`). The replay
   paper's finding: a long-context lapse in a live session is not reproduced
   by replaying its state, so replays can't validate a fix.

The direction Emma raised on 2026-11-12/13: watching an autonomous agent
without polluting its context (a question gets taken as a new instruction and
written down as standing policy), and whether cleanvibe can be commercialized.

## What supports it

- `CLAUDE.md` "Key Decisions" (the v2 spec and every later change, with dates).
- `queue.md`: the paper goal (Emma, 2026-10-03) and the standing duties.
- 2026-11-13: Emma asked for this repo itself to be modernized to cleanvibe 2,
  with no session transcripts committed (public repo, personal details).
  Done the same day: INTENT.md, marker (`"session_log": false`), staleness
  hook, CLAUDE.md trimmed (1.x/replicate decisions in
  `docs/legacy-decisions.md`), CI green again.

## Constraints from Emma

- This repo is public: never commit transcripts or personal details (the
  pc-manager transcript in `scratch/` stays gitignored).
- Never use `--no-claude` (now removed from the tool).
- Ask before anything destructive (her instruction for queue work,
  2026-11-12); publishing private material is irreversible.

## Open questions

- How to commercialize cleanvibe (Emma unsure; discussed 2026-11-13).
- Whether "question vs instruction" message types become a cleanvibe feature.
- clawRxiv has reviewed nothing since 2026-10-16; the paper loop waits on it.

## Confidence

High on what the tool and the practice are; medium on where Emma wants to
take it next.
