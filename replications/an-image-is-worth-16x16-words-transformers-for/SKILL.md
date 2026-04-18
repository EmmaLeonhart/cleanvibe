---
name: replicate-an-image-is-worth-16x16-words-transformers-for
description: Replicate the methods of "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale" (arXiv:2010.11929) and produce a runnable artifact plus a findings report.
---

# Replicate: An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale

arXiv:2010.11929 · Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, Neil Houlsby · 2020-10-22T17:55:59Z
PDF: https://arxiv.org/pdf/2010.11929v2

## Prerequisite

If `paper/` is empty, run `python download_paper.py` first. Don't proceed without the paper.

## Plan

1. **Read the paper.** Record, in `notes/claims.md`:
   - The headline claim(s) being made.
   - Datasets used (with version/hash if available) and where they live.
   - Models / methods introduced, in enough detail to re-implement.
   - Evaluation metrics and the specific numbers the paper reports.
   - Compute envelope (GPU type, hours, memory) — used later to decide if CI can auto-run this.

2. **Find the authors' code.** Check arXiv "Code" link, paperswithcode.com, GitHub search for the title and first-author name. If official code exists, link it in `notes/sources.md` and decide whether to fork-and-verify or independently reimplement.

3. **Set up the environment.** Create `environment.yml` or `requirements.txt` pinned to versions that work. Prefer the minimum dependency set needed for the headline claim.

4. **Reimplement the method.** Put code under `src/`. Keep the scope to what is needed to reproduce the headline claim — not every ablation.

5. **Run the replication.** Script it under `scripts/run.py` so CI can invoke it. Capture metrics as JSON into `results/`.

6. **Write the findings.** In `FINDINGS.md`:
   - Reproduced numbers vs reported numbers (table).
   - Gaps you had to fill (hyperparameters, preprocessing, architecture details the paper omitted).
   - Where it diverged, and why you think it diverged.

7. **Publish.** Ensure the repo has a GitHub Pages deployment of `FINDINGS.md` and links to the runnable artifact.

## Budget guardrails

- If the paper's reported compute is more than ~4 GPU-hours on a single consumer GPU, mark this replication as **not CI-runnable** in `paper.json` and document the reduced-scale variant instead.
- Prefer deterministic seeds and logged hashes so reruns are comparable.

## Definition of done

- `FINDINGS.md` exists and reports at least one headline number from the paper, with the reproduced value next to it.
- `scripts/run.py` runs end-to-end from a clean clone (or documents the data step that can't be automated).
- The skill in this file still reflects how you actually did it — if you deviated, edit the plan above.
