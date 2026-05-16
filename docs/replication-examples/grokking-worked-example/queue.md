# replicating-grokking-generalization-beyond-overfitting-on-small-algorithmic-datasets - Work Queue

**This file is a queue of concrete, executable steps, not a state snapshot.**
Finished work lives in `git log`; longer-horizon items live in `todo.md`.
When an item is done, delete it — no checkmarks, no status indicators.

**Why this file exists:** the replication plan is written here BEFORE
execution so an interrupted session resumes from the queue, not from chat.
The canonical methodology is `SKILL.md`; this queue is its executable form.

---

## Active — Replicate "Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets" (arXiv:2201.02177)

Work top to bottom. Delete each item in the same commit that completes it.

1. **Download the paper.** Run `python download_paper.py` — it writes
   `replication_target/paper.pdf` (gitignored). Do not proceed if it is empty.
   Also save a Markdown extraction of the arXiv HTML (https://arxiv.org/html/2201.02177) to
   `replication_target/paper.md` so later steps work from structured text.

2. **Read the paper; record `notes/claims.md`:** headline claim(s); datasets
   (version/hash, where they live); models/methods in enough detail to
   re-implement; evaluation metrics and the exact reported numbers; compute
   envelope (GPU type, hours, memory) — used to decide if CI can auto-run it.
   Commit.

3. **Find the authors' code.** Check the arXiv "Code" link, paperswithcode,
   GitHub (title + first-author). If official code exists, add it as a git
   submodule under `replication_target/` and record the decision in
   `notes/sources.md` (fork-and-verify vs. independent reimplementation).
   Commit.

4. **Set up the environment.** `requirements.txt` / `environment.yml` pinned
   to versions that work; minimum set needed for the headline claim. Commit.

5. **Reimplement the method** under `src/` — scope to the headline claim,
   not every ablation. Commit as you go.

6. **Run the replication.** Script it as `scripts/run.py` so CI can invoke
   it; capture metrics as JSON into `results/`. Commit.

7. **Write `FINDINGS.md`:** reproduced vs. reported numbers (table); gaps you
   had to fill (hyperparameters, preprocessing, omitted architecture details);
   where and why it diverged. Commit.

8. **Publish the deliverables.** Confirm `.github/workflows/pages.yml` builds
   the GitHub Pages site + PDF report and `.github/workflows/package.yml`
   builds the ZIP replication package. Make the repo public; enable Pages
   (Settings -> Pages -> Source: GitHub Actions). Update `SKILL.md` so it
   reflects how you actually did this. Commit.

9. **Stop / hand back** when `FINDINGS.md` reports at least one headline
   number with its reproduced value, `scripts/run.py` runs end-to-end from a
   clean clone (or documents the un-automatable data step), and the Pages
   deployment is green.

---

## Pointers

- Methodology / definition of done: `SKILL.md`.
- Long-horizon items: `todo.md`.
- Narrative history: `git log`.
