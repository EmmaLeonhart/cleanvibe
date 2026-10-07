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
