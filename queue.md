# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `git log`; longer-horizon ideas live in `todo.md`. When an item is done, delete it — no checkmarks, no status indicators.

**Why this file exists:** when a planning step produces a plan, that plan is written here BEFORE execution starts. An interrupted session can pick up from the queue rather than from chat context.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

---

## Active — Merge `replication_skill` into cleanvibe as `cleanvibe replicate`

Decisions locked: standalone replication *project* per paper; land the refined *structure* working this session (deep extractor/report/site programs → `todo.md`); absorb code into the `cleanvibe` package, keep example outputs + framing notes under `docs/`. arXiv **and alphaxiv** links; stdlib only (zero-dep); unittest tests; templates as inline `string.Template` constants. Paper lives at `replication_target/paper.pdf` (gitignored, **not** in `data_lake/`); `data_lake/` still present for other downloaded material. Default dir `replicating-<slug>` with `-2/-3` collision suffix (auto-named — user supplies no title).

1. **Add `tests/test_replicate.py`** — monkeypatched paper (no network): expected tree incl. `data_lake/.gitkeep`, `replication_target/.gitkeep`, paper NOT under data_lake; `replicating-<slug>` naming + collision suffix; dry-run writes nothing. Full `unittest discover` green. Commit.

2. **Disposition of merged tree.** Move `replication_skill/replications/` → `docs/replication-examples/`; `replication_skill/notes/replication_framing.md` → `docs/replication_framing.md`; `replication_skill/{papers.json,download_all.py}` → `docs/replication-examples/`. Delete the now-consumed remainder of `replication_skill/` (its standalone CLAUDE.md/.github/.claude/pyproject/runclaude.bat/.gitignore/src/tests). Subtree history stays in `git log`. Commit.

3. **Docs + version.** Update root `CLAUDE.md` (architecture, key decision: replicate sibling subcommand, stdlib arxiv, examples in docs/) and `README.md` (`cleanvibe replicate` usage). Bump `0.6.0` → `0.7.0` (`cleanvibe/__init__.py`, `pyproject.toml`). Full test run + `cleanvibe --version` + dry-run smoke. Commit.

---

## Pointers

- Long-horizon backlog: `todo.md` (see "Replication infrastructure").
- Vision / framing source: `docs/replication_framing.md` (after step 7).
- Narrative history: `git log`.
