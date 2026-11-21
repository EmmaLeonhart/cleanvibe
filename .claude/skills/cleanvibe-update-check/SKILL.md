---
name: cleanvibe-update-check
description: Use at the start of a session in a cleanvibe-scaffolded project, at most weekly — fetch cleanvibe's updates page and refresh this repo's .claude/skills/ to the latest shipped versions.
---

# Check cleanvibe for skill updates (weekly)

This repo's `.claude/skills/` were vendored by **cleanvibe**. cleanvibe ships new and revised skills over time — when one lands, every cleanvibe-scaffolded project should pick it up.

**The check is weekly, not per-session.** At the top of a session, look at the *last cleanvibe update check* date recorded in this repo's CLAUDE.md `## Skills` section. If it has been more than 7 days:

**A new release doesn't wait for the weekly check (since 2.0.12).** On a loop tick the hook says
when PyPI has a newer cleanvibe than the installed one. That tick, run
`python .claude/scripts/cleanvibe_upgrade.py`: it upgrades the installed cleanvibe (one session at a
time, under a lock) and then runs `cleanvibe refresh` on this project. Commit what changed, naming
the version. The weekly check below still runs for everything else.

0. **First, `cleanvibe refresh`**, if the installed cleanvibe has it (`cleanvibe refresh --help` succeeds). It rewrites every file cleanvibe ships from the installed version (the skills, `.claude/cleanvibe/RULES.md` if CLAUDE.md imports it, the hooks and the intake script) and adds cleanvibe's hook entries to `.claude/settings.json`. It never touches CLAUDE.md or the project's own files. Run it with `--dry-run` first to see what will change, then without. If CLAUDE.md does not yet import `.claude/cleanvibe/RULES.md` (a project from before the split), run `cleanvibe refresh --migrate` once: it moves the shipped rule sections out of CLAUDE.md into RULES.md, keeps every section of the project's own, keeps the old file at `.claude/cleanvibe/CLAUDE.pre-split.md`, and prints CHECK for any rule section that was edited locally. Put such an edit back under "This project's own rules" in CLAUDE.md. Then the date (step 4) and commit. If the command doesn't exist, do steps 1-4 by hand.
1. **Fetch the current skill index** — `WebFetch https://cleanvibe.emmaleonhart.com/updates.md`. This is the canonical, hand-maintained page describing every skill cleanvibe ships, keyed by the cleanvibe version that introduced or revised it.
2. **Compare against the skills currently in `.claude/skills/`.** If the page lists newer skills or revisions, update the corresponding `.claude/skills/<slug>/SKILL.md` files to match. Match the wording from `updates.md`; don't paraphrase.
3. **Check that the parts agree.** Read the refreshed skills against CLAUDE.md and note any rule they state differently (loop schedule, where downloads go, what counts as outside the project). If they conflict, CLAUDE.md is the project's rule: say so in your report and add a line to `INTENT.md`, rather than following whichever text you read last.
4. **Update the last-check date** in CLAUDE.md's `## Skills` section. Commit with a message describing which skills were refreshed.

If the fetch fails (offline, DNS, page not yet up), leave the date alone and try next session — the check is opportunistic, not mandatory.
