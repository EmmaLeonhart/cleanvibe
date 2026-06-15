# clawrxiv_clone — Devlog

**This file is where "done" lives.** `queue.md` is delete-only: when a queue
item is finished, the item is **deleted from `queue.md`** and a dated entry
is **appended here**, in the same commit as the work, then pushed. Never
tick a box in place — a checked box left in `queue.md` is the failure mode
this file exists to prevent.

Also record releases (tag + a one-line note), notable milestones, and
anything else worth a chronological trail. Newest entries at the bottom.

This is the **same convention as the cleanvibe repo's own `devlog.md`** —
every cleanvibe-scaffolded project gets one for the same reason.

See `CLAUDE.md` § "Workflow Rules" and `queue.md`'s preamble.

---

## 2026-06-14 — Project scaffolded

Scaffolded with `cleanvibe new` (cleanvibe v1.13.1). Future entries
land here as queue items get deleted.

## 2026-06-14 — Project bootstrap + Phase 1 investigation done

Scaffolded with `cleanvibe new` and pushed to a **private** repo
(github.com/EmmaLeonhart/clawrxiv_clone). Subtree-merged `Claw4S/Claw4S.github.io` into
`claw4s_reference/` with **full git history preserved** (no --squash; 28 upstream commits).

Phase 1 (reverse-engineer clawRxiv's AI peer review) complete — `investigation/FINDINGS.md`:
- **Reviewer = a single "Gemini 3 Flash" call per submission**, confirmed via the `model` field
  on the live `GET /api/posts/:id/review` endpoint (3 independent reviews all say so). Captured
  evidence: `investigation/samples/review_{2780,2603.00283,2604.00100}.json`, plus the live
  `/docs` and `/skill.md`.
- Documented the review JSON schema (rating tier / summary / 5 pros / 5 cons / justification /
  model / createdAt), the full endpoint surface, and both rubrics (clawRxiv's 4 dimensions;
  Claw4S's 5 weighted criteria + 3-phase auto-exec/agent-review/human-meta process).
- Saved the closest open artifact, the LabClaw `peer-review` SKILL.md (by K-Dense Inc.), as a
  reusable rubric skeleton.
- Named what stays closed: the literal reviewer prompt, the tier ladder + thresholds, the
  execution sandbox, the classifier/revision-checker prompts, and the backend source.

Phase 2 (build the open clone) planned into `queue.md`; long-horizon in `todo.md`. CLAUDE.md +
README updated. Crons NOT started yet (per user: restart the work crons once it is working).

## 2026-06-14 — Build: reviewer core (Gemma) + recent-papers fix + tests + CI

Stack recorded in CLAUDE.md: Python + FastAPI + SQLite, **Gemma** reviewer behind a pluggable
`LLMClient` (default local Ollama `gemma3`; mockable), pytest + GitHub Actions.

Built the reviewer (the core piece):
- `src/clawrxiv_clone/schema.py` — `Paper`, `Review` (rating ladder enum, summary, pros, cons,
  justification, model, createdAt), matching the live clawRxiv review shape.
- `src/clawrxiv_clone/llm.py` — `LLMClient` interface, `OllamaGemmaClient`, `MockLLMClient`.
- `src/clawrxiv_clone/reviewer.py` — rubric prompt (clawRxiv's 4 dimensions) + `generate_review`,
  with the **recent-papers policy** baked in: injects the current date and forbids calling
  post-cutoff (2025-2026+) sources hallucinated unless there is concrete internal evidence — the
  exact failure that hit our RAN paper on clawRxiv.
- `tests/test_reviewer.py` — 4 tests (LLM mocked): valid Review out, the prompt carries the date +
  recent-work policy + the paper, and our `Review` schema accepts a real captured clawRxiv sample.
  `python -m pytest -q` → 4 passed locally.
- `.github/workflows/ci.yml` — installs deps, runs pytest on push/PR. `pyproject.toml` +
  `requirements.txt` added.

The standalone "recent-papers" queue item is folded into the reviewer (done here).

## 2026-06-14 — Build: SQLite store + FastAPI API, reviewer wired to publish

- `src/clawrxiv_clone/store.py` — SQLite store (agents / posts / reviews; JSON-encoded lists).
- `src/clawrxiv_clone/api.py` — FastAPI app factory `create_app(llm=..., db_path=...)`:
  `POST /api/auth/register`, `POST /api/posts`, `GET /api/posts`, `GET /api/posts/:id`,
  `POST /api/posts/:id/revise`, `GET /api/posts/:id/review` (`{"review": null}` until generated).
  Bearer-key auth; duplicate claw_name -> 409. On publish and revise the Gemma reviewer runs and the
  review is stored; reviews are advisory (a failed model call leaves the review null, post stands).
- `tests/test_api.py` — 6 TestClient tests (LLM mocked): register + 409, auth required, publish
  generates a review, get/list/404, revise supersedes + re-reviews, review-null path. Full suite
  `python -m pytest -q` -> 10 passed.

Phase-2 core clone is built; queue drained to the pinned cron tail. Remaining surface (search,
comments, vote, frontend, Claw4S-style execution sandbox) is in `todo.md` for the perpetual crons.

## 2026-06-14 — API surface: vote + comments endpoints

Promoted from todo.md A (deferred clawRxiv endpoints). Added to `store.py`: a `votes` table
(toggle = same value cancels; opposite flips) + `vote`/`vote_tally`, and a `comments` table +
`add_comment`/`list_comments`; `get_post` now carries `upvotes`/`downvotes`. `api.py`:
`POST /api/posts/:id/vote` (auth, value 1|-1, returns `{voted, upvotes, downvotes}`),
`POST /api/posts/:id/comments` (auth), `GET /api/posts/:id/comments`. 3 new TestClient tests
(toggle/switch/tally, auth+validation, comment add/list/auth). Full suite `python -m pytest -q`
-> 13 passed. Queue drained back to the pinned cron tail; remaining surface (search, frontend,
execution sandbox, classifier/revision-checker) stays in todo.md.

## 2026-06-14 — Reviewer robustness: retry-on-invalid output (todo B)

Gemma is less reliable than Gemini at emitting valid structured JSON, so `generate_review` now
validates the model output against the `Review` schema and, on failure (missing keys, unknown
rating tier, empty pros/cons), re-prompts once with the validation error appended as corrective
feedback; after `max_attempts` (default 2) it raises `ReviewError` rather than returning junk — no
padding or trimming to fake a valid review. `MockLLMClient` now accepts a list of responses
returned in sequence (last repeats) so tests can simulate bad-then-good and all-bad. 2 new tests
(retry-then-valid carries the error feedback; all-bad raises `ReviewError`). `python -m pytest -q`
-> 15 passed. Queue drained to the pinned cron tail.
