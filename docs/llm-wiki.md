# The LLM Wiki pattern and cleanvibe

Design note for the `todo.md` item "Investigate the Carpathes / L-Carpathes
agentic wiki idea". Written 2026-10-03.

## What the idea is

**Assumption:** "Carpathes / L-Carpathes" is a dictation of "(LLM) Karpathy's"
wiki. A web search for "Carpathes" finds nothing about wikis or agents, and
Andrej Karpathy published an "LLM Wiki" idea file in April 2026 that matches
the description (agents, pages, edits). If the item meant something else,
this note answers the wrong question.

Karpathy's [`llm-wiki.md` gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
is a pattern to paste into a coding agent, not a library. Instead of
retrieving raw chunks at query time (RAG), the agent compiles the sources once
into a persistent, interlinked Markdown wiki and keeps it current.

- **Three layers:** `raw/` (immutable sources the agent reads and never edits),
  `wiki/` (Markdown pages the agent owns entirely), and a schema file
  (`CLAUDE.md` / `AGENTS.md`) with the maintenance conventions.
- **Two fixed files:** `index.md`, a catalog of pages; `log.md`, an
  append-only ledger with a parseable header per entry
  (`## [YYYY-MM-DD] action | title`).
- **Three operations:** *ingest* (one source typically updates 10–15 pages:
  entities, concepts, cross-references), *query* (answers can be filed back as
  new pages), and *lint* (periodic checks for contradictions, stale claims,
  orphan pages, missing links).
- **Scale:** up to roughly 100 sources and a few hundred pages, `index.md`
  alone is enough for navigation; beyond that it needs a search tool.

Secondary write-up used for the details above:
[akitaonrails/ai-memory, research-karpathy-llm-wiki.md](https://github.com/akitaonrails/ai-memory/blob/main/docs/research-karpathy-llm-wiki.md).

## How it maps onto cleanvibe

| LLM Wiki | cleanvibe today |
|---|---|
| `raw/`, immutable | `data_lake/`: committed, filled by the user and by the thirty-minute intake. Nothing says the agent must not edit it. |
| `wiki/` pages | `research-practice`: `research/notes/` (one file per sub-question) and `research/SUMMARY.md` (the living answer). Organised by question, not by entity or concept, and with no cross-links required. |
| `index.md` | none; `SUMMARY.md` is the closest thing |
| `log.md` | `devlog.md` (when `queue-driven-workflow` is adopted) and the committed `sessions/` transcripts |
| schema file | `CLAUDE.md` plus the vendored skills |
| ingest | the intake commits and moves material into `data_lake/`, but does not compile it into anything |
| query, filed back | research answers go into `SUMMARY.md` and notes |
| lint | `cleanvibe doctor` lints the scaffold, not the content |

Most of the pattern is already present. What cleanvibe lacks is the wiki
shape itself: pages per entity or concept, an index, links between pages,
and a content lint.

## Recommendation: (b), as a skill, not a mode or an integration

- **(a) Integrate directly:** there is nothing to integrate with. It is a
  pattern, not a product or an API.
- **(b) Ship it as a scaffold variant:** yes, but as a **skill** a project
  adopts when its material calls for it (like `queue-driven-workflow`), not
  as a new mode. cleanvibe 2 has no modes by design (the agent infers the
  purpose), and the 1.x modes are frozen.
- **(c) Leave it alone:** no. A project whose `data_lake/` is a pile of
  documents (papers, notes, exports) is exactly what the pattern is for, and
  low-information projects are cleanvibe's design point.

Two parts are worth taking even without the full skill:

1. **`data_lake/` is read-only after it lands.** The agent reads it and never
   edits or deletes it; derived material goes elsewhere. That makes every
   claim checkable against an unchanged source, and it is a one-line rule.
2. **Lint as part of ingest, not as a separate periodic duty.** Case study 07
   found that rules triggered by an event (session start, a user message, a
   cron firing) hold, while standing duties named in the tick prompt are
   skipped (INTENT.md in 5 of 79 ticks). A lint pass that runs as the last
   step of each ingest is more likely to happen than a "lint the wiki
   sometimes" duty.

## Open

- **NEEDS-DECISION (Emma):** a separate `knowledge-wiki` skill, or fold the
  wiki shape (entity/concept pages, `index.md`, links, lint) into
  `research-practice`. A separate skill keeps research-practice short; folding
  it in avoids two overlapping layouts (`research/notes/` vs `wiki/`).
- **NEEDS-DECISION (Emma):** whether "`data_lake/` is read-only" goes into the
  v2 CLAUDE.md template now, independent of the skill.
- **Copyright:** the pattern assumes full sources sit in `raw/`. cleanvibe
  never commits copyrighted papers (`replication_target/` is gitignored since
  v1.15.0) and `research-practice` says "link, don't copy". A wiki skill
  must keep that: user-supplied material in `data_lake/` is the user's call;
  fetched third-party texts stay out of git.
