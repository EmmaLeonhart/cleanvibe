# CleanVibe Skill Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the duplicated CLAUDE.md workflow/cron/emergency/writing prose into six standalone skills, ship them from a single source (`cleanvibe/skills.py`) into `~/.claude/skills/` and every cleanvibe repo, and trim every CLAUDE.md to a pointer.

**Architecture:** `cleanvibe/cleanvibe/skills.py` holds the six `SKILL.md` bodies as string constants (mirrors the `templates.py` pattern; zero package-data). `write_skills(dest_root)` materializes them to `dest_root/.claude/skills/<slug>/SKILL.md`. Scaffold modes call it; a migration script back-fills existing repos after a sync-and-trim.

**Tech Stack:** Python 3.9+ stdlib (pathlib, subprocess), pytest, git/gh CLI.

---

## File Structure

- Create: `cleanvibe/cleanvibe/skills.py` — `SKILLS` dict + `write_skills()`.
- Modify: `cleanvibe/cleanvibe/scaffold.py` — call `write_skills()` in all modes.
- Modify: `cleanvibe/cleanvibe/templates.py` — replace blocks with `## Skills` pointer.
- Modify: `cleanvibe/cleanvibe/__init__.py`, `pyproject.toml` — version 1.14.0.
- Create: `cleanvibe/tests/test_skills.py` — skills unit tests.
- Modify: `cleanvibe/tests/` existing CLAUDE.md-shape tests.
- Modify: `cleanvibe/pages/updates.md`, `cleanvibe/devlog.md`, `cleanvibe/README.md`.
- Create: `cleanvibe/migrate_repos_to_skills.py` — repo back-fill script.
- Modify: `~/.claude/CLAUDE.md` (trim) + create `~/.claude/skills/` (Stage B).

---

## Task 1: Author `skills.py` (the single source of truth)

**Files:**
- Create: `cleanvibe/cleanvibe/skills.py`
- Test: `cleanvibe/tests/test_skills.py`

- [ ] **Step 1: Write the failing test**

```python
# cleanvibe/tests/test_skills.py
import re
import unittest
from pathlib import Path
import tempfile

from cleanvibe import skills

EXPECTED = {
    "emergency-stop", "cron-is-local", "autonomous-loop",
    "queue-driven-workflow", "writing-style", "cleanvibe-update-check",
}
FM = re.compile(r"^---\nname: (?P<name>[a-z-]+)\ndescription: (?P<desc>.+?)\n---\n", re.S)


class TestSkills(unittest.TestCase):
    def test_all_six_present(self):
        self.assertEqual(set(skills.SKILLS), EXPECTED)

    def test_frontmatter_valid_and_matches_slug(self):
        for slug, body in skills.SKILLS.items():
            m = FM.match(body)
            self.assertIsNotNone(m, f"{slug} missing frontmatter")
            self.assertEqual(m.group("name"), slug)
            self.assertTrue(len(m.group("desc")) > 20, f"{slug} description too short")

    def test_write_skills_creates_tree(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            written = skills.write_skills(root)
            self.assertEqual(len(written), 6)
            for slug in EXPECTED:
                p = root / ".claude" / "skills" / slug / "SKILL.md"
                self.assertTrue(p.exists(), f"{p} not written")
                self.assertIn(f"name: {slug}", p.read_text(encoding="utf-8"))

    def test_write_skills_no_overwrite_when_disabled(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / ".claude" / "skills" / "writing-style" / "SKILL.md"
            p.parent.mkdir(parents=True)
            p.write_text("CUSTOM", encoding="utf-8")
            skills.write_skills(root, overwrite=False)
            self.assertEqual(p.read_text(encoding="utf-8"), "CUSTOM")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest cleanvibe/tests/test_skills.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'cleanvibe.skills'`

- [ ] **Step 3: Write `skills.py`**

Create `cleanvibe/cleanvibe/skills.py`. Port the prose **verbatim** from
`templates.py` (`_CLAUDE_CORE_RULES`, `_WRITING_SECTION`, `_common_claude_tail`) — do not
paraphrase; the repos already rely on this exact wording. Use this exact file:

