# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See `CLAUDE.md` § "Workflow Rules".

---

## Active — `replicate` arXiv hardening (user report: lots of errors on `replicate https://arxiv.org/abs/2605.20919`)

Work top to bottom. Delete each item in the same commit that completes it and append a dated entry to `devlog.md`.

1. **Fix the constant arXiv 429s, and prefer HTML over PDF.** `fetch_paper` does a single `urlopen` with no retry — arXiv rate-limits intermittently and the user gets raw tracebacks. Add retry-with-backoff that honours the `Retry-After` header (429/503) and retries transient `URLError`s, switch the API base to `https`, and surface a clear message if it still fails. Mirror the same backoff into the generated `download_paper.py`, and make that script fetch the arXiv **HTML** (`arxiv.org/html/<id>` → `replication_target/paper.html`) as the primary artifact since it reads far better than the PDF; keep the PDF as a fallback. Add a network-free retry unit test (mock `urlopen`).

2. **Add a "follow the authors' replication recipe first" step to the replicate queues/SKILL, working from HTML.** Many recent papers ship a reproduction script/skill (`REPRODUCE.md`, `reproduce.*`/`replicate.*`, a Makefile target, Dockerfile/`run.sh`, a `SKILL.md`/`AGENTS.md`/`.claude/` agent recipe, a "Reproducing the results" README section). Add an early, prominent step in both the arXiv (`_REPLICATION_QUEUE_TMPL`, `_REPLICATION_SKILL_TMPL`) and manual (`replication_manual_queue_md`, `replication_manual_skill_md`) templates: before reimplementing anything, look for such a recipe and follow it; only reimplement independently if there is none or it fails. Make the templates prefer working from the HTML→Markdown extraction over the PDF.

3. **Default replication target + gitignored live-scratch dir.** Lock arXiv:2605.20919 ("Sutra", the user's paper) as the default paper for smoke-testing `cleanvibe replicate`; document it in this repo's `CLAUDE.md`. Create a gitignored scratch directory for live replicate runs and add it to `.gitignore`.

4. **Live smoke test.** Run `cleanvibe replicate https://arxiv.org/abs/2605.20919 --no-claude` into the scratch dir and confirm a clean scaffold (paper.json with version, download_paper.py, recipe-first queue). Spot-check the DOI and versioned forms route to arXiv mode.

5. **Finalize.** Run the full unittest suite; bump the version; update `README.md` (replicate URL forms incl. DOI/version, 429 resilience, HTML preference) and `devlog.md`. Leave `## Active` empty.

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `1.3.0`.
