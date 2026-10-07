# The hook paper

There are two papers. This folder is the staleness-hook paper (clawRxiv
post 2907); `../paper-replay/` is the paper on lapses that transcript
replays don't reproduce (post 2910). The scripts and experiment harness
here serve both. `python scripts/clawrxiv.py submit DIR` posts the paper in
DIR.

`paper.md` is the paper and `SKILL.md` its reproduction skill. Pushing a
change to either posts it to clawRxiv (`.github/workflows/clawrxiv.yml`):
a new post the first time, a revision of `.post_id` after that. The
workflow then waits for clawRxiv's AI review and commits it to `reviews/`.

The loop: run practice projects (public repositories, `tests/scratch/`),
write each up in `docs/case-studies/`, measure them with
`scripts/staleness.py`, put the new data in `paper.md`, push, read the
review, and repeat until the review is a Strong Accept. `review-log.md`
records each round's review and what was changed in answer.

The clawRxiv agent is `cleanvibe-paper`; its key is the repository secret
`CLAWRXIV_API_KEY`. Only public material goes here: round 1 and 2 numbers
are from the published case studies 06 and 07, round 3 from the public
practice repositories.
