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
   commits with tests.
3. **Publish the paper at cleanvibe.emmaleonhart.com/paper** (`pages/paper/`;
   the site is public). The note is posted on clawRxiv. Emma approved
   publishing (2026-10-04), but the auto-mode classifier refused the write
   ("Out-of-Place Publication"). **BLOCKED-ON-USER-ACTION (Emma):** she
   publishes the page herself or adds a permission rule that allows it.
4. **NEEDS-DECISION (Emma), do not start until she says go:** merging private
   repos into public cleanvibe can't be undone.
   **Merge the paper repos in as subtrees under `subtrees/`**, with history:
   `replication_skill`, then `deleuze-claw4S` and `clawrxiv_clone` (both
   private: run a secrets check on their full history first and stop if
   anything turns up). Move `helping-with-arxiv/` to `subtrees/` and delete its
   boilerplate `queue.md`.
5. **Quatrix arXiv submission:** BLOCKED-ON-USER-ACTION. The package is built;
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
