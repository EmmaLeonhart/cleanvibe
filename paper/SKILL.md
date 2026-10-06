---
name: cleanvibe-intent-staleness-audit
description: Reproduce the round 3 count — how often a stale INTENT.md is updated after cleanvibe's staleness hook reports it — on public practice sessions or your own cleanvibe projects.
allowed-tools: Bash(git *), Bash(python *), Bash(gh *)
---

# Reproduce the INTENT.md staleness audit

Needs git and Python 3.9+ (standard library only).

1. Get the audit script and the round 3 practice sessions (public; each
   repository holds its full transcripts under `sessions/`):

   ```
   git clone https://github.com/EmmaLeonhart/cleanvibe
   git clone https://github.com/EmmaLeonhart/markdown-notes-static-site
   git clone https://github.com/EmmaLeonhart/pure-python-sql-database
   git clone https://github.com/EmmaLeonhart/r7rs-scheme-in-python
   git clone https://github.com/EmmaLeonhart/pure-python-git
   git clone https://github.com/EmmaLeonhart/pure-python-chess-engine-selfplay
   ```

2. Run the audit on them:

   ```
   python cleanvibe/paper/scripts/staleness.py markdown-notes-static-site pure-python-sql-database r7rs-scheme-in-python pure-python-git pure-python-chess-engine-selfplay
   ```

   Each line is one project. `active_stale_firings` counts the times the hook
   reported INTENT.md two or more hours stale while work was being committed;
   `active_stale_firings_updated` counts how many of those were followed by an
   INTENT.md commit within 30 minutes. The paper's prediction is that the
   second is most of the first.

3. To add a session of your own: install cleanvibe from the clone
   (`pip install ./cleanvibe`), create a project with `cleanvibe new`, put a
   brief large enough for several hours of work in its `data_lake/brief.md`,
   say nothing in the chat, and let the loop run. Then run step 2 on that
   project's folder.

The numbers in the paper's round 3 table are the output of step 2.