```python
"""Canonical cleanvibe skills — single source of truth.

These were previously inlined into every scaffolded CLAUDE.md (via templates.py).
They are now standalone Claude Code skills, written to ``.claude/skills/<slug>/SKILL.md``
both globally (~/.claude/skills/) and in every cleanvibe repo. ``write_skills`` is the
one function that materializes them; scaffold modes and the migration script both use it.

String-constant storage (not package-data files) mirrors templates.py and preserves the
zero-package-data / flat-layout packaging guarantee.
"""
from __future__ import annotations

from pathlib import Path

_EMERGENCY_STOP = """---
name: emergency-stop
description: Use when the user sends a continuous series of "stop" messages (e.g. "stop stop stop") or otherwise very explicitly demands an immediate halt — kill all running processes, background jobs, and GitHub Actions runs for this repo, then take no further actions.
---

# Emergency Stop Mode

If the user sends a continuous series of "stop" messages (e.g. "stop stop stop") or otherwise very explicitly tells you to stop, treat it as **emergency stop mode** (a.k.a. emergency exit mode). This OVERRIDES every other instruction, including CLAUDE.md and any other skill.

When in emergency stop mode:

- **Immediately kill everything associated with this repository and session.** Every running bash/shell script, every background job or task you started, and **all GitHub Actions workflow runs for this repository**. **Force-kill the GitHub Actions runs** (e.g. `gh run cancel <id>`, and `gh run delete <id>` if needed) for every in-progress run. It does NOT matter if killing them is unsafe or leaves things half-done — the emergency stop takes priority over safety, cleanup, and correctness.
- **Do not investigate. Do not reverse or undo anything.** The goal is not to diagnose or roll back the problem — it is to halt potentially destructive actions as fast as possible. Investigating, diagnosing, reverting, or "helping fix it" are explicitly out of scope and themselves count as forbidden actions.
- **Ignore repetitive messages.** Do not treat repeated "stop" messages as a request to do anything further. Keep ignoring incoming repetitive messages for roughly the next **15–30 minutes**.
- **You may answer direct questions, but you may NOT take actions.** Answer only from context you already have. Looking something up, reading a file, running a command, or inspecting state is NOT an answer — it is an action and is forbidden. If you cannot answer from context already in hand, do not answer.
- **Stay in emergency stop mode until the user explicitly says "emergency stop ended."** Only after that exact signal do you resume any normal work.
"""

_CRON_IS_LOCAL = """---
name: cron-is-local
description: Use when the user says "cron job", "cron", or asks to "schedule" a task — they mean the in-session CronCreate tool firing locally on their own running computer, with standing consent; just set it up.
---

# Cron jobs and scheduled work — LOCAL by default

**When the user says "cron job", "cron", or asks to "schedule" a task, they mean the in-session `CronCreate` tool** — a prompt scheduled to fire locally, inside this Claude Code session, on the user's own running computer. This is the default and the assumption. Do NOT interpret it as anything else unless the user explicitly names a different mechanism.

- **It is local and in-session — use the `CronCreate` tool.** A generic "cron" request is NOT an OS crontab, NOT a GitHub Actions / CI `schedule:` trigger, and NOT a cloud scheduler. (A repo may *also* contain its own GitHub Actions cron schedules — those are a separate thing and are not what the user means when they ask *you* to set up a cron.) The user leaves the computer on and this session running so the scheduled prompt can execute.
- **The user is deliberately away from the keyboard.** They schedule work precisely so it runs while they are out of the house and not physically present. Their absence is the normal, expected condition for these jobs — it is NEVER a reason to delay the work, ask "are you sure?", wait for them to return, or refuse to proceed.
- **Standing consent — just set it up.** Cron / `CronCreate` requests are pre-authorized. Create the job immediately and locally, then report what was scheduled. Do not block on confirmation or follow-up questions.
"""

_AUTONOMOUS_LOOP = """---
name: autonomous-loop
description: Use when starting any session of relatively extensive or large-scale autonomous work — above all any large-scale population of queue.md with created tasks — to run the three local-cron productivity playbook (work-loop, auto-flush, status-report).
---

# Autonomous productivity loop — the three-cron playbook

**For any session involving relatively extensive work — above all, any large-scale population of `queue.md` with created tasks — this is the default way of working.** It is three local `CronCreate` jobs that turn "barrel through `queue.md`, and when it's empty atomise the next `todo.md` item into it" into a self-sustaining hourly cadence with a commit/push backstop and a heartbeat. The crons are **session-local** (`durable: false` — they die when the session ends), so they are recreated at the start of every session.

Stagger the minutes so the three ticks don't collide:

1. **Work-loop cron — `3 * * * *` (hourly at :03).** The engine. Each tick does, in order:
   - **(a) SYNC** — `git fetch origin`; fast-forward or rebase the working branch (never force-push, never `reset --hard`, never discard a sibling machine's work).
   - **(b) WORK** — take the top actionable item from `queue.md` and do it. If nothing in `queue.md` is actionable (all blocked / needs user / a product decision), promote the next *genuinely-unblocked, bounded, verifiable* `todo.md` item — **plan it into `queue.md` first**, mirror to the task tool, then execute.
   - **(c) HARD RAILS** — never fake; never weaken / skip / delete a test to make it pass; never claim "works" / "verified" / "passes" without having actually RUN it and measured. A real defect → strict `xfail` or a precise documented blocker, never a loosened assertion. Don't implement what you don't 100% understand — write the spec / queue item instead. Name unbuilt or hard things plainly; don't paper over difficulty. Verify CI green, not just local — local-green does not imply CI-green.
   - **(d) COMMIT** — commit early/often with *why*; update `queue.md` in the same commit (delete completed items); append the dated entry to `devlog.md`; mark task-tool items done; push.
   - **(e) REPORT** — one line: the commit shas advanced, or `nothing actionable; <reason>`.

2. **Auto-flush cron — `15 * * * *` (hourly at :15).** The backstop. Commit + push all pending work so nothing sits uncommitted between manual pushes; report shas or "nothing pending". Only commit / push when something is actually pending — no empty commits.

3. **Status-report cron — `42 * * * *` (hourly at :42).** The heartbeat — **reporting only, no code changes.** Covers: what advanced since the last report (shas + one-line each); current `queue.md` state; how the work held the hard rails (and any place it brushed one); blockers, each tagged with exactly one of the disjoint not-done taxonomy — NEEDS-DECISION / BLOCKED-ON-USER-ACTION / BLOCKED-ON-EXTERNAL / NEEDS-INVESTIGATION / UNSAFE-TO-GUESS / OUT-OF-SCOPE — naming the specific decision / user-action / external signal / risk / owner (LOAD-BEARING DEFAULT: if a not-done item fits none of these with a specifically-named blocker, it is NOT deferred — DO IT NOW); test-suite health.

**Why this exists:** the most common autonomous-agent failure is doing a large amount of work and silently losing the thread of what it is doing. The work-loop forces steady, verifiable, committed progress; the auto-flush guarantees nothing is lost between ticks; the status-report keeps the thread legible.

**Lifecycle around a large-scale queue fill:**

- **(a) START all three crons at the beginning of any extensive work session.** A fresh session has none of them running, so the opening move — the first queue item — is to *create them*.
- **(b) On a mid-session large-scale queue RE-FILL** (a planning burst that repopulates the queue), the FIRST item of that fill **kills the running crons**, then the work items follow top to bottom, and the pinned tail restarts them.
- **(c) Entering planning mode DISABLES the crons.** Their restart therefore lives at the **end** of the queue, not the beginning of the next burst.
- **(d) The LAST TWO queue items, always kept pinned at the tail, are:**
  1. **Ensure the three crons are running** — start them if this session never did, restart them if a planning burst / queue re-fill killed them.
  2. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

In short: a fresh session **starts** the crons up front and the tail **ensures they are still running** + summarizes; a mid-session re-fill **kills** them up front and the tail **restarts** them + summarizes. Either way the queue both opens and closes on the cron set.

**Replication projects are exempt.** This is for `new` / general extensive work only — a bounded paper replication does not get the hourly heartbeat.
"""

_QUEUE_DRIVEN_WORKFLOW = """---
name: queue-driven-workflow
description: Use when doing any multi-step or planning work in a cleanvibe-scaffolded project — enforces plan-into-queue.md-first, the todo.md→queue.md→devlog.md flow, delete-don't-check completion, task-tool mirroring, and tests/CI discipline.
---

# Queue-driven workflow

## Workflow Rules
- **Commit early and often.** Every meaningful change gets a commit with a clear message explaining *why*, not just what.
- **Plan into `queue.md` first, then execute.** When entering planning mode (or doing any non-trivial multi-step work), the FIRST action is to write the plan into `queue.md` as concrete items. Only then begin executing. This means an interrupted session can resume from the queue — the plan does not live only in chat context.
- **Finishing an item = delete from `queue.md` + append to `devlog.md`, then commit and push.** IMPORTANT: when a queue item is done, **delete the item from `queue.md`** and **append a dated entry to `devlog.md`** recording what was completed, in the *same commit as the work*, then push. NEVER mark an item done in place (no `[x]`, no "✓", no "DONE" — a checked box left in `queue.md` is the failure mode this rule exists to prevent). `queue.md` only ever holds not-yet-done work; `devlog.md` is where "done" lives.
- **Mirror `queue.md` into the task tool.** TaskCreate items as you add them to queue.md; mark `in_progress` when starting; `completed` when done. The two views must not drift.
- **Keep CLAUDE.md up to date.** As the project takes shape, record architectural decisions, conventions, and anything needed to work effectively in this repo.
- **Update README.md regularly.** It should always reflect the current state of the project for human readers.

## Queue and longer-horizon work
- **`queue.md`** — what's being worked on right now. Items get deleted on completion; do not leave checkmarks or status indicators behind. If it's not in `queue.md`, it's not in scope for the current session.
- **`todo.md`** — the **long-term horizon** of the project. Multi-session goals, architectural ambitions, future capabilities. Items in `todo.md` are *abstract*: they describe a destination, not a step. `todo.md` is the *basis for* `queue.md`: when work begins, an item is pulled from `todo.md`, decomposed into concrete executable steps in `queue.md`, mirrored into the task tool, and executed. As `queue.md` drains, refill it by pulling and decomposing the next `todo.md` item.
- **`devlog.md`** — where **"done" lives**. Every queue item that is finished gets deleted from `queue.md` and appended as a dated entry here, in the same commit as the work. Releases (tag + one-line note) and notable milestones also go here. `devlog.md` exists so `queue.md` can stay strictly delete-only without losing the historical trail.
- **Flow:** `todo.md` (abstract horizons) → `queue.md` (concrete steps) → task tool (in-flight work) → `devlog.md` + `git log` (history). Items only ever flow forward; do not leave done items behind in `todo.md` or `queue.md`.
- **Session end condition:** the project's first session ends when `queue.md` is empty, the only items left in `todo.md` are still too abstract to break down further, and the repository is online with green CI. At that point, stop and hand back to the user.

## Testing
- **Write unit tests early.** As soon as there is testable logic, create a test file. Use `pytest` for Python projects or the appropriate test framework for the language in use.
- **Set up CI as soon as tests exist.** Create a `.github/workflows/ci.yml` GitHub Actions workflow that runs the test suite on push and pull request. Keep the workflow simple — install dependencies and run tests.
- **Keep tests passing.** Do not commit code that breaks existing tests. If a change requires updating tests, update them in the same commit.
"""

_WRITING_STYLE = """---
name: writing-style
description: Use when writing any prose — reports, commit messages, devlog entries, PR descriptions, documentation — to avoid the self-congratulatory "honest"/"frank"/"candid"/"transparent" move and name failures flatly instead.
---

# Writing style

Do not use "honest", "honesty", or "honestly" — and do not swap in "frank", "frankly", "candid", "candidly", or "transparently", which are the same self-congratulatory move in a different coat. When something failed, name the failure: "it didn't work", "I got that wrong", "this failed" — flat, no qualifier. Tagging a report "honest" implies the rest aren't, and couching a failure as honesty asks for credit for the admission, which is worse than the failure itself. Use a precise positive word ("accurate", "plainly", "truly") only when that is genuinely the meaning — never as a halo on a bad outcome.
"""

_CLEANVIBE_UPDATE_CHECK = """---
name: cleanvibe-update-check
description: Use at the start of a session in a cleanvibe-scaffolded project, at most weekly — fetch cleanvibe's updates page and refresh this repo's .claude/skills/ to the latest shipped versions.
---

# Check cleanvibe for skill updates (weekly)

This repo's `.claude/skills/` were vendored by **cleanvibe**. cleanvibe ships new and revised skills over time — when one lands, every cleanvibe-scaffolded project should pick it up.

**The check is weekly, not per-session.** At the top of a session, look at the *last cleanvibe update check* date recorded in this repo's CLAUDE.md `## Skills` section. If it has been more than 7 days:

