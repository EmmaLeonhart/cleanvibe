# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `git log` and `devlog.md`; longer-horizon ideas live in `todo.md`. When an item is done, **delete it here and append a dated entry to `devlog.md`** — never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — Add a `devlog.md` ("done" lives here, not as ticked boxes), then release v1.1.0

**Why:** agents sometimes *check off* `queue.md` items in place instead of deleting them, so the queue rots. Fix: `devlog.md` is the canonical home for completed work. Finishing a queue item = delete from `queue.md` + append a dated entry to `devlog.md` + commit + push. Ship across all settings (new / clone / convert / replicate) + release v1.1.0.

**This is a fully resumable spec — a fresh session can complete it with no chat context. Progress markers below say what is already DONE vs TODO.**

### 1. devlog template + wire into all scaffold paths
- [DONE] `cleanvibe/templates.py` `claude_md()`: replaced the "update queue.md" rule with the strong devlog rule (delete from queue + append dated entry to `devlog.md` + commit/push; never tick boxes in place).
- [TODO] Add `def devlog_md(project_name: str) -> str:` to `cleanvibe/templates.py` (near `todo_md`). Content: H1 `# {project_name} — Devlog`; a paragraph explaining the workflow (finishing a queue item → delete from queue.md, append dated entry here, commit+push; queue.md holds only not-yet-done work; never tick boxes in place); "Newest entries at the bottom."; a `---`; then one entry `## {YYYY-MM-DD} — Project scaffolded` / body noting it was scaffolded with cleanvibe v{__version__from cleanvibe import __version__} and that for an existing repo onboarded via clone/convert the first task is to backfill this devlog from `git log`. Use `from datetime import datetime` (already imported) and `from . import __version__`? NOTE templates.py imports `from .arxiv import ArxivPaper`; arxiv.py does `from . import __version__`, so do `from cleanvibe import __version__` lazily inside the function OR add `from . import __version__` at top of templates.py (check no circular import — fine, scaffold.py already does it).
- [TODO] `cleanvibe/templates.py` `queue_md()`: in the preamble paragraph + the bootstrap "When an item is done, delete it" line, add: also append a dated entry to `devlog.md` and commit+push; never tick boxes.
- [TODO] `cleanvibe/templates.py` `clone_claude_md()` and `clone_queue_md()`: add the devlog rule; clone is an EXISTING repo so the onboarding queue's step 1 (or a new early step) must say **backfill `devlog.md` from `git log`/existing history** before normal onboarding.
- [TODO] `cleanvibe/templates.py` `replication_claude_md()` (the `_REPLICATION_CLAUDE_TMPL` Template) and `replication_queue_md()` (`_REPLICATION_QUEUE_TMPL`): add the devlog rule (Template uses `$`-substitution — keep literal text, no stray `$`).
- [TODO] `cleanvibe/scaffold.py`:
  - `create_project()`: add `_write(path / "devlog.md", templates.devlog_md(project_name))` (and a `[dry-run] Would write: .../devlog.md` line).
  - `_inject_scaffold()` (used by `convert`): inject `devlog.md` if missing (mirror the README/.gitignore injection blocks; print "Injected devlog.md (was missing)").
  - `clone_project()`: after the CLAUDE.md/queue.md prepend-or-write, write `devlog.md` if missing (clone-flavoured; the clone queue tells the agent to backfill it). Add a `[dry-run]` line.
  - `replicate.py` `replicate_project()`: `_write(target / "devlog.md", templates.devlog_md(...))` (use the paper slug / project name) + add to the dry-run file list.
- [TODO] Tests: extend `tests/test_scaffold.py` (new + convert paths assert `devlog.md` exists), `tests/test_replicate.py` (devlog.md in tree), `tests/test_clone.py` (devlog.md present). Add a templates assertion that the bootstrap queue/claude text contains "devlog". Keep `python -m unittest discover -s tests -v` fully green.
- [TODO] Commit: delete this whole "### 1" block, append a dated `devlog.md` entry, commit, push.

### 2. Dogfood the devlog in this repo
- [TODO] Create root `devlog.md` (this IS an existing repo — the backfill case). Backfill chronological milestones from `git log` (subtree merge of replication_skill; v0.6 data_lake/.gitkeep; v0.7 replicate + arxiv/alphaxiv; clone onboarding rework; Pages site; v1.0.0; Grokking worked example; this devlog feature).
- [TODO] Update root `CLAUDE.md` (Workflow Rules: add the devlog rule; Key Decisions: add a "devlog.md — done lives here" entry) and this `queue.md` preamble (already references devlog — keep).
- [TODO] Commit (delete this block, add devlog entry, push).

### 3. v1.1.0 release
- [TODO] Bump `0?`→ set version `1.1.0` in `cleanvibe/__init__.py` and `pyproject.toml` (currently `1.0.0`).
- [TODO] Run `python -m unittest discover -s tests -v` (all green); smoke `cleanvibe --version`, `cleanvibe new smoke --dry-run --no-claude`, `cleanvibe clone <url> d --dry-run --no-claude`, `cleanvibe replicate https://arxiv.org/abs/1706.03762 --dry-run --no-claude`.
- [TODO] Commit; `git push origin master`; `git tag -a v1.1.0 -m "..."`; `git push origin v1.1.0`; `gh release create v1.1.0 --title "cleanvibe v1.1.0" --notes "<devlog.md feature: done has a home; queue stays delete-only; backfill on clone/convert>"`.
- [TODO] Final `devlog.md` entry for the release; delete this block.

---

## Pointers

- Completed work (chronological): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.0.0` (target `1.1.0`).
