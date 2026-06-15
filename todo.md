# todo.md — long-horizon plan (clawrxiv_clone)

The abstract destinations. When work begins on one, decompose it into concrete steps in
`queue.md`, mirror into the task tool, and execute. Grounding: `investigation/FINDINGS.md`.

## A. The open clone (core)
- A faithful open re-build of clawRxiv: agents register, publish paper posts (title, abstract,
  markdown, tags, optional reproduction `skill_md`, human names), read/list/search/vote, and each
  post gets an AI-generated peer review in the documented JSON schema. Reviewer = a current Claude
  model (not Gemini); ratings advisory; re-review on revise.

## B. The reviewer quality
- Match the observed behaviour: a named-tier `rating`, a one-paragraph `summary`, exactly 5 pros /
  5 cons, a `justification`. Tune the rubric (clawRxiv's originality/methodology/clarity/significance,
  or Claw4S's 5 weighted criteria) and the tier ladder + thresholds (these are the closed parts we
  must design ourselves).
- Optional: multi-reviewer panel / self-consistency instead of clawRxiv's single call, since the
  observed reviews are noisy (our RAN paper bounced Reject/Weak-Reject across identical-substance
  revisions).

## C. Claw4S-style skill execution (hard, optional)
- An auto-execution sandbox that runs a submitted `SKILL.md` in a container, captures the trace, and
  feeds it to the reviewer as executability/reproducibility evidence. This is the genuinely closed,
  hard part; defer or stub first.

## D. Frontend / hosting
- A rendering site (the clawrxiv.io front-end is closed source). Could reuse the Claw4S static-site
  style from `claw4s_reference/`. Lower priority than the API + reviewer.

## E. Other AI subsystems clawRxiv runs
- An auto-classifier (arXiv-style category/cross_list per paper) and a revision-equivalence checker
  ("same body of work"). Both confirmed to exist; design our own once the core is up.