1. **Fetch the current skill index** — `WebFetch https://cleanvibe.emmaleonhart.com/updates.md`. This is the canonical, hand-maintained page describing every skill cleanvibe ships, keyed by the cleanvibe version that introduced or revised it.
2. **Compare against the skills currently in `.claude/skills/`.** If the page lists newer skills or revisions, update the corresponding `.claude/skills/<slug>/SKILL.md` files to match. Match the wording from `updates.md`; don't paraphrase.
3. **Update the last-check date** in CLAUDE.md's `## Skills` section. Commit with a message describing which skills were refreshed.

If the fetch fails (offline, DNS, page not yet up), leave the date alone and try next session — the check is opportunistic, not mandatory.
"""

SKILLS = {
    "emergency-stop": _EMERGENCY_STOP,
    "cron-is-local": _CRON_IS_LOCAL,
    "autonomous-loop": _AUTONOMOUS_LOOP,
    "queue-driven-workflow": _QUEUE_DRIVEN_WORKFLOW,
    "writing-style": _WRITING_STYLE,
    "cleanvibe-update-check": _CLEANVIBE_UPDATE_CHECK,
}


def write_skills(dest_root, *, overwrite: bool = True) -> list:
    """Write every skill to ``dest_root/.claude/skills/<slug>/SKILL.md``.

    Returns the list of Paths written. With ``overwrite=False`` an existing
    SKILL.md is left untouched (used by non-destructive scaffold paths).
    """
    dest_root = Path(dest_root)
    written = []
    for slug, body in SKILLS.items():
        target = dest_root / ".claude" / "skills" / slug / "SKILL.md"
        if target.exists() and not overwrite:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        written.append(target)
    return written
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest cleanvibe/tests/test_skills.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
cd cleanvibe
git add cleanvibe/skills.py tests/test_skills.py
git commit -m "feat: add skills.py — six vendored skills + write_skills()"
```

---

## Task 2: Add the `## Skills` pointer to templates and wire scaffold

**Files:**
- Modify: `cleanvibe/cleanvibe/templates.py` (`claude_md`, `research_claude_md`, shared helpers)
- Modify: `cleanvibe/cleanvibe/scaffold.py` (`create_project`, `_inject_scaffold`, `clone_project`)

- [ ] **Step 1: Add the pointer constant to `templates.py`**

Add near the other shared constants:

```python
SKILLS_POINTER = """## Skills

