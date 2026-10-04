# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

---

## Active

**Goal (Emma, 2026-10-03):** get a paper out fast, for arXiv endorser rights. A
clawRxiv paper that reviews well counts as good enough for arXiv. The paper is
about cleanvibe, lives at cleanvibe.emmaleonhart.com/paper, and CI posts it to
clawRxiv. Paper items come first.

1. **The paper lives in `EmmaLeonhart/ai-context-research`** (private), not
   here. Its `paper/draft.md`, Claw4S `SKILL.md` and 2-page note
   (`claw4s/note.md`) are written; another session works that repo. Do not
   write a second paper here. NEEDS-DECISION (Emma), tracked in that repo's
   queue: review the note, and whether to post to clawRxiv.
2. **Respond to the Claw4S review and refine the hypothesis** (Emma,
   2026-10-04: "continue working… responding to the Claw4S analysis"). Work in
   ai-context-research (pull first; another session may be active). The local
   reviewer gave Weak Accept (4/3/4/4) with five cons: one user/scaffold/agent;
   heuristic read detection; no compaction; transcripts not released;
   correlation not causation. Answer each in the note where data allows:
   validate the read heuristic against a hand-checked sample; release the
   per-tick aggregates; sharpen the hypothesis to "the same duty holds when
   bound to an event and drops when it is standing" using the duties that
   moved between the two (M2 update check 0/9 → 6/6) as the closest thing to
   an intervention; state the rest as limits. Rescore with the reviewer clone.
3. **Once Emma approves posting:** publish the paper at
   cleanvibe.emmaleonhart.com/paper (`pages/paper/`; this site is public), and
   post to clawRxiv as the existing `Emma-Leonhart` agent (`POST /api/posts`,
   Markdown `content` + `skill_md`), from CI with the key as a repo secret.
   Score it first with the clawRxiv reviewer clone in `clawrxiv_clone`.
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
- Narrative history: `git log`. Current version: `2.0.3`.
