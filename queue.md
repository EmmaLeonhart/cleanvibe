# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — `replicate`: fix arXiv links + add folder-drop mode (→ release)

Work top to bottom. Delete each item in the same commit that completes it and append a dated `devlog.md` entry.

1. **Docs + release.** Update `README.md` (replicate section: folder mode + permissive links), root `CLAUDE.md` (architecture decision for the dual-mode `replicate`), `todo.md` (note the link-robustness + manual-mode work landed). Bump version `1.2.2` → `1.3.0` (`cleanvibe/__init__.py`, `pyproject.toml`). Run the full test suite green. Commit, push, tag `v1.3.0`, cut the GitHub release.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.2.2`.
