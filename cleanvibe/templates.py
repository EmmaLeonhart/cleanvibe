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
- **`todo.md`** — longer-horizon work that isn't ready for the active queue. Items migrate `todo.md` → `queue.md` → deleted on completion. Create `todo.md` when you have multi-session work to track.

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


def queue_md(project_name: str) -> str:
    return f"""# {project_name} — Work Queue

**This file is a queue, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `git log`; longer-horizon work lives in `todo.md`. When an item is done, delete it — do not add checkmarks, "done" markers, or status indicators. If an item is still here, it is not done.

**Why this file exists:** when a planning step (formal planning mode or just "think before doing") produces a plan, that plan is written here BEFORE execution starts. That way an interrupted session can pick up from the queue rather than from chat context that may be gone.

The purpose of this file is also to bound scope. If a task is not in this queue, it is not in scope for the current session. New ideas go at the bottom of the queue (or to `todo.md` if they are longer-term / architectural), not silently into whatever is being worked on.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

---

## Active

_(empty — add the first concrete task here when work begins)_

---

## Pointers

- Longer-horizon agenda: `todo.md` (create this file when multi-session work appears).
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
