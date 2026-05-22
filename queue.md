# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — non-arXiv URL replication source (v1.6.2, patch)

User ask: `cleanvibe replicate` should also download a web page / PDF for research that's **not** on arXiv/clawRxiv. Work top to bottom; delete each item in the same commit that completes it and append to `devlog.md`.

1. **Fix the stale editable install.** `pip install -e .` so code run outside the repo uses this repo, not the old site-packages copy.

2. **Add a non-arXiv URL download mode to `replicate`.** New dispatch branch (after clawRxiv + arXiv, before folder mode): if the arg isn't a clawRxiv/arXiv ref but *looks like an http(s) URL*, scaffold a project that **downloads the URL** into `replication_target/source/` (sniff PDF vs HTML → `paper.pdf`/`paper.html`) using the existing 429-aware `_read_url`, record provenance in `source.json`, and commit it (commit 2, like arXiv). Reuse the manual templates **parametrized with the source URL** so the wording is accurate (source already present; no "drop it in / STOP and ask"). Keep arXiv/clawRxiv/folder modes intact and the manual (no-URL) template output byte-stable so existing tests pass.

3. **Tests.** URL routing in the CLI (mock the download), the manual templates' URL-vs-manual wording branch, dry-run, and slug-from-URL. Network-free.

4. **Finalize.** Full suite; bump `1.6.1` → `1.6.2`; update `README.md` (the non-arXiv URL form) + `devlog.md`; merge to main, push, tag + release.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.6.1`.
