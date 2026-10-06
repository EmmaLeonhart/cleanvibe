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
   v14 (`aec436d`: first round 3 case, round 3 transcripts public) is
   pushed but NOT posted: **BLOCKED-ON-USER-ACTION**. The repo is private
   and GitHub refused the clawRxiv job for billing (private Actions minutes
   used up, 2026-10-06), and there is no local `CLAWRXIV_API_KEY` to post
   by hand. Unblocks when Emma raises the Actions spending limit, makes the
   repo public, or gives a local key; then rerun the workflow.
2. **Experiment: practice projects and reports on them** (Emma,
   2026-10-05). Start cleanvibe 2.0.4 projects under `tests/scratch/` on
   small real tasks (`python -m cleanvibe.cli new <name>` from this repo,
   since Emma's installed cleanvibe is not upgraded), so the staleness hook
   gets sessions to measure. Write each one up under `docs/case-studies/`.
   Goal (Emma): more work, to get the paper above Weak Accept (v13 got Weak
   Reject; every con needs data). Launch with the first-session prompt
   (`_launch_claude(p, templates.v2_first_prompt(p, False), ...)`), not
   `!runClaude.bat`, which sends the resume prompt. **Practice repos are
   PUBLIC** (Emma, 2026-10-06: the research shows the transcripts; private
   repos also burn Actions minutes). The first prompt says private, so put
   a "create the GitHub repo public" section in each brief in `data_lake/`
   before the intake runs. So far: three projects
   (case studies 08 and 09). Round 3 has **one case** (09: the hook fired at
   2.1 h stale and the next commit updated INTENT.md with substance). Short
   briefs finish in under 45 min and give none; a staged brief gave one.
   Next: more long staged briefs, so round 3 gets a rate. Practice sessions
   die in Emma's scheduled relaunch: check every tick and resume a dead one
   with `open_project` (resume prompt); ticks only exist between turns, so
   count staleness against commits as well as ticks. Running:
   `velvet-vivid-otter` (auto-named; brief: a pure-Python git in five
   stages, object store -> index/commit -> branches/diff -> merge ->
   packfiles and local clone/fetch/push, each checked byte for byte against
   real git), launched 08:39 UTC, 2026-10-06. `silver-jolly-tulip` is done
   (case study 09) and idles.
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
