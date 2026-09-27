# 05 — ai-history-analysis: the first real run, started from a brief

- **Project:** `Documents/GitHub/narrative_identity/submodules/ai-history-analysis`,
  cleanvibe 2.0.1, named `ai-history-analysis` (chosen, not generated).
- **Started:** 2026-09-26 22:23 PST by Emma's scheduled job (the "10 PM run").
  Whatever created it dropped `AI-HISTORY-BRIEF.md` (92 lines, written from
  Emma's dictated instructions) at the top level. Nobody chatted with it until
  00:31.
- **Why it matters:** the first project whose main input was files. It is the
  case cleanvibe 2's data lake and intake were built for, and the last untested
  branch.
- **Sources:** the project's git history, its transcript (inspected with
  `scratch/inspect_session.py`), INTENT.md, `research/`, `queue.md`.

## What it did

| Time (PST) | |
|---|---|
| 22:23 | Scaffold commit. Pre-trusted, its own transcript, Remote Control on, session titled `ai-history-analysis` (`--name`). |
| 22:24 | Scheduled the intake (`54 22 26 9 *`, one-time). First INTENT.md read straight from the brief: "a sourced, followable history of the AI boom" (`67fdc2e`). |
| 22:54 | Intake: snapshot commit, then `AI-HISTORY-BRIEF.md` moved into `data_lake/`. Verdict: **little or no engagement, but there is material → start now.** |
| 22:54 | Loaded `research-practice` and `autonomous-loop`; planned `research/SUMMARY.md`, `sources.md`, `todo.md`, `queue.md` from the brief (`74d5e50`); started the three hourly crons. |
| 22:55 | First research note: the pre-ChatGPT timeline, answering the brief's "was GPT-3 publicly available?" question. |
| 23:17 | Work tick: RLHF lineage, with Emma's framing set beside the record, not over it. |
| 00:18 | Work tick: when each capability arrived, 2020–2025. |
| 00:31 | Emma: "commit and push please into a private repo". It created `EmmaLeonhart/ai-history-analysis` (private), pushed, and re-created the work and flush crons so they push too. |

## Assessment

**Passed**, and it did the job the brief asked for.

- **Followed the material.** INTENT.md, `research/SUMMARY.md` and the queue all
  come straight from the brief. It picked the right practice skill
  (`research-practice`) without being told.
- **Research quality.** Three labelled layers kept apart throughout: **[doc]**
  sourced history, **[Emma]** her interpretations, **[synth]** its own
  synthesis, as the brief asked. Dated claims carry sources (`sources.md`, 14
  entries) and confidence. It flagged dates written "from memory" as to-check
  items instead of passing them off as sourced.
- **Stayed in scope.** It worked only in its own repo, even though it sits
  inside `narrative_identity`.
- **Transcripts.** The Stop hook refreshed `sessions/` after every response.
  Its hourly commit had nothing to do because each research commit
  (`git add -A`) swept the transcript in. That is the documented behavior.

## What it shows about the design

- **The loop is slow.** Three queue items in about 90 minutes; eight still
  queued. The work tick fires hourly and does one item, then the session sits
  idle for the rest of the hour. For an unattended research run that is a lot
  of idle time. A shorter work interval, or a tick that keeps taking items
  until a time budget runs out, would do more. (NEEDS-DECISION: Emma.)
- **The agent adjusted its own crons** (00:31) to add pushing once a remote
  existed. It was a reasonable response to the user's request, not a
  violation of "only the user stops them", but it is the first time an agent
  edited the loop.
- **Queue numbering** kept the original numbers (4–11) after items were done.
  That's harmless.
