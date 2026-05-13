# cleanvibe — Long-Horizon Backlog

**This file is the long-term horizon of the project, not the current session.** `todo.md` holds multi-session goals, architectural ambitions, future capabilities — things we want to get to *eventually*. Items here are *abstract*: they describe a destination, not a step. Concrete, executable steps live in `queue.md`.

**Flow:**

```
todo.md  (abstract horizons)
   ↓  pick an item, decompose it
queue.md  (concrete executable steps)
   ↓  mirror into task tool, execute
git log  (done)
```

See `CLAUDE.md` § "Workflow Rules" for how `todo.md`, `queue.md`, and the task tool stay in sync.

---

## Backlog

- **Investigate the Carpathes / L-Carpathes agentic wiki idea and see whether it fits inside cleanvibe.** Look at what the Carpathes (a.k.a. L-Carpathes) agentic wiki concept is actually trying to do — how it models pages, agents, and edits — and decide whether cleanvibe should: (a) integrate with it directly, (b) ship a scaffold variant for projects that want this pattern, or (c) leave it alone. Output: a short design note in the repo with the recommendation and, if it's a fit, a follow-up `todo.md` entry describing the integration shape.

- **Make the bootstrap queue customizable.** Right now `queue_md()` ships one fixed bootstrap sequence. Eventually projects with different shapes (library vs. service vs. data pipeline vs. wiki bot) probably want different opening sequences. Explore whether this should be a `--profile` flag on `cleanvibe new`, a set of swappable template modules, or something else.

- **Extend `cleanvibe convert` to detect and adopt existing planning artifacts.** If a target repo already has a `TODO`, `BACKLOG.md`, `ROADMAP.md`, or similar, `convert` should recognize them and either rename/merge into `todo.md` or surface a prompt rather than silently injecting an empty one alongside.

- **Ship a `cleanvibe doctor` command.** A subcommand that audits a cleanvibe project for drift: queue.md items still present after commits that should have deleted them, todo.md items that look like they belong in queue.md (or vice versa), missing CI workflow, stale CLAUDE.md sections. Read-only by default, with `--fix` for the safe ones.

- **Publish 0.x → 1.0 stabilization.** Decide what the 1.0 contract is: which files are guaranteed to be injected, which template sections are stable, what `convert` promises never to overwrite, semver policy for template changes. Write it down in the README under "Stability" before tagging 1.0.

- **Add a feedback loop from real first-sessions back into the template.** As more projects are bootstrapped, the bootstrap queue should evolve based on what consistently goes well or poorly in step 1–7. Figure out a lightweight way to capture that (a "what bit you?" prompt at session end? a curated `BOOTSTRAP_LEARNINGS.md` in this repo?) without making the tool itself heavyweight.
