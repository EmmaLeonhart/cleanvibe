# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `git log` and `devlog.md`; longer-horizon ideas live in `todo.md`. When an item is done, **delete it here and append a dated entry to `devlog.md`** — never tick a box in place.

**Why this file exists:** when a planning step produces a plan, that plan is written here BEFORE execution starts. An interrupted session can pick up from the queue rather than from chat context.

See `CLAUDE.md` § "Workflow Rules" for how this file, `devlog.md`, planning mode, and the task tool stay in sync.

---

## Active — Add a `devlog.md` ("done" lives here, not as ticked boxes)

Problem being solved: agents sometimes *check off* `queue.md` items in place instead of deleting them, so the queue rots. Fix: a `devlog.md` is the canonical home for completed work. Finishing a queue item means **delete it from `queue.md`, append a dated entry to `devlog.md`, then commit and push.** Ship across all settings (new / clone / convert / replicate) and release.

1. **devlog template + wire into all scaffold paths.** Add `templates.devlog_md(project_name)` (header explaining the workflow + a dated "project scaffolded" entry, chronological, newest at bottom). Write `devlog.md` in `create_project`, `_inject_scaffold` (convert), `clone_project`, and `replicate_project`. Add the devlog workflow rule to `claude_md`, `clone_claude_md`, `replication_claude_md` and to `queue_md`, `clone_queue_md`, `replication_queue_md` — for clone/convert (existing repos) the queue says to **backfill** the devlog from `git log`/existing history first. Add/extend stdlib unittest tests (devlog.md present in each path; templates document the workflow; no "[ ]" checkbox guidance). Keep suite green. Commit.

2. **Dogfood the devlog in this repo.** Create root `devlog.md`, backfilled from this repo's real milestones (it is an existing repo — exactly the backfill case). Update root `CLAUDE.md` (Workflow Rules + a Key Decision) and this `queue.md` preamble to the devlog workflow. Commit.

3. **v1.1.0 release.** Bump `1.0.0` → `1.1.0` (`cleanvibe/__init__.py`, `pyproject.toml`); full test run + `--version` + new/clone/replicate dry-run smokes; commit; push; annotated tag `v1.1.0`; `gh release create v1.1.0` with a summary. Record completed items in `devlog.md` as we go.

---

## Pointers

- Completed work (chronological): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`.