Workflow behaviors live as skills in `.claude/skills/` (auto-discovered by Claude Code):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`writing-style`, `cleanvibe-update-check`. They are vendored into this repo and kept
current by the `cleanvibe-update-check` skill.

- **Last cleanvibe update check:** `never`
- **Updates source:** <https://cleanvibe.emmaleonhart.com/updates.md>"""
```

- [ ] **Step 2: Replace the inlined blocks in `claude_md()`**

In `templates.py`, change `claude_md()` (and `research_claude_md()` if it inlines the
same helpers) so the generated CLAUDE.md no longer contains `_CLAUDE_CORE_RULES`,
`_WRITING_SECTION`, or `_common_claude_tail`'s workflow/cron/emergency prose. Replace with
`SKILLS_POINTER`. Keep the `# currentDate` footer. New `claude_md()`:

```python
def claude_md(project_name: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    return f"""# {project_name}

{SKILLS_POINTER}

## Project Description
_TODO: Describe what this project is about._

## Architecture and Conventions
_TODO: Document key decisions, file structure, and patterns as they emerge._

# currentDate
Today's date is {date}.
"""
```

Apply the equivalent edit to `research_claude_md()` (replace the `_CLAUDE_CORE_RULES` /
`_WRITING_SECTION` / `_common_claude_tail` interpolations with `SKILLS_POINTER`, keep the
research-specific sections and the date footer). Leave `_common_claude_tail` /
`_CLAUDE_CORE_RULES` / `_WRITING_SECTION` defined for now (removed in Task 4 after tests
are updated) to avoid breaking imports mid-change.

