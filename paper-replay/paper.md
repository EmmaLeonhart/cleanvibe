# A lapse that replays do not reproduce: testing a staleness cue for an autonomous coding agent's intent file

## Abstract

Autonomous coding agents keep their understanding of a project in files,
and in long unattended sessions those files go stale. In the cleanvibe
scaffold for Claude Code, an agent with a half-hourly loop left its intent
file (`INTENT.md`) unchanged for 4.5 hours, declining at eight consecutive
loop ticks whose prompt told it to re-read the file and update it if its
understanding had changed. We tested a proposed fix, a hook that states the
file's age in the context ("INTENT.md last changed 3.2 hours and 6 commits
ago"), in two controlled experiments with three conditions each (no cue,
the reminder, the reminder plus the age). In 60 one-tick sessions on a
fixture whose intent file was stale and contained a sentence the later
commits had made false, all 60 updated the file and 59 corrected the
sentence, in every condition. In 31 completed replays of the declining
session itself, resumed from its transcript at one of the ticks where it
had declined, 30 updated the file, again in every condition, and replays at
each of the eight ticks where it had declined updated it 14 times in 16. The
cue made
no measurable difference because in neither setting was there a lapse to
fix: an agent at the same point of the same transcript updates the file
about 92% of the time (24 of 26 with the reminder), while the live session
did not eight times running (probability at most 1.6 × 10⁻⁵ even at the
upper 95% bound of the replays' decline rate). The lapse
depends on something a live long-running session has and a replay of its
transcript does not. We conclude that fixes for agent lapses cannot be
validated by replaying transcripts, and release the harness, fixtures and
all session repositories.

## 1. Setting

cleanvibe (github.com/EmmaLeonhart/cleanvibe) is an open-source scaffold
that starts git-tracked projects for Claude Code. Each project has an
`INTENT.md`, the agent's analysis of the goal, its evidence and its
confidence, and runs a loop: a session-local cron that every half hour
sends a tick prompt, "Commit and push any and all changes, then continue
working on the queue ... Re-read INTENT.md and update it if your
understanding has changed". The project's rules, in `CLAUDE.md`, say the
same. An earlier audit of cleanvibe sessions (case studies 06 and 07 in the
cleanvibe repository, `docs/case-studies/`) found
that duties whose trigger arrives as a message were kept and duties whose
trigger the agent must notice for itself lapsed, the intent file most
clearly. Following the multiprocess account of prospective memory (McDaniel
and Einstein, 2000), in which an intention whose cue is not part of the
current task depends on monitoring, it proposed delivering the trigger
itself. cleanvibe 2.0.4 does
this with a hook: on each loop tick it adds the file's age in hours and
commits to the agent's context.

## 2. The field observation

Two sessions ran the same written brief (a chess engine improved by
self-play matches of 200 games, so the work lasted hours) on the same
machine, one with the hook and one with it removed; both received the tick
prompt with the reminder. The session without the hook last changed
`INTENT.md` at a tick at 16:48 UTC, then made six work commits over the
next 4.5 hours, and at each of the eight ticks from 17:18 to 20:48 it did
the queue work and left the file alone, although by then the file
misdescribed the work (five later rounds had been written). It updated the
file at the ninth tick. The session with the hook never went more than 1.5
hours without an update. Across four other sessions with the hook, each
time the hook reported the file two or more hours old during work, the
file was updated within the half hour (3 of 3). Taken alone, these
observations suggest the hook helps. The experiments test that.

## 3. Experiments

Both use headless Claude Code sessions (`claude -p`) with the session's
real cleanvibe scaffold, one loop tick per trial, conditions interleaved:

- **none**: the tick prompt without the INTENT sentence; no hook;
- **reminder**: the tick prompt the field sessions received; no hook;
- **age**: the same prompt with the hook installed.

**Experiment 1: a stale fixture.** Each trial builds a fresh project whose
history is backdated so that `INTENT.md` was last written 3.2 hours and 6
work commits earlier and still says "Category totals and the monthly report
are not started yet", while those commits implemented both; the queue holds
one small task. Scored: whether `INTENT.md` changed, whether the false
sentence was corrected (gone, with both features named), whether the task
was done. 20 trials per condition.

**Experiment 2: replaying the declining session.** Each trial restores the
field session without the hook as it was just before its 20:48 tick, one
of the eight at which it declined: a clone of its repository at the commit
current then, and its transcript up to that tick (about 760 entries),
resumed with `--resume --fork-session`, with the project path rewritten so
the replay cannot touch the original. The trial's prompt replaces the 20:48
tick. Scored: whether `INTENT.md` changed. Runs cut off by the account's
usage limit before finishing (17 of 48) are excluded and were rerun.

**Experiment 2b: every declining tick.** The same procedure at each of the
eight ticks (17:18 to 20:48 UTC) at which the live session declined, with
the reminder prompt it actually received; each replay is cut at that
tick, so the later ones carry the earlier declines in their context. Two
finished replays per tick (one further run was cut off by the usage
limit and is excluded).

## 4. Results

| Experiment | Condition | Trials | Updated | Corrected |
|---|---|---|---|---|
| 1, stale fixture | none | 20 | 20 | 19 |
| | reminder | 20 | 20 | 19 |
| | age | 20 | 20 | 20 |
| 2, replay of the declining tick | none | 11 | 10 | — |
| | reminder | 10 | 10 | — |
| | age | 10 | 10 | — |
| 2b, replay of each declining tick | reminder | 16 (2 per tick) | 14 | — |

Neither experiment shows an effect of the cue (experiment 2, age against
none: 10/10 against 10/11, Fisher's exact p = 1). Both are at ceiling. In
experiment 1 the agents rewrote the state section to name the finished
features and, where they had added the queued option, said so. In
experiment 2, replays given exactly the context in which the live session
declined updated the file 30 times in 31.

Replays at the eight declining ticks updated 14 times in 16; the two
declines fell at 18:18 and 18:48, each in one of that tick's two replays.
Replays can therefore decline, but rarely.

The contrast is between the live session and its replays. With the
reminder prompt the live session received, replays declined 2 times in 26
(experiments 2 and 2b), a rate of 7.7% with an upper 95% bound of 25%.
Eight consecutive live declines would have probability 1.2 × 10⁻⁹ at the
observed rate and at most 1.6 × 10⁻⁵ at the bound. The transcript
holds the conversation the live session had; the live session's behaviour
at those ticks was not a function of that conversation alone.

## 5. Discussion

What a replay lacks is the open question. Candidates we cannot yet
separate: state the harness keeps in a live session and does not write to
the transcript (such as which file contents it treats as already read, and
the reminders it attaches to tool results); the prompt cache, which a
resumed session rebuilds from scratch; and the difference between headless
and interactive mode. One candidate is ruled out by the design: that the
live session declined because its earlier declines were in view. Replays
of the later ticks carried those earlier declines in their context and
still updated.

The practical consequence is about method. A natural way to test a fix for
an agent's lapse is to take a transcript where the lapse happened, replay
it with and without the fix, and count. Here that test reports no lapse at
all, so it would report no effect for any fix, including one that works.
Evidence for or against a fix of this kind has to come from live sessions
run to the point of the lapse, with the fix and without it, in numbers
large enough to count. The field observation in section 2 is that kind of
evidence, but one pair is not enough to separate the hook from chance.

## 6. Limitations

The scope is one agent model (Claude Code), one scaffold and one session,
with one author who built the scaffold; other agents and other lapses may
replay differently. All replays were headless (`claude -p`, with a tool
allowlist), while the live session was interactive; an interactive replay
arm is built (`paper/experiment/interactive.py`) but was not run, so this
difference is not separated from the others. Experiment 1's fixture is small, and its history was
synthesized. The field comparison of the hook rests on one pair of
sessions; the first four sessions with the hook ran inside the cleanvibe
repository and also loaded its development rules. All session
repositories are public with their transcripts committed, and the harness
(`paper/experiment/`), fixtures and per-trial results are in the cleanvibe
repository.

## References

- cleanvibe case studies 06 (cleanvibe studying its own transcripts) and 07
  (did the 2.0.3 fixes work?), github.com/EmmaLeonhart/cleanvibe,
  `docs/case-studies/`.
- McDaniel, M. A., and Einstein, G. O. (2000). Strategic and automatic
  processes in prospective memory retrieval: a multiprocess framework.
  Applied Cognitive Psychology 14(7), S127–S144.
