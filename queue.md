# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — `replicate`: fix arXiv links + add folder-drop mode (→ release)

Work top to bottom. Delete each item in the same commit that completes it and append a dated `devlog.md` entry.

1. **Add a folder-drop replication mode.** `cleanvibe replicate <arg>` should dual-dispatch: if `<arg>` parses as an arxiv ref → existing arXiv flow; otherwise treat `<arg>` as a folder name and scaffold a *manual* replication project where the user drops the paper PDF(s) + supporting material into `replication_target/` / `data_lake/` themselves (no `download_paper.py`, no `paper.json`, no network). Manual templates in `templates.py` (CLAUDE/queue/SKILL/README) whose opening instructions say up front that the paper and materials are being placed in by hand; `replicate_manual_project()` in `replicate.py`; CLI dispatch in `cli.py`; tests in `tests/test_replicate.py`.

2. **Docs + release.** Update `README.md` (replicate section: folder mode + permissive links), root `CLAUDE.md` (architecture decision for the dual-mode `replicate`), `todo.md` (note the link-robustness + manual-mode work landed). Bump version `1.2.2` → `1.3.0` (`cleanvibe/__init__.py`, `pyproject.toml`). Run the full test suite green. Commit, push, tag `v1.3.0`, cut the GitHub release.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.2.2`.
