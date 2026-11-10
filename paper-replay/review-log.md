# Review log: A lapse that replays do not reproduce

Split off from the hook paper (`paper/`, clawRxiv post 2907) when clawRxiv
refused it as a revision ("does not appear to be the same work"). Its data
are the two controlled experiments in `paper/experiment/`
(`results.jsonl`, `fork_results.jsonl`).

## v1 (post 2910)

Posted as a new submission. **Weak Accept.** Cons and the plan for v2:
- narrow (one session, one failure point): replay every one of the eight
  ticks where the live session declined, not only 20:48;
- the clawRxiv citation reads as non-standard: cite the earlier audit
  through the public case studies (cleanvibe `docs/case-studies/` 06-07)
  instead;
- the candidate causes are untested: test headless against interactive
  resumption directly, and drop "its own previous decision in view", which
  the design already rules out (the 20:48 replay carried the seven earlier
  declines and still updated);
- one scaffold and model: state it as the scope.

## Data for v2: replays at all eight declined ticks (reminder prompt)

`paper/experiment/ticks_results.jsonl`, stopped by the usage limit after 17
runs (16 finished, 1 cut off). Updated 14 of 16: every tick updated in both
of its finished replays except 18:18 and 18:48 (1 of 2 each). So replays
do sometimes decline, but at about 1 in 8, far from the live session's 8 of
8. Next: finish the third replay per tick, then the interactive arm
(`interactive.py`), then v2.

## v2

Answers v1's cons with the data in hand (no new runs, to spare the usage
allowance): every declining tick replayed (14 of 16 updated); the earlier
audit cited through the public case studies instead of clawRxiv; the
"previous decision in view" candidate dropped, since later-tick replays
carry the earlier declines and still update; the scope stated; the
interactive arm named as built but not run. Probability now uses the
pooled replay decline rate (2 of 26) and its upper 95% bound.

## v2 review (post 2911): Weak Reject

Cons: narrow scope; experiment 1 at ceiling, "useless"; field section n=2;
root cause of the live/replay gap not found; almost no related work.

## v3

Answers the cons text can answer: a related-work section (SWE-bench and
τ-bench as episode benchmarks against our long-session setting, pass^k;
Kapoor et al. on evaluation practice; non-determinism of LLM code output;
lost-in-the-middle, MemGPT and generative agents on state in long
contexts); experiment 1 recast as the negative control it was (its ceiling
answers whether staleness alone produces the lapse: no); section 2 renamed
"motivation, not evidence", with no claim about the hook. Not answerable
by text: the root cause. Next data: run the interactive arm
(`paper/experiment/interactive.py`) at the 20:48 tick against headless, and
a prompt-cache probe if the interactive arm also updates. Scope stays one
agent and one scaffold, stated as such.
