# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `git log`; longer-horizon ideas live in `todo.md`. When an item is done, delete it — no checkmarks, no status indicators.

**Why this file exists:** when a planning step produces a plan, that plan is written here BEFORE execution starts. An interrupted session can pick up from the queue rather than from chat context.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

---

## Active — Merge `replication_skill` into cleanvibe as `cleanvibe replicate`

Decisions locked: standalone replication *project* per paper; land it working this session; absorb code into the `cleanvibe` package, keep example outputs + framing notes as reference under `docs/`. arXiv fetch rewritten to stdlib (zero-dep guarantee); tests ported to stdlib `unittest`; templates as inline `string.Template` constants (no package data).

1. **Add replication templates to `cleanvibe/templates.py`** as `string.Template` constants + accessor functions: replication CLAUDE.md, replication queue.md (derived from the SKILL plan), README, SKILL.md, download_paper.py, .gitignore, CI workflow, Pages workflow, paper.json. Commit.

2. **Add `cleanvibe/replicate.py`** — `replicate_project(arxiv, path, dry_run, no_claude)`: fetch paper → write standalone project (CLAUDE.md, queue.md, README.md, SKILL.md, paper.json, download_paper.py, .gitignore, data_lake/.gitkeep, paper/.gitkeep, .github/workflows/{ci,pages}.yml, runclaude.bat on Windows) → `git init` + initial commit → launch Claude. Reuse `_git_init`/`_launch_claude`/`_write`. Honor `--dry-run`/`--no-claude`. Commit.

3. **Wire the subcommand in `cleanvibe/cli.py`** — `cleanvibe replicate <arxiv> [path] [--dry-run] [--no-claude]`; default dir = paper slug; refuse non-empty existing dir like `new`. Commit.

4. **Add `tests/test_replicate.py`** — monkeypatched paper (no network): writes expected tree incl. `data_lake/.gitkeep` and `paper/.gitkeep`; dry-run writes nothing. Run `python -m unittest discover -s tests -v` — all green. Commit.

5. **Disposition of merged tree.** Move `replication_skill/replications/` → `docs/replication-examples/`; `replication_skill/notes/replication_framing.md` → `docs/replication_framing.md`; `replication_skill/{papers.json,download_all.py}` → `docs/replication-examples/`. Delete the now-consumed remainder of `replication_skill/` (its standalone CLAUDE.md/.github/.claude/pyproject/runclaude.bat/.gitignore/src/tests). Subtree history stays in `git log`. Commit.

6. **Docs + version.** Update root `CLAUDE.md` (architecture, key decision: replicate sibling subcommand, stdlib arxiv, examples in docs/) and `README.md` (`cleanvibe replicate` usage). Bump `0.6.0` → `0.7.0` (`cleanvibe/__init__.py`, `pyproject.toml`). Full test run + `cleanvibe --version` + dry-run smoke. Commit.

---

## Pointers

- Long-horizon backlog: `todo.md` (see "Replication infrastructure").
- Vision / framing source: `docs/replication_framing.md` (after step 7).
- Narrative history: `git log`.
