---
name: replicate-attention-is-all-you-need
description: Replicate the methods of "Attention Is All You Need" (arXiv:1706.03762) and produce a runnable artifact plus a findings report.
---

# Replicate: Attention Is All You Need

arXiv:1706.03762 · Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin · 2017-06-12T17:57:34Z
PDF: https://arxiv.org/pdf/1706.03762v7

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
