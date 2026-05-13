"""Default templates that cleanvibe injects into new projects.

The CLAUDE.md template is the core of cleanvibe. It shapes how Claude Code
behaves inside a repo by enforcing documentation discipline, meaningful commits,
queue-driven planning, and thoughtful work tracking.
"""

from datetime import datetime


def claude_md(project_name: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    return f"""# {project_name}

## Workflow Rules
- **Commit early and often.** Every meaningful change gets a commit with a clear message explaining *why*, not just what.
- **Plan into `queue.md` first, then execute.** When entering planning mode (or doing any non-trivial multi-step work), the FIRST action is to write the plan into `queue.md` as concrete items. Only then begin executing. This means an interrupted session can resume from the queue — the plan does not live only in chat context.
- **Update `queue.md` in the same commit as the work.** When you finish an item, delete it from queue.md in the same commit. A stale queue.md is worse than no queue.md — it lies about what's in flight.
- **Mirror `queue.md` into the task tool.** TaskCreate items as you add them to queue.md; mark `in_progress` when starting; `completed` when done. The two views must not drift.
- **Keep this file up to date.** As the project takes shape, record architectural decisions, conventions, and anything needed to work effectively in this repo.
- **Update README.md regularly.** It should always reflect the current state of the project for human readers.

## Queue and longer-horizon work
- **`queue.md`** — what's being worked on right now. Items get deleted on completion; do not leave checkmarks or status indicators behind. If it's not in `queue.md`, it's not in scope for the current session.
- **`todo.md`** — the **long-term horizon** of the project. Multi-session goals, architectural ambitions, future capabilities, "things we want to do eventually." Items in `todo.md` are *abstract*: they describe a destination, not a step. `todo.md` is the *basis for* `queue.md`: when work begins, an item is pulled from `todo.md`, decomposed into concrete executable steps in `queue.md`, mirrored into the task tool, and executed. As `queue.md` drains, refill it by pulling and decomposing the next `todo.md` item.
- **Flow:** `todo.md` (abstract horizons) → `queue.md` (concrete steps) → task tool (in-flight work) → `git log` (history). Items only ever flow forward; do not leave done items behind in `todo.md` or `queue.md`.
- **Session end condition:** the project's first session ends when `queue.md` is empty, the only items left in `todo.md` are still too abstract to break down further, and the repository is online with green CI. At that point, stop and hand back to the user.

## Testing
- **Write unit tests early.** As soon as there is testable logic, create a test file. Use `pytest` for Python projects or the appropriate test framework for the language in use.
- **Set up CI as soon as tests exist.** Create a `.github/workflows/ci.yml` GitHub Actions workflow that runs the test suite on push and pull request. Keep the workflow simple — install dependencies and run tests.
- **Keep tests passing.** Do not commit code that breaks existing tests. If a change requires updating tests, update them in the same commit.

## Project Description
_TODO: Describe what this project is about._

## Architecture and Conventions
_TODO: Document key decisions, file structure, and patterns as they emerge._

# currentDate
Today's date is {date}.
"""


def readme_md(project_name: str) -> str:
    return f"""# {project_name}

> Scaffolded with [cleanvibe](https://github.com/Immanuelle/cleanvibe).

## About

_TODO: Describe what this project does._

## Getting Started

This project was initialized with `cleanvibe new` and is intended to be developed
with AI-assisted coding via Claude Code.

```
cd {project_name}
claude
```
"""


def todo_md(project_name: str) -> str:
    return f"""# {project_name} — Long-Horizon Backlog

**This file is the long-term horizon of the project, not the current session.** `todo.md` holds multi-session goals, architectural ambitions, future capabilities — things we want to get to *eventually*. Items here are *abstract*: they describe a destination, not a step. Concrete, executable steps live in `queue.md`.

**Flow:**

```
todo.md  (abstract horizons)
   ↓  pick an item, decompose it
queue.md  (concrete executable steps)
   ↓  mirror into task tool, execute
git log  (done)
```

When work begins, the typical move is: pull an item from `todo.md`, break it into a small ordered set of concrete steps in `queue.md`, mirror those into the task tool, and execute. When the queue items are completed, delete the original `todo.md` item too (or replace it with a more specific follow-up that surfaced during the work).

**Session end condition:** the first session ends when `queue.md` is empty, the items remaining in `todo.md` are still too abstract to break down further, and the repository is online with green CI. At that point, stop and hand back.

See `CLAUDE.md` § "Queue and longer-horizon work" for how `todo.md`, `queue.md`, and the task tool stay in sync.

---

## Backlog

_(Populated during bootstrap from the user interview and the inferred project picture. Each item should be a sentence or short paragraph describing a goal or capability — not a checklist, not a step.)_
"""


def queue_md(project_name: str) -> str:
    return f"""# {project_name} — Work Queue

**This file is a queue of *concrete, executable steps*, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `git log`; longer-horizon, *abstract* work lives in `todo.md` and gets decomposed into items here when it's ready to execute. When an item is done, delete it — do not add checkmarks, "done" markers, or status indicators. If an item is still here, it is not done.

**Why this file exists:** when a planning step (formal planning mode or just "think before doing") produces a plan, that plan is written here BEFORE execution starts. That way an interrupted session can pick up from the queue rather than from chat context that may be gone.

The purpose of this file is also to bound scope. If a task is not in this queue, it is not in scope for the current session. New ideas go at the bottom of the queue (or to `todo.md` if they are longer-term / architectural), not silently into whatever is being worked on.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

---

## Active — First-session bootstrap

These items are the default opening sequence for a new cleanvibe project. Work them top to bottom. Delete each item from this file in the same commit that completes it. When this whole section is gone, the project has finished bootstrap and the queue is ready to be repopulated with real product work (see the final item).

1. **Triage user-supplied files into `data_lake/`.** Look at everything in the repo that isn't part of the cleanvibe scaffold (i.e. anything the user dropped in: notes, exports, spec PDFs, sample data, mockups, etc.).
   - Create a `data_lake/` directory and move all such files into it so the project root stays clean. Only the scaffold (`CLAUDE.md`, `README.md`, `queue.md`, `.gitignore`, `LICENSE`, and any source/config files you have explicitly chosen to keep at the root) should live at the top level.
   - If any of these files are `.zip` archives, extract them into `data_lake/` alongside the originals, then add the `.zip` files to `.gitignore` (we keep the extracted contents in git, not the archives).
   - For any file that looks big enough to need Git LFS (rough rule of thumb: >50 MB, or large binary like video/audio/large datasets), STOP and ask the user before doing anything — do not silently commit it, do not silently `git lfs track` it.
   - Commit. Commit message should describe what got moved/extracted and why.

2. **Read the data lake to infer what this project is.** Skim every file in `data_lake/` (text files, READMEs from extracted zips, design notes, spec docs, sample data shapes). Build up a working hypothesis: what is the user trying to build? What domain? What constraints or instructions are stated explicitly?
   - Update `README.md` to reflect this hypothesis: project description, any explicit instructions you found, anything load-bearing for future sessions.
   - Update `CLAUDE.md`'s "Project Description" and "Architecture and Conventions" sections to capture the same context for future Claude sessions.
   - Do NOT touch `queue.md` in this commit — the real queue gets written later, after talking to the user.
   - Commit. Commit message should briefly explain how the inferred description was derived (e.g. "Inferred project scope from data_lake/spec.md and data_lake/notes/").

3. **Interview the user about what they actually want to build.** Your inferred picture from the data lake is a starting point, not the spec. Ask the user direct, specific questions to fill in the gaps: what is the goal of the first usable version? What's the longer-term vision (capabilities, integrations, audience) beyond v1? What's in scope vs. out of scope for this session? Are there constraints (language, framework, deployment target, must-integrate-with-X)? What does "done" look like for them today?
   - As answers come in, fold them into `README.md` and `CLAUDE.md` so future sessions inherit the context.
   - Capture both **near-term** answers (what to build now) AND **long-horizon** answers (what's wanted eventually). The long-horizon material is what feeds `todo.md` in the next step.
   - Commit once the picture is concrete enough to plan against.

4. **Create `todo.md` — the long-horizon backlog.** This is the step before any concrete queue gets written. Based on the interview and inferred picture, write `todo.md` as the project's long-term horizon: every multi-session goal, architectural ambition, capability, integration, or future direction the user described. Items here are *abstract destinations*, not steps — they will be decomposed into concrete tasks in `queue.md` later, one at a time, as the work unfolds. `todo.md` is the *basis for* `queue.md`: work flows `todo.md` → `queue.md` → executed → deleted from both.
   - Use the convention described in `CLAUDE.md` § "Queue and longer-horizon work" for the file format.
   - Do NOT touch `queue.md` in this commit — populating the real queue is the *next* step.
   - Commit `todo.md` on its own so the long-horizon picture is a reviewable artifact, not buried inside a larger change.

5. **Replace this bootstrap queue with the real project queue.** Pull the first item (or first few items) from `todo.md` and decompose them into a concrete, ordered list of implementation tasks. Write those into the `## Active` section of this file (deleting this bootstrap section entirely as part of the same edit). Each task should be small enough to finish and commit on its own. Mirror the queue into the task tool. As you drain queue items, refill by pulling and decomposing more from `todo.md`.
   - Commit the new queue.

6. **Create a private GitHub repo and push.** Use whatever GitHub tooling is available (e.g. `gh repo create --private --source=. --push`) to create a private remote and push the current branch. Confirm CI (`.github/workflows/`) is wired up so pushes run tests.

7. **Work the queue until the stop condition.** Pull the top item, do it, delete it from `queue.md` in the same commit as the work, push, let CI run. When `queue.md` empties, refill from `todo.md` by decomposing the next item. New ideas that surface mid-work go to the bottom of the queue (or to `todo.md` if they're longer-horizon), not into the currently-in-flight task. **Stop** when: `queue.md` is empty, the items still in `todo.md` are too abstract to break down further without more user input, and the repository is online with green CI. At that point, hand back to the user.

---

## Pointers

- Long-horizon backlog (abstract goals, source of future queue items): `todo.md`.
- Narrative history: `git log`.
"""


RUNCLAUDE_BAT = """@echo off
cd /d "%~dp0"
claude
"""


GITIGNORE = """# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
*.egg
.eggs/

# Virtual environments
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
"""
