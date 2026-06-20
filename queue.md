# clawrxiv_clone — Work Queue

**This file is a queue of *concrete, executable steps*, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `devlog.md` (a dated entry) and `git log`; longer-horizon, *abstract* work lives in `todo.md` and gets decomposed into items here when it's ready to execute. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Do not add checkmarks, "done" markers, or status indicators in place. If an item is still here, it is not done.

**Why this file exists:** when a planning step (formal planning mode or just "think before doing") produces a plan, that plan is written here BEFORE execution starts. That way an interrupted session can pick up from the queue rather than from chat context that may be gone.

The purpose of this file is also to bound scope. If a task is not in this queue, it is not in scope for the current session. New ideas go at the bottom of the queue (or to `todo.md` if they are longer-term / architectural), not silently into whatever is being worked on.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

**Three-cron playbook.** Extensive work runs under three local `CronCreate` jobs — **work-loop at :03** (the engine that drains `queue.md` and refills it from `todo.md`), **auto-flush at :15** (commit/push backstop), and **status-report at :42** (heartbeat). On a fresh session they are **started** as the opening step (bootstrap step 1 below); on a mid-session **large-scale re-fill** of this queue the FIRST item worked is instead to **kill** the already-running crons. Either way the **last two items are always pinned at the tail** — ensure the three crons are running, then run an end-of-session summary (see the `## Always last` section below and `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook"). Entering planning mode also disables the crons; their restart lives at the end of the queue.

---

## Phase 1 — investigation: DONE (record)

The reverse-engineering of clawRxiv's AI peer review is complete; write-up in
`investigation/FINDINGS.md` with captured live-API evidence (`investigation/samples/`) and the
closest open artifact (`investigation/references/labclaw_peer_review_SKILL.md`). Headline: the
reviewer is a single **Gemini 3 Flash** call per submission returning a fixed JSON review
(`rating` tier, `summary`, 5 `pros`, 5 `cons`, `justification`); endpoint surface + both rubrics
documented. (This bullet is a pointer; the bootstrap section it replaced is in git history.)

## Phase 2 — core clone built (record)

Reviewer (Gemma) + schema + SQLite store + FastAPI publish/read/revise/review API, reviewer
wired to publish, 10 pytest tests green. Further surface (search, comments, vote, frontend,
execution sandbox) lives in `todo.md`; the perpetual crons (started by the pinned tail) will pull
and decompose those next.


---

## CLI enablement — point the reviewer at an arbitrary paper PATH

These make `scripts/review.py` usable as a command-line tool against any paper file, then run it
on two specific papers. **Today `scripts/review.py` accepts exactly one arg — a path to a `.md`
file** (read UTF-8, parsed by `parse_markdown_paper`: first `# H1` = title, first blank-line block
= abstract, rest = body), runs one Gemma review via `OllamaGemmaClient` (Ollama at
`$OLLAMA_HOST`, default `http://localhost:11434`, model `$CLAWRXIV_REVIEW_MODEL`, default
`gemma3:12b`), and **prints the review JSON to stdout** (it does NOT save a file, does NOT accept
`.tex`/`.pdf`, and exits 2 with usage text if argc != 2). Each step below is concrete.

1. **Make `scripts/review.py` argument handling robust.** In `scripts/review.py`: switch from the
   bare `len(sys.argv) != 2` check to `argparse` with one positional `paper_path` and an optional
   `-o/--output PATH`; resolve `paper_path` via `pathlib.Path(...).expanduser().resolve()`; if the
   file does not exist print `error: no such file: <path>` to stderr and `return 2` (keep the exit
   code so callers can detect failure). Update the module docstring to match. Keep the existing
   stdout JSON print as the default behaviour.