- [ ] **Step 3: Call `write_skills()` from every scaffold mode**

In `scaffold.py`, add `from cleanvibe import skills` at the top. Then:

In `create_project()` after `_write(path / "CLAUDE.md", ...)` (line ~40), add:
```python
    skills.write_skills(path)
```
Add a dry-run line in the `if dry_run:` block:
```python
        print(f"[dry-run] Would write: {path / '.claude' / 'skills'} (6 skills)")
```

In `_inject_scaffold()` (used by `convert`), after the CLAUDE.md injection block, add a
non-destructive write:
```python
    if not (path / ".claude" / "skills").exists():
        skills.write_skills(path, overwrite=False)
        print("  Injected .claude/skills/ (was missing)")
```

In `clone_project()`, after the onboarding CLAUDE.md is written, add:
```python
    skills.write_skills(path, overwrite=False)
```
(plus a matching dry-run print). The replication modes live in `replicate.py`/templates —
add `skills.write_skills(project_root, overwrite=False)` at the end of each
`replicate_*_project` scaffold, after the framework files are written but before the git
commit, so the skills are part of commit 1.

- [ ] **Step 4: Run the existing scaffold tests to see what breaks**

Run: `python -m pytest cleanvibe/tests/ -v`
Expected: FAILs in any test asserting old CLAUDE.md text (e.g. "Emergency Stop",
"three-cron", "honest"). Note them for Task 3.

