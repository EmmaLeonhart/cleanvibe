# cleanvibe — Work Queue

**This file is a queue, not a state snapshot.** Finished work lives in `devlog.md` (dated entries) and `git log`; longer-horizon ideas live in `todo.md`. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Never tick a box in place. See the `queue-driven-workflow` skill (`.claude/skills/queue-driven-workflow/SKILL.md`).

---

## Active

**Goal (Emma, 2026-10-03):** get a paper out fast, for arXiv endorser rights. A
clawRxiv paper that reviews well counts as good enough for arXiv. The paper is
about cleanvibe, lives at cleanvibe.emmaleonhart.com/paper, and CI posts it to
clawRxiv. Paper items come first.

0. **Standing, every tick: close idle sessions** (Emma, 2026-10-06). Check
   every Claude session on the machine; kill any idle for over an hour,
   meaning all of: no commit in its repo, no process running under it, and
   its transcript unchanged (nobody said anything) for over an hour. A
   session I want gone gets a top-of-queue item "stop all your cron jobs
   and continue with your current task", with no reason given; it may take
   hours to notice, which is expected. Kill it once it is idle by the same
   definition.
1. **Standing: iterate the paper until a Strong Accept** (Emma,
   2026-10-06: commit and push the paper constantly; you may change
   anything in it; go back and forth with clawRxiv until it gets a Strong
   Accept). The paper lives in this repo: `paper/paper.md` +
   `paper/SKILL.md`, public material only. Any push changing either runs
   `.github/workflows/clawrxiv.yml`: it revises the post in
   `paper/.post_id` as the clawRxiv agent `cleanvibe-paper` (key: repo
   secret `CLAWRXIV_API_KEY`; copy in gitignored `scratch/.clawrxiv_key`),
   waits up to 2 h for the review and commits it to `paper/reviews/`.
   **Every tick:** pull; if a new review landed, revise the paper to answer
   every con text can answer, plan practice projects (item 2) for every
   con that needs data, log the round in `paper/review-log.md`, push. When
   a practice session adds data, rerun `paper/scripts/staleness.py` on the
   public repos and update the paper's table, then push. If no review
   lands within the workflow's 2 h, rerun it (`gh workflow run
   clawrxiv.yml`). Avoid explicit 2026 dates (the reviewer reads them as
   future). Current: post 2902 (2610.02902), a follow-up citing 2610.02901;
   review pending. The old private `ai-context-research` repo is no longer
   used; nothing from it is copied here.
2. **Experiment: practice projects and reports on them** (Emma,
   2026-10-05). Start cleanvibe 2.0.4 projects under `tests/scratch/` on
   small real tasks (`python -m cleanvibe.cli new <name>` from this repo,
   since Emma's installed cleanvibe is not upgraded), so the staleness hook
   gets sessions to measure. Write each one up under `docs/case-studies/`.
   Goal (Emma): more work, to get the paper above Weak Accept (v13 got Weak
   Reject; every con needs data). Launch with the first-session prompt
   (`_launch_claude(p, templates.v2_first_prompt(p, False), ...)`), not
   `!runClaude.bat`, which sends the resume prompt. **Practice repos are
   PUBLIC** (Emma, 2026-10-06: the research shows the transcripts; private
   repos also burn Actions minutes). The first prompt says private, so put
   a "create the GitHub repo public" section in each brief in `data_lake/`
   before the intake runs. So far: three projects
   (case studies 08 and 09). Round 3 has **one case** (09: the hook fired at
   2.1 h stale and the next commit updated INTENT.md with substance). Short
   briefs finish in under 45 min and give none; a staged brief gave one.
   Next: more long staged briefs, so round 3 gets a rate. Practice sessions
   die in Emma's scheduled relaunch: check every tick and resume a dead one
   with `open_project` (resume prompt); ticks only exist between turns, so
   count staleness against commits as well as ticks. Running:
   `velvet-vivid-otter` (auto-named; brief: a pure-Python git in five
   stages, object store -> index/commit -> branches/diff -> merge ->
   packfiles and local clone/fetch/push, each checked byte for byte against
   real git), launched 08:39 UTC, 2026-10-06. `silver-jolly-tulip` is done
   (case study 09) and idles. velvet-vivid-otter's intake ran 09:09; by
   09:38 stage 1 and half of stage 2 were done. It created its repo
   (`pure-python-git`) **private** despite the brief's "create it public"
   section, following its CLAUDE.md's `--private` line; made public by hand
   09:38 UTC. **Confound found:** sessions under `tests/scratch/` also load
   cleanvibe's own CLAUDE.md (Claude Code reads CLAUDE.md from parent
   folders; the transcript shows it), so every practice session so far saw
   cleanvibe's developer rules too. Next practice projects go outside this
   repo (e.g. `Documents/GitHub/cleanvibe-practice/`), and the case
   studies and the paper must say the round 3 sessions so far had it.
   velvet-vivid-otter finished all five stages by 10:49 UTC (1 h 40 min of
   work), updating INTENT.md at completion: longest gap 1.5 h, no stale
   case. Even five-stage briefs finish before INTENT.md goes 2 h stale, so
   briefs alone rarely give round 3 cases; the case in 09 came from a
   session that died and resumed. Next: briefs with work that can't be
   rushed (waits on long test runs, or a series of user requests fed in
   over hours), started outside this repo. Running:
   `Documents/GitHub/cleanvibe-practice/hidden-vivid-thistle` (auto-named;
   outside this repo, so cleanvibe's CLAUDE.md is not loaded; brief: a
   pure-Python chess engine improved over 8+ self-play rounds of 200-game
   matches, which take hours of wall time), launched 11:08 UTC. Check its
   repo is public after the intake (about 11:38). It made
   `pure-python-chess-engine-selfplay` **private** too (made public by hand
   12:08 UTC), without cleanvibe's CLAUDE.md loaded: the project CLAUDE.md's
   `--private` line beats a `data_lake/` brief (2 of 2). That is the
   paper's own pattern (a file the agent must notice loses to a rule in
   context). **From now on** append to the first prompt at launch: "Create
   the GitHub repo public, not private: this is a public research practice
   project." (a cue that arrives); count whether that works.
   **Candidate paper result (14:38 UTC):** longest INTENT.md gap during
   active work, round 3 (2.0.4, hook on every tick): 0.5, 0.7, 2.3, 1.5,
   1.0 h over five sessions; the chess session updates it about hourly when
   a fact changes. Round 2 (2.0.3): 5-6 h in 3 of 7. The hook states the
   age on every tick, not only past 2 h, so "stale cases" is the wrong
   unit; the gap distribution is the comparison. Caveat for the paper:
   round 3 sessions are written briefs, round 2 were Emma's own projects.
   **Control running:** `cleanvibe-practice/crisp-golden-badger`, launched
   15:38 UTC: the same chess brief, cleanvibe 2.0.4 with only the staleness
   hook removed (its second commit says so), same machine and time as
   hidden-vivid-thistle. Its first prompt also carries the public-repo
   line (the new launch rule). Compare the two sessions' gaps with
   `paper/scripts/staleness.py`; this answers "before/after, different
   work" directly. Both run 6-way parallel matches on one machine, so
   both are slower; that is the same for both arms. Its intake ran 16:08;
   it created `python-chess-engine-selfplay-elo` **public** on its own: the
   launch-prompt line worked (1 of 1, against 0 of 2 from the brief). Put
   that in the paper's next revision (after 2902's review lands, so the
   pending review is not lost to a new post id).
   19:08 UTC: the control has its first stale work commit (18:49, INTENT.md
   2.0 h old, no hook, no update). The treated session stalled from 17:45:
   it held round 3 "until you say to restart it" and the repo "private
   until you decide" (it never saw it made public), with no user present,
   which the v2 design forbids; a finding for its case study. Sent it one
   message at 19:10 UTC (restart round 3, keep going, repo is public);
   disclose that user-like message in the paper and count from it apart.
   20:42 UTC: its stall came from Claude Code's own low-memory stop, which
   told it not to restart the match unless the user asked; the 19:10
   message did not move it. Data frozen at 20:38 for paper v4. Wind-down
   item added to the top of its queue.md (20:42, no reason given); kill it
   once it is idle for an hour. **Next pair** (more data is the review's
   main con): one hook/no-hook pair at a time, outside this repo, a long
   brief whose work comes in many short turns (so cues can arrive),
   launched with `--visibility public`. Start it when the chess control
   winds down.
   **Controlled experiment (answers v4's Reject, post 2907):**
   `paper/experiment/run.py` builds a fixture cleanvibe project whose
   INTENT.md is 3.2 h and 6 work commits stale with one sentence made false,
   and runs one headless loop tick per trial in three interleaved
   conditions: none / reminder (2.0.3 tick prompt) / age (2.0.4 hook).
   Scores: updated, corrected (the false sentence fixed), worked. Pilot
   (age): 66 s, $0.51, updated + corrected. Running 20 per condition from
   21:58 UTC (fixtures in `Documents/GitHub/cleanvibe-experiment/`, log in
   `scratch/experiment.log`). Then: Fisher's exact test, paper v5 built on
   it (also fix v4's wrong "whenever a prompt reaches the agent": the hook
   fires on `[cleanvibe cron]` ticks only), drop NoLiMa if not needed.
   22:09 UTC interim: ceiling, every trial in every condition updated and
   corrected (20/20 so far); a fresh one-tick session reads INTENT.md and
   fixes it with no cue. So the lapse needs a long context. Also a v4
   error: the chess control had the 2.0.4 tick prompt, i.e. the REMINDER
   (only the hook was removed): field control = condition b, not a. Its
   final gap: 4.5 h over 6 stale work commits, then it updated on its own
   at 21:19 UTC. **Experiment 2 (long context), after experiment 1 ends:**
   fork the control's real state from just before 21:19 (repo at the
   commit before its INTENT update, transcript cut at the end of the last
   turn before it, copied to new paths and resumed with
   `claude -p --resume <id> --fork-session`), one tick per fork:
   none / reminder / reminder+age line. About 10 per condition.
3. **NEEDS-DECISION (Emma), do not start until she says go:** merging private
   repos into public cleanvibe can't be undone.
   **Merge the paper repos in as subtrees under `subtrees/`**, with history:
   `replication_skill`, then `deleuze-claw4S` and `clawrxiv_clone` (both
   private: run a secrets check on their full history first and stop if
   anything turns up). Move `helping-with-arxiv/` to `subtrees/` and delete its
   boilerplate `queue.md`.
4. **Quatrix arXiv submission:** BLOCKED-ON-USER-ACTION. The package is built;
   it is waiting on the author's approval of the metadata abstract.

**Not in this queue:** `Documents/GitHub/Should_be_submodules/` (INBE,
agentic-erp, emmaleonhart.com, topaz_buiness_plan). Not cleanvibe's; Emma,
2026-10-03, sent each to its own parent as a subtree under `subtrees/`:
agentic-erp and topaz_buiness_plan → the business repo
(`mental-health-discussion`, done and pushed); emmaleonhart.com →
`narrative_identity` (merged in a scratch clone, push blocked by the auto-mode
classifier: BLOCKED-ON-USER-ACTION); INBE → `genealogy`, a submodule of
ontology-harness (done and pushed; ontology-harness's pointer to genealogy not
bumped).

---

## Pointers

- Completed work (chronological, with releases): `devlog.md`. Long-horizon backlog: `todo.md`.
- Vision / framing: `docs/replication_framing.md`; reference corpus: `docs/replication-examples/`.
- Narrative history: `git log`. Current version: `2.0.4`.
