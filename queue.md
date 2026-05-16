# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `git log`; longer-horizon ideas live in `todo.md`. When an item is done, delete it — no checkmarks, no status indicators.

**Why this file exists:** when a planning step produces a plan, that plan is written here BEFORE execution starts. An interrupted session can pick up from the queue rather than from chat context.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

---

## Active — Rework `clone` for codebase onboarding + cut v1.0.0

Decisions locked: `cleanvibe clone` is for onboarding an EXISTING repo, not bootstrapping a new one. It clones, creates a dedicated `cleanvibe-onboarding` branch, commits the injected onboarding files there (default branch untouched), and drives a *smaller, different* queue: NO `data_lake/` (nothing dropped in — it's a real codebase); the work is to read & document the repo, update existing docs if present, adapt `CLAUDE.md` to the repo's real dev practices, add tests/CI if sparse, and synthesize any existing `todo.md`/`queue.md` then work the repo's own `todo.md`. Re-running `clone` prepends a fresh onboarding block to the top of CLAUDE.md/queue.md if they exist (non-destructive). This is the maturity release: **v1.0.0**.

1. **Add `tests/test_clone.py`** — build a local temp git repo as the clone source. Cover: `cleanvibe-onboarding` branch created & checked out, clone CLAUDE/queue content present (no data_lake, no README injected), pre-existing repo files preserved, a commit exists on the branch, and a second `clone` run prepends a fresh block above existing CLAUDE.md/queue.md content. Full `unittest discover` green. Commit.

2. **Build the cleanvibe GitHub Pages site.** A static `site/` (vanilla HTML/CSS/JS, no build step) explaining what cleanvibe is and why to use it, with tabbed sections: **What is cleanvibe** · **New project** · **Clone (onboarding)** · **Replicate a paper**. Add `.github/workflows/pages.yml` (`actions/upload-pages-artifact` from `site/` + `actions/deploy-pages`; Pages Source is already set to GitHub Actions on the repo). Commit.

3. **Docs + v1.0.0 release.** README: rewrite the clone section for the new behavior, add a "Stability" section (per the `todo.md` 0.x→1.0 item), and link the Pages site. Root `CLAUDE.md`: architecture + a key decision for the onboarding-clone model + the site. Bump `0.7.0` → `1.0.0` (`cleanvibe/__init__.py`, `pyproject.toml`). Remove the now-done items from `todo.md`. Full test run + `cleanvibe --version` + dry-run smokes. Commit, push, annotated tag `v1.0.0`, `gh release create v1.0.0` with an informative summary of everything since v0.5.0.

4. **Worked example: a real end-to-end replication.** Target chosen: **"Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets"**, Power et al. 2022, **arXiv:2201.02177** (tiny transformer on modular arithmetic; single-GPU/CPU-feasible; widely re-implemented; visually compelling). Run the new `cleanvibe replicate` pipeline on it and carry the replication through, committing it INTO this repo (tracked under `docs/replication-examples/`; the paper PDF itself stays gitignored) so the replication Pages site has a genuine worked example. **Environment note:** the local Python sandbox has no outbound network (arXiv `urllib` fetch fails), though Bash git/gh and WebSearch/WebFetch do reach the network — so the actual scaffold+download+train run is delegated to a networked run/scheduled job; this item tracks that.

---

## Pointers

- Long-horizon backlog: `todo.md`.
- Vision / framing source: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`.
