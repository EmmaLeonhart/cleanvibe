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