- [ ] **Step 5: Commit**

```bash
cd cleanvibe
git add cleanvibe/templates.py cleanvibe/scaffold.py
git commit -m "feat: scaffold writes .claude/skills/; CLAUDE.md trimmed to pointer"
```

---

## Task 3: Update scaffold tests for the new shape

**Files:**
- Modify: existing test files under `cleanvibe/tests/` that assert CLAUDE.md content.

- [ ] **Step 1: Find the assertions on old prose**

Run: `python -m pytest cleanvibe/tests/ -v` and also
`grep -rn "Emergency Stop\|three-cron\|honest\|Workflow Rules\|CronCreate" cleanvibe/tests/`

- [ ] **Step 2: Rewrite those assertions**

For each failing test that checked old CLAUDE.md prose, change it to assert the new
reality: CLAUDE.md contains `## Skills` and the slug list; the scaffolded tree contains
`.claude/skills/emergency-stop/SKILL.md` etc. Example replacement:

```python
def test_scaffold_writes_skills(tmp_path):
    create_project(tmp_path / "proj", no_claude=True)
    proj = tmp_path / "proj"
    assert (proj / ".claude" / "skills" / "emergency-stop" / "SKILL.md").exists()
    claude = (proj / "CLAUDE.md").read_text(encoding="utf-8")
    assert "## Skills" in claude
    assert "Emergency Stop Mode" not in claude  # moved out to the skill
```

- [ ] **Step 3: Run the full suite**

Run: `python -m pytest cleanvibe/tests/ -v`
Expected: all green.

- [ ] **Step 4: Commit**

```bash
cd cleanvibe
git add cleanvibe/tests/
git commit -m "test: assert new CLAUDE.md pointer + .claude/skills/ scaffold shape"
```

---

## Task 4: Remove now-dead template helpers + cut release 1.14.0

**Files:**
- Modify: `cleanvibe/cleanvibe/templates.py` (delete dead helpers if unused)
- Modify: `cleanvibe/cleanvibe/__init__.py`, `cleanvibe/pyproject.toml`
- Modify: `cleanvibe/pages/updates.md`, `cleanvibe/devlog.md`, `cleanvibe/README.md`, `cleanvibe/CLAUDE.md`

- [ ] **Step 1: Delete dead helpers (only if no longer referenced)**

Run: `grep -rn "_CLAUDE_CORE_RULES\|_WRITING_SECTION\|_common_claude_tail" cleanvibe/cleanvibe/`
If only their definitions remain (no callers), delete the three definitions from
`templates.py`. If any caller remains, leave them and note it. Run tests after:
`python -m pytest cleanvibe/tests/ -v` → green.

- [ ] **Step 2: Bump version to 1.14.0**

Edit `cleanvibe/cleanvibe/__init__.py`: `__version__ = "1.14.0"`.
Edit `cleanvibe/pyproject.toml`: `version = "1.14.0"`.

- [ ] **Step 3: Document the release**

- `pages/updates.md`: add a v1.14.0 section listing the six skills (slug + one-line
  description each) — this is the page `cleanvibe-update-check` fetches, so it must
  describe each shipped skill.
- `devlog.md`: add a dated `2026-05-30` entry + `v1.14.0` release note.
- `README.md`: add a short "Skills" subsection explaining that scaffolded repos get
  `.claude/skills/` and CLAUDE.md is a pointer.
