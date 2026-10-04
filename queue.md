# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

---

## Active

**Goal (Emma, 2026-10-03):** get a paper out fast, for arXiv endorser rights. A
clawRxiv paper that reviews well counts as good enough for arXiv. The paper is
about cleanvibe, lives at cleanvibe.emmaleonhart.com/paper, and CI posts it to
clawRxiv. Paper items come first.

1. **Post to clawRxiv and run the review loop** (Emma, 2026-10-04: post it;
   research CI/CD as in latent-space-cartography). ai-context-research has
   `.github/workflows/clawrxiv.yml` (`9dfc8b7`): a push changing
   `claw4s/note.md` or `SKILL.md` posts or revises the note, waits for
   clawRxiv's AI review and commits it to `claw4s/reviews/`.
   Posted 2026-10-04 as clawRxiv 2610.02893 (post 2893). Round 1: v6
   rated **Reject** (Gemini 3 Flash; "hallucinated" NoLiMa citation, which
   is real, plus scope, bias, no public data). v7 (`d804fd2`) answers each
   point in `claw4s/review.md` and was pushed as a revision.
   **BLOCKED-ON-EXTERNAL:** clawRxiv's review of v7 (run 37234965304);
   unblock signal: a new file in `claw4s/reviews/`. Then read it, revise,
   repeat until it reviews well. The public-data point needs Emma's call on
   publishing `research/data/release/` (NEEDS-DECISION, in that repo).
2. **Publish the paper at cleanvibe.emmaleonhart.com/paper** (`pages/paper/`;
   the site is public) once it is posted.
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
- Narrative history: `git log`. Current version: `2.0.3`.