2. **Add `.tex` / `.pdf` text extraction so the path arg is not `.md`-only.** Add
   `src/clawrxiv_clone/extract.py` with `extract_text(path: pathlib.Path) -> str` that dispatches
   on suffix: `.md`/`.markdown`/`.txt` → `path.read_text(encoding="utf-8")`; `.tex` → read text and
   strip the LaTeX preamble/commands enough to feed `parse_markdown_paper` (at minimum: take from
   `\begin{document}` onward if present, drop comment lines starting `%`, convert `\section{X}` →
   `# X` and `\title{X}` → `# X`); `.pdf` → extract text with `pypdf` (add `pypdf` to
   `requirements.txt` and `pyproject.toml`), raising a clear `RuntimeError` if `pypdf` is not
   installed. Unknown suffix → fall back to `read_text`. Wire `scripts/review.py` to call
   `extract_text(paper_path)` instead of `.read_text(...)`. Add a `tests/test_extract.py` covering
   the `.md` passthrough and the `.tex` `\section`→`#` conversion with a `MockLLMClient`-free pure
   string test (no live model).

3. **Add a `scripts/review_paper.py` wrapper that saves the review next to the paper.** It takes a
   paper PATH (any of `.md`/`.tex`/`.pdf`), calls `extract_text` → `parse_markdown_paper` →
   `generate_review(paper, OllamaGemmaClient())`, prints the JSON to stdout AND writes it to
   `<paper_stem>.review.json` in the paper's own directory (e.g. `paper.md` →
   `paper.review.json`), unless `-o/--output` overrides the destination. Print the saved path to
   stderr so stdout stays pure JSON. This is the entry point Emma drives for experiments.

4. **EXPERIMENT — run the reviewer on the Sutra formal-verification (FV) paper.** The FV paper is
   `paper/formal-verification/paper.md` in **EmmaLeonhart/Sutra**; the local Sutra clone is ABSENT
   (deleted in a workspace cleanup), so first fetch just that one file —
   `gh api repos/EmmaLeonhart/Sutra/contents/paper/formal-verification/paper.md --jq .content | base64 -d > /tmp/fv_paper.md`
   (or `gh repo clone EmmaLeonhart/Sutra` if the whole repo is wanted) — then with local Ollama
   serving `gemma3:12b` run `python scripts/review_paper.py /tmp/fv_paper.md` and confirm a
   structured review JSON is printed and `/tmp/fv_paper.review.json` is written. Record the
   `rating` and `scores` in `devlog.md`.

5. **EXPERIMENT — run the reviewer on the latent-space-cartography paper.** Its `paper.md` is at
   the repo root of **EmmaLeonhart/latent-space-cartography**; the local clone is present at
   `C:\Users\Immanuelle\Documents\Github\latent-space-cartography\paper.md` (else
   `gh repo clone EmmaLeonhart/latent-space-cartography`). With local Ollama serving `gemma3:12b`
   run `python scripts/review_paper.py ../latent-space-cartography/paper.md` and confirm the review
   JSON prints and `../latent-space-cartography/paper.review.json` is written. NOTE: this paper
   uses a `## Abstract` header rather than a blank-line abstract block, so `parse_markdown_paper`
   currently treats the author line as the abstract — verify the review still reads as sensible, and
   if not, file a follow-up queue item to teach `parse_markdown_paper` to recognise a `## Abstract`
   section. Record the `rating` and `scores` in `devlog.md`.

---

## Always last — restart the three crons and summarize

**These two items stay pinned to the tail of the queue at all times** — below every bootstrap step and below every real work item. They are the closing half of the three-cron lifecycle described in `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook": the crons are **started** at the beginning of extensive work (a fresh session starts them as the opening item; a mid-session large-scale re-fill instead kills the already-running crons as its first item, and planning mode disables them), and these are always the LAST two, after everything else — they bring them back and sign off:

A. **Ensure the three crons are running** — start them if this session never did, restart them if a planning burst / queue re-fill killed them: work-loop (`3 * * * *`), auto-flush (`15 * * * *`), status-report (`42 * * * *`).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

(During first-session bootstrap these simply sit here at the bottom; they become load-bearing the moment the queue is filled with a large batch of created tasks.)

---

## Pointers

- Long-horizon backlog (abstract goals, source of future queue items): `todo.md`.
- Completed work (chronological, with releases): `devlog.md`.
- Narrative history: `git log`.
