# 06 — ai-context-research: cleanvibe studying its own transcripts

- **Project:** `Documents/GitHub/ai-context-research`, cleanvibe 2.0.2, named
  by Emma. Started 2026-09-28 21:57 PST. Emma: "make a clean vibe research
  paper… look at the other projects… their transcripts are preserved…
  seeing what strategies work and don't work… posting this on ArXiv".
- **What it is:** a research project whose evidence is other cleanvibe
  sessions' `sessions/*.jsonl`: chat-test (04), untitled-cleanvibe-project
  (03), the 2026-09-28 untitled research session, and itself. The
  write-up is `ai-context-research/paper/draft.md` (builds to PDF with
  `scripts/build_paper.py`). Its data and code are in `research/` and
  `scripts/`.
- **Why it matters:** it is the first systematic look across sessions rather
  than at one. It also produced the 2.0.3 changes, the same way case study
  04 produced 2.0.2.

## Method in one paragraph

`scripts/transcript_metrics.py` mines each session's jsonl and git log
(human messages, cron fires, tool calls, commits, INTENT.md commits, peak
context). It also writes one row per cron-fired turn, recording which files
that turn actually read. 20 CLAUDE.md and skill rules were coded
followed / violated / over-applied / n/a per session. The coding was done
twice: once by the analysing agent, and once blind by a fresh subagent that
read only the raw transcripts (κ = 0.69).

## What it found (four sessions, so read these as case evidence)

- **Most rules held.** The pinned one-shot intake, following the verdict,
  commit cadence, staying in the project, and never inventing a purpose held
  everywhere.
- **The unprompted standing duties failed.** INTENT.md went stale for
  3–5.5 h while commits kept landing. The README stayed a stub. The update
  check never ran in any session. When the untitled session's queue ran dry,
  the loop went idle twice instead of refilling it, until Emma asked "Why
  empty why not working". **0 of 22 loop ticks read INTENT.md**, while 18
  committed. The ticks did what the tick prompt named and nothing else.
- **Human corrections were misreadings of Emma, not of the rules** (04's
  "poisoned context"; "you must have hallucinated that" in the untitled
  session). Both times the agent inferred instead of asking.
- **The parts contradicted each other.** In 2.0.1 the skill said three hourly
  crons while CLAUDE.md said one half-hourly cron. research-practice put
  downloads in `data_lake/`. Claude Code's own memory instructions led an
  agent to write into `~/.claude/projects/…/memory`, which CLAUDE.md forbids.
- **Times were estimated, not read.** Reported cron times were off by
  7–30 min (because of jitter), and the analysing agent itself wrote
  unchecked times three times, overestimating each one.
- **The `.md` logs dropped `[cleanvibe cron]` prompts**, so a reader saw loop
  actions without their triggers.
- **A retraction worth keeping:** a broader claim, "adherence falls the less
  a rule is prompted", looked strong under the agent's own post-hoc coding
  and fell to noise under blind coding. The paper reports it as unsupported.

## The fix (2.0.3)

M1 the tick prompt names the duties (refill, re-read and refresh INTENT.md,
README, clock) · M2 the first and resume prompts name the update check ·
M3 "times come from the clock" · M4 quote the user before recording their
stance, and ask if the input was dictated or ambiguous · M5 downloads go in
`data_lake/downloads/`, the harness memory directory counts as outside the
project, and the update check verifies the parts agree · M6 the log renders
`## Cron` prompts · M7 chat-only constraints go in INTENT.md (they survive
compaction) · M8 prose goes through the file tools, dependent shell steps are
chained, and an edit is checked before it is logged. Emma approved applying
all eight on 2026-09-29.

**Still untested:** no session in the corpus reached context compaction, so
the biggest risk the literature predicts (losing constraints at compaction)
is unobserved. M7 is a guess until one does.
