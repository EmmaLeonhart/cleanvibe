# Replicating: Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets

**arXiv:** [2201.02177](https://arxiv.org/pdf/2201.02177v1) - **HTML:** [2201.02177](https://arxiv.org/html/2201.02177)
**Authors:** Alethea Power, Yuri Burda, Harri Edwards, Igor Babuschkin, Vedant Misra
**Published:** 2022-01-06T18:43:37Z

## Abstract

In this paper we propose to study generalization of neural networks on small algorithmically generated datasets. In this setting, questions about data efficiency, memorization, generalization, and speed of learning can be studied in great detail. In some situations we show that neural networks learn through a process of "grokking" a pattern in the data, improving generalization performance from random chance level to perfect generalization, and that this improvement in generalization can happen well past the point of overfitting. We also study generalization as a function of dataset size and find that smaller datasets require increasing amounts of optimization for generalization. We argue that these datasets provide a fertile ground for studying a poorly understood aspect of deep learning: generalization of overparametrized neural networks beyond memorization of the finite training dataset.

## Replication status

Not started. The agent-executable plan is in [`SKILL.md`](./SKILL.md);
the concrete step queue is in [`queue.md`](./queue.md).

## What this repo produces

Three compounding artifacts:

1. **The replication** — runnable code under `src/` + `scripts/run.py`.
2. **The legibility layer** — `FINDINGS.md`, published as a GitHub Pages
   site with a transportable PDF report (built by GitHub Actions).
3. **`SKILL.md`** — a reusable, agent-executable replication methodology.

## Layout

- `replication_target/` — the paper and everything pulled about it:
  - `paper.pdf` — downloaded PDF (gitignored; `python download_paper.py`).
  - `paper.md` — Markdown extraction of the arXiv HTML (for structured text).
  - the authors' code, if any, as a git **submodule**.
- `data_lake/` — other downloaded/supplied material (NOT the paper).
- `src/` — your reimplementation. `scripts/run.py` — CI entry point.
- `results/` — metrics JSON (gitignored). `FINDINGS.md` — the report.
- `paper.json` — frozen metadata pulled from the arXiv API.
- `.github/workflows/` — `pages.yml` (site + PDF), `package.yml` (ZIP).

## Deliverables (GitHub Actions)

To publish, **make this repo public** and set **Settings -> Pages -> Source:
GitHub Actions**. Then `pages.yml` deploys the findings site + PDF report and
`package.yml` builds a downloadable ZIP replication package. Site shape
inspiration: http://sutra.emmaleonhart.com/
