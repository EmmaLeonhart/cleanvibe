# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — `replicate` arXiv hardening (user report: lots of errors on `replicate https://arxiv.org/abs/2605.20919`)

Work top to bottom. Delete each item in the same commit that completes it and append a dated entry to `devlog.md`.

1. **Live smoke test.** Run `cleanvibe replicate https://arxiv.org/abs/2605.20919 --no-claude` into the scratch dir and confirm a clean scaffold (paper.json with version, download_paper.py, recipe-first queue). Spot-check the DOI and versioned forms route to arXiv mode.

2. **Finalize.** Run the full unittest suite; bump the version; update `README.md` (replicate URL forms incl. DOI/version, 429 resilience, HTML preference) and `devlog.md`. Leave `## Active` empty.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.3.0`.
