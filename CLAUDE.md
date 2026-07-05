# cleanvibe

## ⚠️ Repo history — do NOT merge this branch; fork instead

This repo was originally the **cleanvibe framework/generator itself** (the Python
package that scaffolds other projects). This branch (`claude/cleanvibe-data-lake-p96t1s`)
threw all of that away and replaced it with a *fresh* `cleanvibe new` scaffold plus a
`data_lake/` — because forking the framework was the only convenient way to pull in the
skills in `.claude/skills/`. That's the "big fork for technical reasons" the work started
from; the framework content lives on in `git log` and on the `main` branch.

Consequences for future sessions:

- **Do NOT merge this branch into `main`.** `main` is still the real cleanvibe framework;
  merging would delete the generator. This branch is a *different project* that happens to
  share history.
- The right move is to **split this out into its own proper repository** (a real fork /
  new repo), then develop the data-lake project there with a clean history. Until that
  happens, treat this branch as a standalone project and keep working on it in place.
- Everything before the "Convert repo into a fresh cleanvibe project" commit
  (`b6fd9e2`) is framework history, not this project's history.

## Skills

Workflow behaviors live as skills in `.claude/skills/` (auto-discovered by Claude Code):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`writing-style`, `cleanvibe-update-check`. They are vendored into this repo and kept
current by the `cleanvibe-update-check` skill.

- **Last cleanvibe update check:** `never`
- **Updates source:** <https://cleanvibe.emmaleonhart.com/updates.md>

## Project Description
_TODO: Describe what this project is about._

## Architecture and Conventions
_TODO: Document key decisions, file structure, and patterns as they emerge._

## Long command series run in strict order
When the user gives a long series of commands, treat it as a long series of commands to be
executed in relatively STRICT ORDER, one after another, EVEN IF the order seems not to make
sense or seems inefficient. The sequencing is intentional — the user organizes the steps so
states change in the order they want. Do not reorder, merge, or skip steps.

## Not-done taxonomy (never "deliberately deferred")
When work is NOT done, tag it with exactly ONE of: **NEEDS-DECISION** (name the decision +
who decides), **BLOCKED-ON-USER-ACTION** (a real-world action only the user can take — name
it), **BLOCKED-ON-EXTERNAL** (CI / a remote / a third party / another session's unpushed
commit — name it + the unblock signal), **NEEDS-INVESTIGATION** (not understood yet — a
to-do for the next tick, never a resting place), **UNSAFE-TO-GUESS** (could cause damage —
name the risk + what makes it safe), or **OUT-OF-SCOPE** (another repo's job — name it).
LOAD-BEARING DEFAULT: if it fits none of these with a specifically-named blocker, it is NOT
deferred — DO IT NOW. Bare "deliberately not done" / "blocked on <person>" is banned.

# currentDate
Today's date is 2026-07-05.
