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

## 2026-06-14 — Search endpoint: GET /api/search (keyword + tag)

`store.search_posts(q, tag, limit, offset)` — title/abstract LIKE (case-insensitive for ASCII)
plus optional exact tag membership on the decoded JSON tags. `GET /api/search?q=&tag=&page=&limit=`
returns the same `{posts, page, limit}` shape as list. 5 TestClient assertions (q-on-title,
q-on-abstract, tag filter, q+tag, empty). `python -m pytest -q` -> 16 passed. Semantic
`/api/search/similar` (needs embeddings) deferred to todo.md. Queue drained to the pinned cron tail.

## 2026-06-15 — Real Gemma wired and verified (stop hiding behind mocks)

gemma3:12b is installed in local Ollama; ran the reviewer against it for real:
- `scripts/review.py paper.md` runs a live review end-to-end. A real run on the RAN abstract
  returned a valid review (rating Borderline) in ~42s; model field = `gemma3:12b`.
- **The recent-papers policy works on the live model.** Gemma wrote, of a real 2026 citation
  (arXiv:2508.18130), "which I cannot verify" / "(though I cannot verify the cited work)" — calibrated
  uncertainty, NOT "hallucinated/fabricated." Exactly the fix the user asked for, confirmed against
  real Gemma rather than a mock.
- Fixed the default model tag `gemma3` -> `gemma3:12b` (the tag actually installed).
- Added `tests/test_integration.py` — a live test guarded by `CLAWRXIV_LIVE=1` (CI skips it; run
  locally to re-verify the real path). Default suite: 16 passed, 1 skipped.

## 2026-06-15 — Classifier subsystem (todo E), verified on real Gemma

Second AI subsystem parallel to the reviewer (clawRxiv auto-classifies each paper):
- `schema.Classification` (category + 0-3 cross_list); `classifier.py` — `classify_paper` does one
  Gemma structured-output call constrained to a fixed 20-item arXiv-style category set, re-prompts
  once on invalid output, filters out-of-set / self cross-list entries, raises `ClassificationError`
  on failure (no inventing categories).
- store: posts gain nullable category/cross_list + `save_classification`; `get_post` surfaces them.
- api: `create_app` gains a `classify_llm` (independently mockable); `POST /api/posts/:id/classify`
  (auth) classifies + stores + returns; 404/401 handled.
- Tests: classifier unit (valid, out-of-set filtering, retry-then-raise) + an API classify test.
  Suite: 21 passed, 1 skipped.
- **Verified on real gemma3:12b** (not just mocks): the RAN paper classified as cs.LG (cross-list
  cs.AI, stat.ML), in-set, ~17s.

## 2026-06-15 — Revision-equivalence checker (todo E) — all three AI subsystems done

Third (and last) clawRxiv AI subsystem: "verifies revisions represent the same body of work."
- `schema.EquivalenceVerdict` (equivalent: bool, reason: str); `equivalence.check_equivalence`
  (original, revised, llm) — one Gemma call deciding same-body-of-work vs substantially different;
  re-prompt once; raise `EquivalenceError` on failure.
- api: `create_app` gains an independently-mockable `equivalence_llm`; `POST /api/posts/:id/check-revision`
  (auth) looks up the post's supersedes target, compares, returns the verdict; 400 if not a revision.
- Tests: equivalence unit (same/different/retry-then-raise) + API endpoint (verdict, 400 non-revision,
  401 no-auth). Suite: 25 passed, 1 skipped.
- **Verified on real gemma3:12b:** same-work revision -> equivalent=True (18s); an unrelated GNN survey
  -> equivalent=False (6s), with sensible reasons.

With this, all three clawRxiv AI subsystems are reconstructed on Gemma: reviewer (recent-papers
policy), classifier (arXiv category), and revision-equivalence checker. Remaining todo: semantic
search (embeddings available locally), frontend, and the hard execution sandbox.

## 2026-06-15 — Semantic search: GET /api/search/similar (embeddings)

- `embeddings.py` — `EmbedClient` interface, `OllamaEmbedClient` (default nomic-embed-text),
  `MockEmbedClient` (deterministic keyword vectors), `cosine`, `embed_text`.
- store: posts gain a nullable `embedding` (JSON) column + `set_embedding`/`get_embedding`/`post_briefs`.
- api: `create_app` gains an independently-mockable `embedder`; `GET /api/search/similar?post_id=&limit=`
  lazily embeds + caches any missing vectors, then cosine-ranks the rest against the target (excludes
  the target), returns top-N with scores. 404 on unknown post.
- Tests: cosine + mock-embed units; the similar endpoint ranks same-topic posts above off-topic
  (MockEmbedClient). Suite: 29 passed, 1 skipped. (Fixed one over-strict float-equality assertion in
  the cosine test -- the code was right; identical-vector cosine is 0.9999999998, not exactly 1.0.)
- **Verified on real nomic-embed-text** (768-dim): a reservoir/reservoir pair (cosine 0.661) ranks
  above reservoir/graph (0.588).

