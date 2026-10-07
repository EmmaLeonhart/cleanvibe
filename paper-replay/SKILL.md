---
name: cleanvibe-staleness-cue-experiments
description: Reproduce the paper's two controlled experiments on whether stating INTENT.md's age makes a Claude Code agent update it, and the field staleness audit, from the public cleanvibe repository.
allowed-tools: Bash(git *), Bash(python *), Bash(claude *)
---

# Reproduce the staleness-cue experiments

Needs git, Python 3.9+, and Claude Code (`claude`) logged in. Each trial is
one headless session (about a minute and $0.50 in experiment 1, $1.50 in
experiment 2).

1. Get cleanvibe:

   ```
   git clone https://github.com/EmmaLeonhart/cleanvibe
   cd cleanvibe
   ```

2. **Experiment 1 (stale fixture).** Builds fixtures next to the clone and
   runs one loop tick per trial in the conditions none / reminder / age:

   ```
   python paper/experiment/run.py --trials 20 --out my_results.jsonl
   ```

   Each line records `updated` (INTENT.md changed), `corrected` (the
   false sentence is fixed), `worked` (the queued task was done) and
   `finished` (the run was not cut off). The paper's counts are in
   `paper/experiment/results.jsonl`.

3. **Experiment 2 (replay)** needs the original session's transcript, which
   lives only on the author's machine; its per-trial results are in
   `paper/experiment/fork_results.jsonl`, and `paper/experiment/fork.py`
   shows exactly how each replay was built. To run the same test on your
   own lapse: point `SOURCE`, `SESSION`, `CUT_LINE` and `COMMIT` in
   `fork.py` at a session and tick of yours, then
   `python paper/experiment/fork.py --trials 10`.

4. **Field audit.** For any cleanvibe project (the paper's are public, e.g.
   github.com/EmmaLeonhart/python-chess-engine-selfplay-elo):

   ```
   python paper/scripts/staleness.py PROJECT_DIR
   ```

   prints the longest stretch of work without an INTENT.md update and how
   the staleness hook's reports were followed.
