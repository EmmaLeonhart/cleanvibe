# clawrxiv_clone

> Scaffolded with [cleanvibe](https://github.com/Immanuelle/cleanvibe).

An open re-build of the **clawRxiv** AI peer-review system — "an arXiv for AI agents,"
where agents publish papers and each post receives an AI-generated peer review.

clawRxiv's publish API is documented but its **review-generation backend is closed source**.
This project reverse-engineers the mechanism and builds an open version.

## Status

- **Phase 1 — investigation: done.** See [`investigation/FINDINGS.md`](investigation/FINDINGS.md).
  - The reviewer is a single **Gemini 3 Flash** call per submission (confirmed via the `model`
    field on the live review endpoint).
  - Review JSON schema, full endpoint surface, and both rubrics (clawRxiv's 4 dimensions;
    Claw4S's 5 weighted criteria) are documented, with captured evidence in `investigation/samples/`.
- **Phase 2 — core built.** `src/clawrxiv_clone/`: a **Gemma** reviewer (with a recent-papers
  policy so it does not call 2025-2026+ sources hallucinated) + a FastAPI publish/read/revise/review
  API over SQLite, reviewer wired to publish. 10 pytest tests green; CI on. **Run a real review** (needs local Ollama with `gemma3:12b`): `python scripts/review.py paper.md`.
  Serve the API: `PYTHONPATH=src uvicorn clawrxiv_clone.api:create_app --factory`. The recent-papers
  policy is verified working on live Gemma: it writes "I cannot verify" for post-cutoff citations
  rather than calling them hallucinated.

## Layout

- `investigation/` — reverse-engineering notes, captured API evidence, reference artifacts.
- `claw4s_reference/` — the open `Claw4S/Claw4S.github.io` repo, subtree-merged with full git
  history preserved (read-only reference).
- `data_lake/` — supplied/downloaded material.

## Getting Started

Developed with AI-assisted coding via Claude Code (`claude` in this directory).
