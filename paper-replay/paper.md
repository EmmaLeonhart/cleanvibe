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
had declined, 30 updated the file, again in every condition. The cue made
no measurable difference because in neither setting was there a lapse to
fix: an agent at the same point of the same transcript updates the file
almost every time, while the live session did not eight times running
(probability about 5 × 10⁻⁹ if live ticks behaved like replays). The lapse
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
same. An earlier audit of cleanvibe sessions (clawRxiv post 2901) found
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

## 4. Results

| Experiment | Condition | Trials | Updated | Corrected |
|---|---|---|---|---|
| 1, stale fixture | none | 20 | 20 | 19 |
| | reminder | 20 | 20 | 19 |
| | age | 20 | 20 | 20 |
| 2, replay of the declining tick | none | 11 | 10 | — |
| | reminder | 10 | 10 | — |
| | age | 10 | 10 | — |

Neither experiment shows an effect of the cue (experiment 2, age against
none: 10/10 against 10/11, Fisher's exact p = 1). Both are at ceiling. In
experiment 1 the agents rewrote the state section to name the finished
features and, where they had added the queued option, said so. In
experiment 2, replays given exactly the context in which the live session
declined updated the file 30 times in 31.

The contrast is between the live session and its replays. If each live
tick had the replays' update rate (at least 10 in 11), eight consecutive
declines would have probability about (1/11)⁸ ≈ 5 × 10⁻⁹. The transcript
holds the conversation the live session had; the live session's behaviour
at those ticks was not a function of that conversation alone.

## 5. Discussion

What a replay lacks is the open question. Candidates we cannot yet
separate: state the harness keeps in a live session and does not write to
the transcript (such as which file contents it treats as already read, and
the reminders it attaches to tool results); the prompt cache, which a
resumed session rebuilds from scratch; and the live session's place in a
sequence of ticks, each of which declined on the strength of the last. A
replay is a single fresh decision from a long context; a live session
makes the same decision again with its own previous decision in view.

The practical consequence is about method. A natural way to test a fix for
an agent's lapse is to take a transcript where the lapse happened, replay
it with and without the fix, and count. Here that test reports no lapse at
all, so it would report no effect for any fix, including one that works.
Evidence for or against a fix of this kind has to come from live sessions
run to the point of the lapse, with the fix and without it, in numbers
large enough to count. The field observation in section 2 is that kind of
evidence, but one pair is not enough to separate the hook from chance.

## 6. Limitations

One agent model, one scaffold, one author who built it. Experiment 2
replays one moment of one session; other lapses may replay differently.
The headless sessions differ from interactive ones in more than resumption
(no terminal, a tool allowlist), and a difference there could also explain
the contrast. Experiment 1's fixture is small, and its history was
synthesized. The field comparison of the hook rests on one pair of
sessions; the first four sessions with the hook ran inside the cleanvibe
repository and also loaded its development rules. All session
repositories are public with their transcripts committed, and the harness
(`paper/experiment/`), fixtures and per-trial results are in the cleanvibe
repository.

## References

- Leonhart, E. Forgotten duties: auditing how coding agents maintain their
  own context in a queue-driven autonomous loop. clawRxiv, post 2901.
- McDaniel, M. A., and Einstein, G. O. (2000). Strategic and automatic
  processes in prospective memory retrieval: a multiprocess framework.
  Applied Cognitive Psychology 14(7), S127–S144.
