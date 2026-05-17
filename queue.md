# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — `cleanvibe new` on a non-empty dir should prompt, not error

Pulled from `todo.md`. Today `cleanvibe new PATH` errors+exits if the target exists and is non-empty. Make it prompt instead. Preserve the asymmetry: `new` PROMPTS (the user chose that name on purpose); only `replicate` silently auto-numbers.

1. **Version + ship.** Bump `1.1.1` → `1.2.0` (`cleanvibe/__init__.py`, `pyproject.toml`); drain this queue section + append a `devlog.md` entry; `git push origin master` (rebase first if it moved; no release — a later job handles releases). Commit.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.1.0`.
