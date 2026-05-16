# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `git log`; longer-horizon ideas live in `todo.md` (create when needed). When an item is done, delete it — no checkmarks, no status indicators.

**Why this file exists:** when a planning step produces a plan, that plan is written here BEFORE execution starts. An interrupted session can pick up from the queue rather than from chat context.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

---

## Active

1. **Merge `replication_skill` repo in via git subtree, preserving history.**
   - `git subtree add --prefix=replication_skill "C:/Users/Immanuelle/Documents/Github/replication_skill" master` (no `--squash` — keep full history).
   - Verify files landed under `replication_skill/` and the imported commits are present in `git log`.

2. **Bootstrap creates `data_lake/.gitkeep`.**
   - Edit `cleanvibe/templates.py` queue_md step 1 so creating `data_lake/` also adds `data_lake/.gitkeep` (keeps the dir tracked when empty).
   - Add a test assertion in `tests/test_scaffold.py` that the bootstrap queue mentions `.gitkeep`.
   - Bump version 0.5.0 → 0.6.0 (`cleanvibe/__init__.py`, `pyproject.toml`).
   - Note the data_lake/.gitkeep decision in `CLAUDE.md` Key Decisions.
   - Run `python -m unittest discover -s tests -v`.

---

## Pointers

- Reference repos using the same pattern: `../Sutra/`, `../SutraDB/`, `../shintowiki-scripts/`, `../life-planning/`.
- Narrative history: `git log`.
