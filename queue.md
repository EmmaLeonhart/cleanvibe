# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — `cleanvibe new` on a non-empty dir should prompt, not error

Pulled from `todo.md`. Today `cleanvibe new PATH` errors+exits if the target exists and is non-empty. Make it prompt instead. Preserve the asymmetry: `new` PROMPTS (the user chose that name on purpose); only `replicate` silently auto-numbers.

1. **cli.py: prompt seam + reworked `new` handler.** Add `_ask(prompt)` (wraps `input()`, monkeypatchable), `_confirm(question)`, and `_suggest_name(path)` (append `-2`, `-3`, … until free). In the `new` branch, when `path` exists and is non-empty:
   - `--dry-run`: do NOT call input; print that it would prompt (convert-in-place vs. different name) and show the `convert_project(..., dry_run=True)` preview; return.
   - else: print the situation; `_confirm("Turn this existing directory into a git repo with cleanvibe scaffolding and start work?")` → **yes** = `convert_project(path, no_claude=...)` (reuses convert: commit1 existing, commit2 scaffold, launch); **no** = `_ask` for a name (suggest `_suggest_name(path)`, blank accepts the suggestion), guard the chosen target is itself free, then `create_project(target, ...)`.
   - Commit (delete this item, add devlog entry).

2. **tests/test_cli_new_prompt.py** (stdlib unittest, monkeypatch `cleanvibe.cli._ask`): yes-path → 2 commits like convert + CLAUDE.md present; no-path → project created at the typed/suggested name; `--dry-run` on a non-empty dir never calls `_ask` (patch it to raise) and prints `[dry-run]`. Keep `python -m unittest discover -s tests -v` fully green. Commit.

3. **Version + ship.** Bump `1.1.1` → `1.2.0` (`cleanvibe/__init__.py`, `pyproject.toml`); remove the todo.md item (done in step 1's plan commit); drain this queue section + append a `devlog.md` entry; `git push origin master` (rebase first if it moved; no release — a later job handles releases). Commit.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.1.0`.
