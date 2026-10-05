# cleanvibe — Long-Horizon Backlog

**This file is the long-term horizon of the project, not the current session.** `todo.md` holds multi-session goals, architectural ambitions, future capabilities — things we want to get to *eventually*. Items here are *abstract*: they describe a destination, not a step. Concrete, executable steps live in `queue.md`.

**Flow:**

```
todo.md  (abstract horizons)
   ↓  pick an item, decompose it
queue.md  (concrete executable steps)
   ↓  mirror into task tool, execute
git log  (done)
```

See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`) for how `todo.md`, `queue.md`, and the task tool stay in sync.

---

## Backlog

- **An LLM Wiki skill (Karpathy's pattern) for projects whose `data_lake/` is a pile of documents.** Design note: `docs/llm-wiki.md`. Shape: `data_lake/` as the read-only raw layer; entity/concept pages with an `index.md` and a parseable `log.md`; ingest / query (file answers back) / lint, with lint run as the last step of each ingest. Adopted on demand like `queue-driven-workflow`, not a mode. NEEDS-DECISION (Emma): a separate skill or folded into `research-practice`, and whether "`data_lake/` is read-only" goes into the v2 CLAUDE.md now.

- **Make the bootstrap queue customizable.** Right now `queue_md()` ships one fixed bootstrap sequence. Eventually projects with different shapes (library vs. service vs. data pipeline vs. wiki bot) probably want different opening sequences. Explore whether this should be a `--profile` flag on `cleanvibe new`, a set of swappable template modules, or something else.

- **Add a feedback loop from real first-sessions back into the template.** As more projects are bootstrapped, the bootstrap queue should evolve based on what consistently goes well or poorly in step 1–7. Figure out a lightweight way to capture that (a "what bit you?" prompt at session end? a curated `BOOTSTRAP_LEARNINGS.md` in this repo?) without making the tool itself heavyweight.

- **Decide how `helping-with-arxiv/` relates to `cleanvibe/arxiv.py`.** Since 2026-10-03 the arXiv submission-prep repo (Quatrix paper: LaTeX rebuilt from the Zenodo PDF, submission package) lives in this repo as a subtree at `helping-with-arxiv/`, with its history. `arxiv.py` reads arXiv for `replicate`; this goes the other way, preparing a submission. Open: whether submission prep becomes a cleanvibe feature (a mode or skill), stays a worked example under `docs/`, or stays where it is. Its nested `.claude/skills/` are v1.17-era copies.

### Replication infrastructure (merged-in from `replication_skill`)

The horizons below are what is still open of the "replication infrastructure" vision in `docs/replication_framing.md`: every replication should produce three compounding artifacts (the runnable replication, a findings page, a reusable agent SKILL.md). What already shipped, and when, is in `devlog.md`: the themed Pages findings site + PDF report (v1.13.0), the ZIP replication package workflow, early private `gh repo create` (v1.5.0, private since v1.18.0), source-first download (v1.5.0), the paper never committed (v1.15.0), the consent gate (v1.6.1) and `cleanvibe scan` (2026-10-03).

- **Paper text for PDF-only papers.** `download_paper.py` fetches the arXiv e-print source first (v1.5.0) and falls back to the PDF. Non-arXiv HTML pages are converted to `paper.md` since 2026-10-04 (`cleanvibe/htmltext.py`). Left: PDF-only papers (arXiv PDF-only submissions have no HTML, since arXiv and ar5iv build it from the LaTeX), which need a stdlib PDF text extractor.
- **Paper-artifact extractor.** A program that finds and pulls every associated artifact for a paper — the authors' code repository (cloned as a git **submodule** under `replication_target/`), datasets, supplementary files — and lays them out so the replication agent can build against them. Today the downloader only flags candidate recipe files; the rest is the agent's job.
- **CI/CD auto-replication for low-compute papers.** If a paper's compute envelope is small (CPU-feasible / ≲ a few GPU-hours), the project's CI re-runs the replication on a schedule so the repo is living evidence and silent regressions surface.
- **Automated safety scan of cloned/recipe code before running it.** Replication runs third-party code (the authors' recipe, cloned repos, downloaded zips). v1.6.1 added a **consent gate** — the generated `queue.md`/`SKILL.md` make the agent stop and get explicit user consent before executing any such code. Since 2026-10-03 `cleanvibe scan` gives the gate a pattern-match summary (see `devlog.md`). What is left is depth: following what an install step pulls in (`setup.py` hooks, `requirements.txt` packages, a recipe's downloads), and a real review step for code that matches, beyond regexes.
- **SKILL.md corpus as the compounding artifact.** Accumulate the per-paper SKILL.md files into a browsable library/index of operationalized replication methodology — the part that compounds over time, separate from any single replication.
- **Generalization hardening.** Handle the real friction: papers with official code (fork-and-verify via submodule) vs. clean reimplementation; heterogeneous dependency/compute situations; papers that don't fit the SKILL.md plan's assumptions.
- **Replication on the cleanvibe 2 base.** `replicate` still writes its own 1.x-style scaffold (`queue.md`, `devlog.md`, a root `SKILL.md`; no INTENT.md, `sessions/`, transcript hook or vendored skills). Whether it should share the v2 base (transcripts committed, INTENT.md) or stay a bounded 1.x-shaped job is open.