## 2026-06-15 — Auto-wire subsystems into publish/revise + production entry

The AI subsystems now run automatically like clawRxiv (the on-demand endpoints stay too):
- `POST /api/posts` -> auto-review + auto-classify. `POST /revise` -> auto-review + auto-classify +
  auto revision-equivalence vs the superseded post (verdict stored on the revision).
- Auto-runs are conditional on the relevant client being configured (`auto_classify`/`auto_equivalence`
  captured at construction), so CI (review-mock only) makes zero network calls; all advisory (a failed
  subsystem never breaks publishing). store: `revision_equivalent`/`revision_reason` columns +
  `save_equivalence`; `get_post` surfaces them.
- `server.py` `production_app()` wires real OllamaGemmaClient(s) + OllamaEmbedClient + a file DB;
  `uvicorn clawrxiv_clone.server:production_app --factory`.
- Tests: auto classify+equivalence on publish/revise (mocks); no-auto path stays network-free.
  31 passed, 1 skipped.
- **Verified live end-to-end:** one real POST /api/posts auto-reviewed (Borderline, gemma3:12b) AND
  auto-classified (cs.AI; cross-list cs.LG, stat.ML) in ~50s.

## 2026-06-15 — API docs (so papers can be submitted) + drop internal embedding from post shape

- `API.md` — full endpoint reference + a register -> submit -> read-review curl quickstart, plus the
  server run instructions (Ollama + gemma3:12b + nomic-embed-text;
  `uvicorn clawrxiv_clone.server:production_app --factory`). Linked from README.
- Dropped the raw 768-dim `embedding` vector from the public `GET /api/posts/:id` shape (internal).
- **Verified the documented quickstart end-to-end against a live server:** register -> submit ->
  real gemma3:12b review (Borderline, 5 pros/5 cons) + auto-classify (cs.LG; cross-list cs.AI, stat.ML).

## 2026-06-15 — Minimal read-only frontend (todo D)

`src/clawrxiv_clone/web/index.html` — one self-contained page (inline CSS + vanilla JS, no build
step, warm paper theme) that calls the public API: lists posts, and on click shows the paper
(abstract + content) and its AI review (rating badge, summary, pros, cons, justification). Served at
`GET /` via FileResponse. Test: GET / -> 200 text/html with the app markers. 32 passed, 1 skipped.
Live-verified under real uvicorn: GET / returns the 5 KB page (200, text/html). README documents the
UI at http://127.0.0.1:8000/.

## 2026-06-15 — Per-dimension review scores (todo B)

The reviewer now returns numeric rubric scores so the rating is grounded:
- `schema.Review.scores` (`dict[str,int]`, default empty so score-less live clawRxiv samples still
  validate). The reviewer prompt asks for `originality`/`methodology`/`clarity`/`significance` each
  1-5, consistent with the rating. reviews table gains a `scores` JSON column; save/get persist it;
  the review endpoint returns it. API.md updated.
- Tests: prompt requests scores; a review with scores validates + round-trips through the API; a
  score-less response still validates. 36 passed, 1 skipped.
- **Verified live on gemma3:12b:** returned scores {originality 3, methodology 2, clarity 3,
  significance 2} with rating Weak Reject (consistent low scores -> weak reject).
- Moved the higher-risk **async submit** item to todo.md B (own dedicated tick: needs a thread-safe
  store) rather than rushing it here.

## 2026-06-15 — Async submit: non-blocking POST, background review (todo B)

`POST /api/posts` and `/revise` no longer block on Gemma:
- **Thread-safe store:** added an `RLock` and wrapped all 18 public methods (a class-level decorator
  loop) so the shared SQLite connection is safe across request + background-task threads. The slow
  LLM call stays OUTSIDE the lock (only brief DB ops are guarded), so generation never blocks reads.
- **api:** `create_post`/`revise` schedule `review_post` (+ classify / equivalence) via FastAPI
  `BackgroundTasks` and return the id immediately. `GET /review` is null-until-ready (faithful to
  clawRxiv). API.md contract updated (poll for the review).
- **Tests:** existing tests unchanged (TestClient runs background tasks before returning, so review is
  present after POST in tests); added `test_store_concurrency.py` (8 threads x 20 iters = 160
  concurrent posts with get/vote/list -> no errors). 37 passed, 1 skipped.
- **Verified live:** `POST /api/posts` returned in **0.14s** (was ~50s); the review was `null`
  immediately, then appeared ~39s later (Weak Reject) from the background task.

## 2026-06-15 — Accept the reproduction skill (skill_md)

Closed a clawRxiv API-parity gap: papers can now carry an optional `skill_md` (a SKILL.md another
agent can run to reproduce the work). PostBody gains `skill_md`; posts table gains a `skill_md`
column; publish + revise store it; `GET /api/posts/:id` returns it; API.md documents it. **Stored,
not executed** — actually running submitted skills is the separate, decision-gated sandbox item (C).
Tests: publish with skill_md round-trips; without -> null. 38 passed, 1 skipped.

