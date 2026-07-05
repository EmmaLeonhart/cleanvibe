# cleanvibe — Work Queue

**This file is a queue of *concrete, executable steps*, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `devlog.md` (a dated entry) and `git log`; longer-horizon, *abstract* work lives in `todo.md` and gets decomposed into items here when it's ready to execute. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Do not add checkmarks, "done" markers, or status indicators in place. If an item is still here, it is not done.

**Why this file exists:** when a planning step (formal planning mode or just "think before doing") produces a plan, that plan is written here BEFORE execution starts. That way an interrupted session can pick up from the queue rather than from chat context that may be gone.

The purpose of this file is also to bound scope. If a task is not in this queue, it is not in scope for the current session. New ideas go at the bottom of the queue (or to `todo.md` if they are longer-term / architectural), not silently into whatever is being worked on.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

**Three-cron playbook.** Extensive work runs under three local `CronCreate` jobs — **work-loop at :03** (the engine that drains `queue.md` and refills it from `todo.md`), **auto-flush at :15** (commit/push backstop), and **status-report at :42** (heartbeat). On a fresh session they are **started** as the opening step (bootstrap step 1 below); on a mid-session **large-scale re-fill** of this queue the FIRST item worked is instead to **kill** the already-running crons. Either way the **last two items are always pinned at the tail** — ensure the three crons are running, then run an end-of-session summary (see the `## Always last` section below and `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook"). Entering planning mode also disables the crons; their restart lives at the end of the queue.

---

## Active — First-session bootstrap

These items are the default opening sequence for a new cleanvibe project. Work them top to bottom. **Delete each item from this file in the same commit that completes it, and append a dated entry to `devlog.md` recording the step.** Push after every step. When this whole section is gone, the project has finished bootstrap and the queue is ready to be repopulated with real product work (see the final item).

1. **Start the three-cron playbook.** Use the `CronCreate` tool to schedule three local crons (all `durable: false`): **work-loop at `3 * * * *`** (sync → take top actionable `queue.md` item / promote from `todo.md` → hold the hard rails → commit + push → one-line report), **auto-flush at `15 * * * *`** (commit + push pending work, no empty commits), and **status-report at `42 * * * *`** (reporting only, no code changes). Together they turn this bootstrap run into a self-sustaining hourly cadence so a long autonomous session can't silently lose the thread. (See `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook"; the `## Always last` section pinned at the tail keeps them running — starting them here, restarting them there if a later planning burst / queue re-fill kills them.)

2. **Triage user-supplied files into `data_lake/`.** Look at everything in the repo that isn't part of the cleanvibe scaffold (i.e. anything the user dropped in: notes, exports, spec PDFs, sample data, mockups, etc.).
   - `data_lake/` already exists — the scaffold created it with a `.gitkeep` (so a user could drop files straight into it before this session). Move all such files into `data_lake/` so the project root stays clean. Only the scaffold (`CLAUDE.md`, `README.md`, `queue.md`, `.gitignore`, `LICENSE`, and any source/config files you have explicitly chosen to keep at the root) should live at the top level. Leave the `.gitkeep` in place.
   - If any of these files are `.zip` archives, extract them into `data_lake/` alongside the originals, then add the `.zip` files to `.gitignore` (we keep the extracted contents in git, not the archives).
   - For any file that looks big enough to need Git LFS (rough rule of thumb: >50 MB, or large binary like video/audio/large datasets), STOP and ask the user before doing anything — do not silently commit it, do not silently `git lfs track` it.
   - Commit. Commit message should describe what got moved/extracted and why.

3. **Read the data lake to infer what this project is.** Skim every file in `data_lake/` (text files, READMEs from extracted zips, design notes, spec docs, sample data shapes). Build up a working hypothesis: what is the user trying to build? What domain? What constraints or instructions are stated explicitly?
   - Update `README.md` to reflect this hypothesis: project description, any explicit instructions you found, anything load-bearing for future sessions.
   - Update `CLAUDE.md`'s "Project Description" and "Architecture and Conventions" sections to capture the same context for future Claude sessions.
   - Do NOT touch `queue.md` in this commit — the real queue gets written later, after talking to the user.
   - Commit. Commit message should briefly explain how the inferred description was derived (e.g. "Inferred project scope from data_lake/spec.md and data_lake/notes/").

4. **Interview the user about what they actually want to build.** Your inferred picture from the data lake is a starting point, not the spec. Ask the user direct, specific questions to fill in the gaps: what is the goal of the first usable version? What's the longer-term vision (capabilities, integrations, audience) beyond v1? What's in scope vs. out of scope for this session? Are there constraints (language, framework, deployment target, must-integrate-with-X)? What does "done" look like for them today?
   - As answers come in, fold them into `README.md` and `CLAUDE.md` so future sessions inherit the context.
   - Capture both **near-term** answers (what to build now) AND **long-horizon** answers (what's wanted eventually). The long-horizon material is what feeds `todo.md` in the next step.
   - Commit once the picture is concrete enough to plan against.

5. **Create `todo.md` — the long-horizon backlog.** This is the step before any concrete queue gets written. Based on the interview and inferred picture, write `todo.md` as the project's long-term horizon: every multi-session goal, architectural ambition, capability, integration, or future direction the user described. Items here are *abstract destinations*, not steps — they will be decomposed into concrete tasks in `queue.md` later, one at a time, as the work unfolds. `todo.md` is the *basis for* `queue.md`: work flows `todo.md` → `queue.md` → executed → deleted from both.
   - Use the convention described in `CLAUDE.md` § "Queue and longer-horizon work" for the file format.
   - Do NOT touch `queue.md` in this commit — populating the real queue is the *next* step.
   - Commit `todo.md` on its own so the long-horizon picture is a reviewable artifact, not buried inside a larger change.

6. **Replace this bootstrap queue with the real project queue.** Pull the first item (or first few items) from `todo.md` and decompose them into a concrete, ordered list of implementation tasks. Write those into the `## Active` section of this file (deleting this bootstrap section entirely as part of the same edit). Each task should be small enough to finish and commit on its own. Mirror the queue into the task tool. As you drain queue items, refill by pulling and decomposing more from `todo.md`.
   - **Keep the `## Always last — restart the three crons and summarize` section pinned at the very bottom of the queue.** It is never deleted; real work items go above it. The real queue's FIRST work item should **start the three crons (work-loop, auto-flush, status-report)** — unless this is a mid-session large-scale re-fill while they are already running, in which case the first item is instead to **kill them** (the pinned tail restarts them). Planning mode disables the crons; the tail brings them back.
   - Commit the new queue.

7. **Create a private GitHub repo and push.** Use whatever GitHub tooling is available (e.g. `gh repo create --private --source=. --push`) to create a private remote and push the current branch. Confirm CI (`.github/workflows/`) is wired up so pushes run tests.

8. **Work the queue until the stop condition.** Pull the top item, do it, **delete it from `queue.md` AND append a dated entry to `devlog.md`** in the same commit as the work, push, let CI run. When `queue.md` empties, refill from `todo.md` by decomposing the next item. New ideas that surface mid-work go to the bottom of the queue (or to `todo.md` if they're longer-horizon), not into the currently-in-flight task. **Stop** when: `queue.md` is empty, the items still in `todo.md` are too abstract to break down further without more user input, and the repository is online with green CI. At that point, hand back to the user.

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
