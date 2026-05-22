# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — non-arXiv URL replication source (v1.6.2, patch)

User ask: `cleanvibe replicate` should also download a web page / PDF for research that's **not** on arXiv/clawRxiv. Work top to bottom; delete each item in the same commit that completes it and append to `devlog.md`.

1. **Finalize.** Full suite; bump `1.6.1` → `1.6.2`; update `README.md` (the non-arXiv URL form) + `devlog.md`; merge to main, push, tag + release.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.6.1`.
