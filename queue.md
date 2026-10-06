# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

---

## Active

**Goal (Emma, 2026-10-03):** get a paper out fast, for arXiv endorser rights. A
clawRxiv paper that reviews well counts as good enough for arXiv. The paper is
about cleanvibe, lives at cleanvibe.emmaleonhart.com/paper, and CI posts it to
clawRxiv. Paper items come first.

1. **Standing: the clawRxiv review loop** (Emma, 2026-10-04: keep it
   running; it is the research CI/CD). In `EmmaLeonhart/ai-context-research`,
   a push changing `claw4s/note.md` or `SKILL.md` posts a revision and CI
   commits clawRxiv's AI review to `claw4s/reviews/`. **Every tick:** pull
   that repo; if a new review has landed, answer what text can answer in
   `claw4s/note.md`, log the responses in `claw4s/review.md`, rebuild to
   check it is still 4 pages, push. If the review is still pending, move on
   to the next item. Never "done"; only Emma stops it. **If a review has not landed an hour after posting** (Emma, 2026-10-05): run the review locally (`scratch/clawrxiv_clone`: `python scripts/review.py <note> -o ../paper-score/<name>.review.json`, gemma3 via Ollama), act on what it says, then check clawRxiv again; if still nothing, repost with `gh workflow run clawrxiv.yml -R EmmaLeonhart/ai-context-research -f force_submit=true`. Latest: v13 reposted as post 2901 (post 2900 was never reviewed): Weak Reject, same cons as v12, all needing data; stands until round 3 practice sessions (item 2) give some. Avoid explicit 2026 dates (the reviewer reads them as future).
2. **Experiment: practice projects and reports on them** (Emma,
   2026-10-05). Start cleanvibe 2.0.4 projects under `tests/scratch/` on
   small real tasks (`python -m cleanvibe.cli new <name>` from this repo,
   since Emma's installed cleanvibe is not upgraded), so the staleness hook
   gets sessions to measure. Write each one up under `docs/case-studies/`.
   Goal (Emma): more work, to get the paper above Weak Accept (v13 got Weak
   Reject; every con needs data). Launch with the first-session prompt
   (`_launch_claude(p, templates.v2_first_prompt(p, False), ...)`), not
   `!runClaude.bat`, which sends the resume prompt. Running:
   `notes-to-site` (brief in its `data_lake/`: Markdown notes -> static
   site with backlinks), launched 01:41 UTC, 2026-10-06 (from its initial
   commit). By 02:15 UTC: intake ran on time (WORK MODE), INTENT.md set from
   the brief, update check run, queue/todo/devlog planned, three build
   commits with tests. By 02:45 UTC: first version done in 37 minutes
   (51 tests, CI green on 6 jobs, private repo
   `EmmaLeonhart/markdown-notes-static-site`), INTENT.md updated at
   completion; since then idle ticks that see the empty queue and decline
   to refill (todo.md holds only extras beyond the brief), as in round 2.
   The staleness hook fires ("last changed 0.5 hours and 0 commits ago"),
   but INTENT.md never goes stale with no commits. Next practice project:
   a task big enough to keep committing for hours, so the round 3
   comparison (ticks with INTENT.md over 2 h stale) has cases.
   Running: `quiet-gentle-otter` (auto-named, so it also tests the
   passphrase folder + title; brief: a pure-Python SQL database with a
   B-tree file format, indexes, joins, crash-safe transactions, and
   differential tests against sqlite3), launched 02:45 UTC, 2026-10-06.
   Both finished their brief in under 45 min and idled; written up as
   case study 08 (no round 3 cases). Running: `silver-jolly-tulip`
   (auto-named; brief: an R7RS-small Scheme in pure Python in five stages,
   interpreter -> call/cc and macros -> libraries -> bytecode VM ->
   conformance suite), launched 05:15 UTC, 2026-10-06. Decision (Claude,
   Emma not answering): a long staged brief rather than waiting for a
   human to feed requests, so round 3 gets hours of commits.
   By 06:50 UTC: intake on time, INTENT.md set at 05:45 UTC and not touched
   since, stages 1-3 done (interpreter, call/cc + syntax-rules, libraries +
   ports + CLI), stage 4 (bytecode VM) in progress, 15 commits, still
   committing every few minutes. Round 3 cases start once INTENT.md passes
   2 h stale with commits continuing; write up case study 09 when stage 5
   ends or the session idles. Two findings for case study 09: (a) the
   whole build from intake (05:45) to 06:47 UTC was ONE turn, so neither
   the Stop hook (sessions/ still at 05:15) nor the half-hour cron (fires
   only when the REPL is idle) ran during it: a long turn produces no
   ticks to measure. (b) The session died about 06:48 UTC. Emma's scheduled
   job relaunched its sessions at 06:49:57 and this one was not among them.
   Resumed with `open_project` (resume prompt) at 07:10 UTC.
3. **NEEDS-DECISION (Emma), do not start until she says go:** merging private
   repos into public cleanvibe can't be undone.
   **Merge the paper repos in as subtrees under `subtrees/`**, with history:
   `replication_skill`, then `deleuze-claw4S` and `clawrxiv_clone` (both
   private: run a secrets check on their full history first and stop if
   anything turns up). Move `helping-with-arxiv/` to `subtrees/` and delete its
   boilerplate `queue.md`.
4. **Quatrix arXiv submission:** BLOCKED-ON-USER-ACTION. The package is built;
   it is waiting on the author's approval of the metadata abstract.

**Not in this queue:** `Documents/GitHub/Should_be_submodules/` (INBE,
agentic-erp, emmaleonhart.com, topaz_buiness_plan). Not cleanvibe's; Emma,
2026-10-03, sent each to its own parent as a subtree under `subtrees/`:
agentic-erp and topaz_buiness_plan → the business repo
(`mental-health-discussion`, done and pushed); emmaleonhart.com →
`narrative_identity` (merged in a scratch clone, push blocked by the auto-mode
classifier: BLOCKED-ON-USER-ACTION); INBE → `genealogy`, a submodule of
ontology-harness (done and pushed; ontology-harness's pointer to genealogy not
bumped).

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `2.0.4`.