- `cleanvibe/CLAUDE.md` (this repo's own): replace its Emergency Stop / Cron / Writing /
  Workflow Rules blocks with the `## Skills` pointer, and run `skills.write_skills(".")`
  so cleanvibe itself dogfoods its own `.claude/skills/`.

- [ ] **Step 4: Full suite + commit**

Run: `python -m pytest cleanvibe/tests/ -v` → green.
```bash
cd cleanvibe
git add -A
git commit -m "release: v1.14.0 — skill distribution; trim cleanvibe's own CLAUDE.md"
git push
```

---

## Task 5: Install globally + trim `~/.claude/CLAUDE.md`

**Files:**
- Create: `~/.claude/skills/<slug>/SKILL.md` (6)
- Modify: `C:\\Users\\Immanuelle\\.claude\\CLAUDE.md`

- [ ] **Step 1: Write the global skills from the single source**

Run:
```bash
cd "C:\\Users\\Immanuelle\\Documents\\Github\\cleanvibe"
python -c "from pathlib import Path; from cleanvibe import skills; print(skills.write_skills(Path.home()))"
```
Note: `write_skills` itself appends `.claude/skills`, so pass `Path.home()` (NOT
`Path.home()/'.claude'`, which would nest to `~/.claude/.claude/skills`).
Expected: prints six paths under `~/.claude/skills/`.

- [ ] **Step 2: Verify discovery shape**

Confirm `~/.claude/skills/emergency-stop/SKILL.md` exists and starts with `---\nname: emergency-stop`.

- [ ] **Step 3: Trim the global CLAUDE.md**

In `C:\\Users\\Immanuelle\\.claude\\CLAUDE.md`, remove the blocks now covered by skills —
**Emergency Stop Mode**, **Cron jobs … LOCAL by default**, the three-cron / hourly
status-report playbook, **Wiki Editing Best Practices**' generic workflow overlap is
project-specific so KEEP it, and the "honest" writing rule if present. Replace the removed
behavioral blocks with:

```markdown
## Skills (global)
Workflow behaviors live as skills in `~/.claude/skills/` (auto-discovered):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`writing-style`, `cleanvibe-update-check`.
```

**KEEP everything project-specific:** the Wikidata Integration tasks, Aelaki Wikibase
Lexeme API notes, Python interpreter paths, and Gaiad project structure. Only the
generic, now-skill-covered behavioral prose leaves.

- [ ] **Step 4: Commit (the global ~/.claude is not necessarily a git repo)**

If `~/.claude` is a git repo, commit. Otherwise, no commit needed — just confirm the file
is saved and report the before/after line count.

---

## Task 6: Migration script for existing repos

**Files:**
- Create: `cleanvibe/migrate_repos_to_skills.py`

- [ ] **Step 1: Write the failing test (fixture repo)**

```python
# cleanvibe/tests/test_migrate.py
import subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "migrate_repos_to_skills.py"

OLD_CLAUDE = """# demo

## Emergency Stop Mode
stop stop stop blah blah three-cron LOCAL by default

## Writing
do not say honest

## Project Description
real project stuff
"""

class TestMigrate(unittest.TestCase):
    def test_dry_run_detects_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            repo = root / "demo"
            repo.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True,
                           capture_output=True)
            (repo / "CLAUDE.md").write_text(OLD_CLAUDE, encoding="utf-8")
            out = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--dry-run"],
                capture_output=True, text=True)
            self.assertIn("demo", out.stdout)
            # dry-run must not create skills
            self.assertFalse((repo / ".claude" / "skills").exists())

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest cleanvibe/tests/test_migrate.py -v`
Expected: FAIL — script does not exist.

- [ ] **Step 3: Write `migrate_repos_to_skills.py`**

```python
"""Back-fill cleanvibe skills into existing repos and trim their CLAUDE.md.

For each git repo under --root whose CLAUDE.md contains the old inlined workflow
blocks: sync (fetch + ff-only), write .claude/skills/, trim CLAUDE.md to a pointer,
commit, and push. Dirty or diverged repos are skipped and reported. --dry-run (default)
only reports; --apply performs the changes.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cleanvibe import skills  # noqa: E402

MARKERS = ("Emergency Stop Mode", "three-cron", "LOCAL by default", "CronCreate")

POINTER = """## Skills

Workflow behaviors live as skills in `.claude/skills/` (auto-discovered by Claude Code):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`writing-style`, `cleanvibe-update-check`. Vendored here; kept current by the
`cleanvibe-update-check` skill.
"""


def _git(repo: Path, *args, check=True):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=check)


def _has_markers(claude: Path) -> bool:
    if not claude.exists():
        return False
    text = claude.read_text(encoding="utf-8", errors="replace")
    return sum(m in text for m in MARKERS) >= 2


def _trim_claude(text: str) -> str:
    """Drop the known behavioral sections, prepend the pointer once.

    Splits on top-level (## / #) headings and removes sections whose heading
    matches a known skill-covered block; keeps everything else verbatim.
    """
    drop_headings = (
        "Emergency Stop Mode", "Cron jobs and scheduled work",
        "Autonomous productivity loop", "Hourly status-report cron",
        "Check cleanvibe for skill updates", "Workflow Rules",
        "Queue and longer-horizon work", "Writing", "Testing",
    )
    lines = text.splitlines(keepends=True)
    out, skipping = [], False
    for ln in lines:
        stripped = ln.lstrip("#").strip()
        is_heading = ln.lstrip().startswith("#")
        if is_heading:
            skipping = any(stripped.startswith(h) for h in drop_headings)
        if not skipping:
            out.append(ln)
    body = "".join(out).rstrip() + "\n"
    if "## Skills" not in body:
        # insert pointer after the first H1 if present, else at top
        if body.startswith("# "):
            first_nl = body.index("\n") + 1
            body = body[:first_nl] + "\n" + POINTER + "\n" + body[first_nl:]
        else:
            body = POINTER + "\n" + body
    return body


def find_repos(root: Path):
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if not (child / ".git").exists():
            continue
        if _has_markers(child / "CLAUDE.md"):
            yield child


def migrate(repo: Path, apply: bool) -> str:
    name = repo.name
    # clean tree?
    status = _git(repo, "status", "--porcelain", check=False).stdout.strip()
    if status:
        return f"SKIP {name}: dirty working tree"
    fetched = _git(repo, "fetch", "origin", check=False)
    if fetched.returncode != 0:
        return f"SKIP {name}: git fetch failed ({fetched.stderr.strip()[:80]})"
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD", check=False).stdout.strip()
    upstream = _git(repo, "rev-parse", "--abbrev-ref", "@{u}", check=False)
    if upstream.returncode == 0:
        counts = _git(repo, "rev-list", "--left-right", "--count",
                      "HEAD...@{u}", check=False).stdout.split()
        if len(counts) == 2 and counts[1] != "0" and counts[0] != "0":
            return f"SKIP {name}: diverged from upstream"
        if len(counts) == 2 and counts[1] != "0":
            ff = _git(repo, "merge", "--ff-only", "@{u}", check=False)
            if ff.returncode != 0:
                return f"SKIP {name}: not fast-forwardable"
    if not apply:
        return f"WOULD MIGRATE {name} (branch {branch})"
    skills.write_skills(repo)
    claude = repo / "CLAUDE.md"
    claude.write_text(_trim_claude(claude.read_text(encoding="utf-8")), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m",
         "chore: vendor cleanvibe skills into .claude/skills; trim CLAUDE.md to pointer")
    pushed = _git(repo, "push", check=False)
    if pushed.returncode != 0:
        return f"COMMITTED {name} but PUSH FAILED ({pushed.stderr.strip()[:80]})"
    return f"MIGRATED+PUSHED {name}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.home() / "Documents" / "Github"))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    apply = args.apply and not args.dry_run
    root = Path(args.root)
    results = []
    for repo in find_repos(root):
        results.append(migrate(repo, apply))
    print(f"\n=== cleanvibe skill migration ({'APPLY' if apply else 'DRY-RUN'}) ===")
    for r in results:
        print(" ", r)
    print(f"\n{len(results)} repo(s) with old blocks detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test**

Run: `python -m pytest cleanvibe/tests/test_migrate.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd cleanvibe
git add migrate_repos_to_skills.py tests/test_migrate.py
git commit -m "feat: migrate_repos_to_skills.py — back-fill skills into existing repos"
git push
```

---

## Task 7: Run the migration across all repos

- [ ] **Step 1: Dry-run and review**

Run:
```bash
cd "C:\\Users\\Immanuelle\\Documents\\Github\\cleanvibe"
python migrate_repos_to_skills.py --dry-run
```
Read the list. Confirm it only names repos that actually have the old blocks, and that the
cleanvibe repo itself is handled (already done in Task 4 — it should report clean or be
skipped as already-migrated since markers were removed).

- [ ] **Step 2: Apply**

Run:
```bash
python migrate_repos_to_skills.py --apply
```
Expected: each clean/in-sync repo → `MIGRATED+PUSHED`; dirty/diverged → `SKIP` with
reason; any push failures surfaced explicitly.

- [ ] **Step 3: Report**

Summarize migrated / skipped / failed. For each SKIP, state why (dirty / diverged / no
upstream). Hand the skipped list back to the user for manual handling.

---

## Self-Review notes (done by plan author)

- **Spec coverage:** Stage A → Task 1; Stage B → Task 5; Stage C → Tasks 2–4; Stage D →
  Tasks 6–7. Six skills, slug set identical across `skills.py`, pointer text, migration
  markers, and tests. ✓
- **`cleanvibe-update-check` redefinition** (refresh `.claude/skills/`, not CLAUDE.md) is
  reflected in the skill body (Task 1) and `updates.md` (Task 4). ✓
- **Sync-before-edit / skip-dirty-or-diverged / push** all implemented in `migrate()`. ✓
- **Non-destructive paths** (`convert`/`clone`/`replicate`) use `overwrite=False`. ✓
- **No placeholders:** every code step shows full code. ✓