## 2026-06-15 — Submit CLI (frictionless paper submission)

- `src/clawrxiv_clone/papers.py` — `parse_markdown_paper(md) -> Paper` (title = first H1, abstract =
  first paragraph, content = body); `scripts/review.py` refactored onto it (removed its duplicate).
- `scripts/submit.py` — `python scripts/submit.py paper.md`: parses the file, uses `CLAWRXIV_KEY` or
  auto-registers (`CLAWRXIV_CLAW_NAME`), POSTs to `CLAWRXIV_BASE` (default :8000), then polls the
  async review and prints it (rating, pros, cons, scores). Uses httpx (existing dep).
- Tests: `test_papers.py` (parser title/abstract/content + no-H1 fallback). 40 passed, 1 skipped.
  API.md documents the CLI.
- **Live-verified end-to-end** against a running server: registered, submitted, polled, printed a real
  gemma3:12b review (Weak Reject, scores {3,2,2,1}); the recent-papers policy held (the 2026 citation
  was noted, not called hallucinated).

## 2026-06-15 — API key rotation (POST /api/auth/key)

Closed the last clawRxiv auth-parity gap: `POST /api/auth/key` (auth) issues a new API key for the
agent and invalidates the old one. `store.regenerate_key` (added to the thread-safe method set) +
the endpoint + API.md. Test: rotate -> old key 401, new key 200, no-auth 401. 41 passed, 1 skipped.

## 2026-06-15 — Multi-reviewer panel / self-consistency (todo B)

Single-call reviews are noisy (our RAN paper bounced Reject/Weak-Reject across identical-substance
revisions), so added `reviewer.review_panel(paper, llm, k)`: runs k independent reviews, skips any
member that fails validation, sorts by rating ordinal on the 7-tier ladder, and returns the median
member (its rating is the consensus; its text representative). k=1 is the single review (unchanged).
`create_app` gains `review_panel_size` (default 1); `review_post` uses it; `production_app` reads
`CLAWRXIV_REVIEW_PANEL` (default 1). Cheap to adopt now that reviews run in the background.
Tests: median consensus, a failed member is skipped, k=1 unchanged, and an in-app panel. 45 passed,
1 skipped. Verified live: a k=2 real Gemma panel (75s) -> consensus Weak Reject. API.md documents it.

## 2026-06-26 — CLI enablement + first real-paper experiments; fixed long-paper drift

Made `scripts/review.py` a proper CLI: argparse with a positional `paper_path` + `-o/--output`,
path resolution via `expanduser().resolve()`, and `error: no such file: <path>` -> exit 2 on a
missing file. Added `src/clawrxiv_clone/extract.py` (`extract_text` dispatching on suffix: md/txt
passthrough, `.tex` lightly de-LaTeXed — `\begin{document}` onward, drop `%` lines, `\section`->`#`,
`\subsection`->`##` — and `.pdf` via pypdf with a clear RuntimeError when absent); wired both review
scripts through it; added `pypdf` to requirements + pyproject; `tests/test_extract.py` covers the md
passthrough and the tex section conversion. Added `scripts/review_paper.py` which saves the review
to `<paper_stem>.review.json` next to the paper (or `-o`). 49 passed, 1 skipped.

Also fixed a real bug found while running on a long paper: on the 77KB Sutra FV paper gemma3:12b
drifted past the system-prompt schema and returned a *summary* of the paper instead of a review
(validation failed, "rating field required"). The user prompt now restates the task after the
paper, pinning the model back to the review schema.

Experiments (local Ollama gemma3:12b):
- Sutra formal-verification paper -> **Borderline**, scores originality 4 / methodology 3 /
  clarity 2 / significance 4. (~30-80s per review, no clawRxiv round-trip.)
- latent-space-cartography paper -> **Borderline**, scores 3 / 3 / 2 / 4. Review reads sensibly,
  but it uses a `## Abstract` header so `parse_markdown_paper` grabs the author line as the
  abstract — filed a follow-up queue item to teach the parser to prefer a `## Abstract` section.

## 2026-06-29 — clone vs live clawRxiv on our own papers

Ran the Gemma reviewer (gemma3:12b) on the original Sutra paper and the latent-space-cartography
paper; compared to the live clawRxiv (Gemini 3 Flash) reviews. **The clone fixes the defining
failure mode (2/2):** the website Reject/Strong-Rejects both papers on FALSE temporal-hallucination
flags (real 2026 dates/Ollama versions read as "the future"/"fraudulent"); the clone produces ZERO
temporal false-flags and gives content-based Borderline reviews, even crediting the LSC Ollama bug
as significance 5. Findings + build plan: `investigation/2026-06-29-clone-vs-website-comparison.md`;
raw clone reviews: `investigation/samples/clone_review_{sutra,lsc}_2026-06-29.json`.
