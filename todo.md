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

See `CLAUDE.md` § "Workflow Rules" for how `todo.md`, `queue.md`, and the task tool stay in sync.

---

## Backlog

- **Investigate the Carpathes / L-Carpathes agentic wiki idea and see whether it fits inside cleanvibe.** Look at what the Carpathes (a.k.a. L-Carpathes) agentic wiki concept is actually trying to do — how it models pages, agents, and edits — and decide whether cleanvibe should: (a) integrate with it directly, (b) ship a scaffold variant for projects that want this pattern, or (c) leave it alone. Output: a short design note in the repo with the recommendation and, if it's a fit, a follow-up `todo.md` entry describing the integration shape.

- **Make the bootstrap queue customizable.** Right now `queue_md()` ships one fixed bootstrap sequence. Eventually projects with different shapes (library vs. service vs. data pipeline vs. wiki bot) probably want different opening sequences. Explore whether this should be a `--profile` flag on `cleanvibe new`, a set of swappable template modules, or something else.

- **Extend `cleanvibe convert` to detect and adopt existing planning artifacts.** If a target repo already has a `TODO`, `BACKLOG.md`, `ROADMAP.md`, or similar, `convert` should recognize them and either rename/merge into `todo.md` or surface a prompt rather than silently injecting an empty one alongside.

- **`cleanvibe new` on an existing/non-empty directory should prompt, not error.** Today `cleanvibe new PATH` exits with an error if the target exists and is non-empty. Instead: ask the user **yes/no** — "turn this existing directory into a git repo with cleanvibe scaffolding and start work?". If **yes**, behave like `cleanvibe convert`: commit 1 = the existing files as-is, commit 2 = the injected cleanvibe scaffold, then launch Claude (Claude then decides data_lake triage etc. per the bootstrap queue, or asks the user). If **no**, ask whether to create it under a *different* name, **suggest** one, and let the user type their own. Note the deliberate asymmetry: the `replicate` paper flow **auto-numbers** collisions (`replicating-<slug>-2`) silently because the user supplies no name; `cleanvibe new` does **not** auto-number — it prompts, because the user chose that name on purpose and a silent rename would be surprising.

- **Ship a `cleanvibe doctor` command.** A subcommand that audits a cleanvibe project for drift: queue.md items still present after commits that should have deleted them, todo.md items that look like they belong in queue.md (or vice versa), missing CI workflow, stale CLAUDE.md sections. Read-only by default, with `--fix` for the safe ones.

- **Add a feedback loop from real first-sessions back into the template.** As more projects are bootstrapped, the bootstrap queue should evolve based on what consistently goes well or poorly in step 1–7. Figure out a lightweight way to capture that (a "what bit you?" prompt at session end? a curated `BOOTSTRAP_LEARNINGS.md` in this repo?) without making the tool itself heavyweight.

### Replication infrastructure (merged-in from `replication_skill`)

The `replicate` subcommand absorbs the now-sunset `replication_skill` project. A working standalone `cleanvibe replicate <arxiv-url>` is the near-term goal (decomposed in `queue.md`). The horizons below are the larger "replication infrastructure" vision from `docs/replication_framing.md` — every replication should produce three compounding artifacts: the runnable replication, a legibility layer (findings page), and a reusable agent SKILL.md.

- **arXiv/alphaxiv HTML → Markdown extractor.** A program that pulls the paper's HTML (arXiv ar5iv/HTML or alphaxiv) and transforms it into a clean Markdown file written into `replication_target/`, so the agent works from structured text rather than raw PDF. PDF text extraction as a fallback when no HTML exists.
- **Paper-artifact extractor.** A program that finds and pulls every associated artifact for a paper — the authors' code repository (cloned as a git **submodule** under `replication_target/`), datasets, supplementary files — and lays them out so the replication agent can build against them.
- **GitHub Pages "living replication report" site.** Each replication repo builds, via GitHub Actions, a Pages site in the spirit of http://sutra.emmaleonhart.com/ : findings, reproduced-vs-reported tables, and a generated transportable **PDF report**. The user configures repo-public + Pages-enable; the workflow does the rest.
- **Downloadable replication package (ZIP).** A GitHub Actions job that assembles a ZIP — the replication code plus the necessary code pulled from the paper's repo — and publishes it on the Pages site / as a release asset, so anyone can download and re-run. Built in Actions, never a committed directory.
- **CI/CD auto-replication for low-compute papers.** If a paper's compute envelope is small (CPU-feasible / ≲ a few GPU-hours), the project's CI re-runs the replication on a schedule so the repo is living evidence and silent regressions surface.
- **SKILL.md corpus as the compounding artifact.** Accumulate the per-paper SKILL.md files into a browsable library/index of operationalized replication methodology — the part that compounds over time, separate from any single replication.
- **Remote repo + Pages provisioning.** Optionally `gh repo create` a public repo and enable Pages automatically as part of `cleanvibe replicate`, so the artifact is public from minute one.
- **Generalization hardening.** Handle the real friction: papers with official code (fork-and-verify via submodule) vs. clean reimplementation; heterogeneous dependency/compute situations; papers that don't fit the SKILL.md plan's assumptions.
- **Batch replication from a corpus.** Port the `docs/replication-examples/download_all.py` + `papers.json` idea into a `cleanvibe replicate --batch <papers.json>` flow for standing up many replications at once.
- **Unify the two scaffolds.** Factor a single shared base-scaffold core that both `cleanvibe new` and `cleanvibe replicate` build on, so conventions (queue/todo/data_lake/CLAUDE) stay in lockstep across project types.

This session lands the *refined structure* only: `replicating-<slug>` auto-naming (with `-2/-3` collision suffix), arXiv **and alphaxiv** link parsing, the paper at `replication_target/paper.pdf` (gitignored, **not** in `data_lake/`), `data_lake/` still present for other downloaded material, and scaffolded GitHub Actions workflows (Pages + ZIP-package) with user-configured TODOs. The extractor/report/site programs above are the deep follow-on work.
