# replicating-grokking-generalization-beyond-overfitting-on-small-algorithmic-datasets

## Project Description

This is a **paper replication** project (scaffolded by `cleanvibe replicate`).
The goal is to reproduce the headline results of:

> **Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets**
> arXiv:2201.02177 - Alethea Power, Yuri Burda, Harri Edwards, Igor Babuschkin, Vedant Misra - 2022-01-06T18:43:37Z
> PDF: https://arxiv.org/pdf/2201.02177v1 - HTML: https://arxiv.org/html/2201.02177

It produces three compounding artifacts (see `docs/replication_framing.md`
in the cleanvibe repo for the full framing): the runnable replication, a
legibility layer (the published findings report), and `SKILL.md` — the
reusable, agent-executable replication methodology.

## Architecture and Conventions

- **`replication_target/`** holds the paper and everything pulled *about* it:
  - `replication_target/paper.pdf` — the downloaded paper (gitignored; run
    `python download_paper.py`). The paper does NOT go in `data_lake/`.
  - `replication_target/paper.md` — a Markdown extraction of the paper's
    arXiv HTML, for working from structured text. (Extract it during the
    replication; an automated extractor is a cleanvibe horizon, not built yet.)
  - the authors' code, if any, cloned as a **git submodule** in here
    (`git submodule add <repo> replication_target/<name>`).
- **`data_lake/`** — other downloaded/supplied material (datasets, notes,
  exports). Same cleanvibe convention as every project. The paper is NOT here.
- **`src/`** — your reimplementation. **`scripts/run.py`** — the entry point
  CI invokes. **`results/`** — metrics JSON (gitignored). **`FINDINGS.md`** —
  the report (reproduced vs. reported, gaps, divergences).
- **Deliverables are built by GitHub Actions, not committed.**
  `.github/workflows/pages.yml` publishes the GitHub Pages site + PDF report;
  `.github/workflows/package.yml` builds the downloadable ZIP replication
  package. You must make the repo public and enable Pages (Settings -> Pages
  -> Source: GitHub Actions) — the workflows carry TODO markers for this.
  Vision for the site shape: http://sutra.emmaleonhart.com/

## Workflow Rules

- **Commit early and often.** Every meaningful change gets a descriptive commit.
- **Plan into `queue.md` first, then execute.** The replication plan already
  lives in `queue.md` (derived from `SKILL.md`). Work it top to bottom.
- **Update `queue.md` in the same commit as the work.** Delete completed
  items; no checkmarks.
- **Keep `SKILL.md` truthful.** It is the compounding artifact. If you
  deviated from its plan, edit the plan to match what you actually did.
- **Keep this file and `README.md` current** as the replication takes shape.
