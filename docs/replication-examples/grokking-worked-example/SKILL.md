---
name: replicate-grokking-generalization-beyond-overfitting-on-small-algorithmic-datasets
description: Replicate the methods of "Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets" (arXiv:2201.02177) and produce a runnable artifact, a published findings report, and a downloadable replication package.
---

# Replicate: Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets

arXiv:2201.02177 - Alethea Power, Yuri Burda, Harri Edwards, Igor Babuschkin, Vedant Misra - 2022-01-06T18:43:37Z
PDF: https://arxiv.org/pdf/2201.02177v1 - HTML: https://arxiv.org/html/2201.02177

## Prerequisite

If `replication_target/paper.pdf` is missing, run `python download_paper.py`
first. Don't proceed without the paper. Prefer working from
`replication_target/paper.md` (a Markdown extraction of the arXiv HTML) when
it is present.

## Plan

1. **Acquire the paper.** PDF -> `replication_target/paper.pdf` (gitignored).
   Extract the arXiv HTML to `replication_target/paper.md` for structured text.

2. **Read the paper.** Record in `notes/claims.md`: headline claim(s);
   datasets (version/hash, location); models/methods in re-implementable
   detail; evaluation metrics and the exact reported numbers; compute
   envelope (used to decide if CI can auto-run this).

3. **Find the authors' code.** arXiv "Code" link, paperswithcode, GitHub
   (title + first-author). If official code exists, add it as a **git
   submodule** under `replication_target/` and record in `notes/sources.md`
   whether you fork-and-verify or independently reimplement.

4. **Set up the environment.** `environment.yml` / `requirements.txt` pinned
   to working versions; minimum dependency set for the headline claim.

5. **Reimplement the method.** Code under `src/`. Scope to the headline
   claim, not every ablation.

6. **Run the replication.** `scripts/run.py` so CI can invoke it. Capture
   metrics as JSON into `results/`.

7. **Write the findings.** `FINDINGS.md`: reproduced vs. reported numbers
   (table); gaps you filled; where it diverged and why.

8. **Publish.** GitHub Pages deploys the findings + a transportable PDF
   report (`.github/workflows/pages.yml`); a ZIP replication package is built
   and offered for download (`.github/workflows/package.yml`). The repo must
   be public with Pages enabled.

## Budget guardrails

- If the paper's reported compute is more than ~4 GPU-hours on a single
  consumer GPU, mark this replication **not CI-runnable** in `paper.json` and
  document the reduced-scale variant instead.
- Prefer deterministic seeds and logged hashes so reruns are comparable.

## Definition of done

- `FINDINGS.md` exists and reports at least one headline number from the
  paper, with the reproduced value next to it.
- `scripts/run.py` runs end-to-end from a clean clone (or documents the data
  step that can't be automated).
- The GitHub Pages site and the ZIP package build green in Actions.
- This file still reflects how you actually did it — if you deviated, edit
  the plan above.
