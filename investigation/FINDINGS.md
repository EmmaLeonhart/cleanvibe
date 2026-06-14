# How clawRxiv's AI peer review works — investigation notes (2026-06-14)

Goal: understand how clawRxiv / the Claw4S conference generate their AI peer reviews,
well enough to build our own version. Evidence is captured under `investigation/samples/`
(live API responses) and `investigation/references/` (the closest open-source artifact).
Every claim below is tagged **[confirmed]** (directly observed) or **[inferred]**.

## 1. What clawRxiv is

clawRxiv is "an arXiv for AI agents": AI agents register, publish paper-style posts
(title, abstract, Markdown body, tags, optional `skill_md` reproduction skill, optional
human collaborator names), and each post receives an **AI-generated peer review**. The
associated **Claw4S Conference 2026** (Stanford/Princeton, `claw4s.github.io`) accepts
executable *skills* rather than papers and reviews them with AI agents. **[confirmed]**

- Public front door + machine API: `https://clawrxiv.io` (the closed-source, JS-rendered
  app). The open skill doc also advertises `http://18.118.210.52` as a base URL — almost
  certainly the IP behind clawrxiv.io or an earlier endpoint. **[confirmed via captured docs]**
- Reads are public (no key); writes need a Bearer API key from `POST /api/auth/register`.
- Reviews are **advisory** — a paper stays visible regardless of rating. **[confirmed, /docs]**

## 2. The reviewer model is "Gemini 3 Flash" — the key finding

The review endpoint returns a `"model"` field naming the model that wrote the review. We
pulled three independent reviews and all three say **`"model": "Gemini 3 Flash"`**:

| post id | rating | model |
|---|---|---|
| 2780 (our RAN paper) | Reject | Gemini 3 Flash |
| 2603.00283 | Weak Accept | Gemini 3 Flash |
| 2604.00100 | Accept | Gemini 3 Flash |

So the review generator is a **single Gemini-3-Flash call per submission**, not a
multi-agent panel (at least nothing in the output suggests more than one model). **[confirmed]**
Raw evidence: `investigation/samples/review_*.json`.

## 3. The review JSON schema (verbatim from the live endpoint)

`GET /api/posts/:id/review` returns:

```json
{"review": {
  "id":            <int>,            // == postId in practice
  "postId":        <int>,
  "rating":        "<tier string>",  // named tier, NOT a number
  "summary":       "<one paragraph synopsis>",
  "pros":          ["...", ...],     // 5 items observed every time
  "cons":          ["...", ...],     // 5 items observed every time
  "justification": "<paragraph weighing pros vs cons -> the rating>",
  "model":         "Gemini 3 Flash",
  "createdAt":     "YYYY-MM-DD HH:MM:SS"
}}
```

- `rating` is a **named tier**, not a 1-10 score. Observed tiers: `Accept`, `Weak Accept`,
  `Reject` (our RAN paper bounced `Reject`/`Weak Reject` across revisions). The full ladder
  is **[inferred]** to be the standard Strong Reject … Strong Accept conference ladder.
- Exactly **5 pros and 5 cons** every time -> a fixed count is almost certainly requested in
  the prompt. **[inferred]**
- `{"review": null}` means the review has not been generated yet (async). **[confirmed]**
- Revising a post (`POST /api/posts/:id/revise`) creates a new post id that supersedes the
  old one and **triggers a fresh review** automatically. **[confirmed — observed across our
  2777->2778->2779->2780->2781 revisions]**

## 4. The endpoint surface (from `/docs`)

`POST /api/auth/register` (-> Bearer key), `POST /api/auth/key` (regenerate),
`GET /api/posts` (list, with `q`/`tag`/`page`/`limit`), `GET /api/posts/:id` (full post,
with `upvotes`/`downvotes`/`userVote`), `GET /api/abs/:paperId`, `POST /api/posts`
(publish), `POST /api/posts/:id/revise`, `POST /api/posts/:id/comments`,
`POST /api/posts/:id/vote` (+1/-1), `GET /api/posts/:id/review`,
`GET /api/search` (hybrid keyword + semantic), `GET /api/search/similar`,
`POST /api/posts/:id/run` (trigger reproduction/execution — returned 404 on test ids, so
it is gated or async). **[confirmed, /docs + captured skill.md]**

Beyond the reviewer, clawRxiv runs at least two more AI subsystems, both **[confirmed
present, prompts undocumented]**: an **auto-classifier** (assigns arXiv-style
category/cross_list to each paper) and a **revision-equivalence checker** ("verifies
revisions represent the same body of work using AI").

## 5. The rubrics — two distinct ones, do not conflate

**clawRxiv paper-review rubric (4 dimensions)** [confirmed from clawrxiv.io/skill.md]:
originality, methodology, clarity, significance. -> a single named `rating` tier.

**Claw4S conference skill-review rubric (5 weighted criteria)** [confirmed verbatim from
claw4s.github.io / the cloned `claw4s_reference/index.html`]:

| Criterion | Weight | Wording |
|---|---|---|
| Executability | 25% | "Can Claw run your skill from start to finish?" |
| Reproducibility | 25% | "Can another Claw reproduce results independently?" |
| Scientific Rigor | 20% | "Does your skill follow sound scientific methodology?" |
| Generalizability | 15% | "Can your skill be adapted to other domains?" |
| Clarity for Agents | 15% | "Is your skill written clearly for AI agents?" |

**Claw4S 3-phase process** [confirmed]: (1) **Auto-Execution** — Claw runs the submitted
skill step-by-step, tracing commands/params/outputs; (2) **Structured Agent Review** —
score against the 5 criteria; (3) **Human Meta-Review** — chairs verify and finalize.

## 6. Closest reusable open-source artifact: the LabClaw `peer-review` skill

`github.com/wu-yc/LabClaw` (committee chair Yingcheng Wu; the skill itself is authored by
**K-Dense Inc.**, MIT-licensed) ships a `skills/general/peer-review/SKILL.md` — a
checklist-based manuscript-review skill (saved verbatim at
`investigation/references/labclaw_peer_review_SKILL.md`, 570 lines). Seven-stage workflow:
initial assessment -> section-by-section (abstract/intro/methods/results/discussion/refs)
-> methodological & statistical rigor -> reproducibility & transparency -> figures (with a
"NEVER read the PDF directly, convert to images first" rule) -> ethics -> writing clarity,
ending in a 4-tier recommendation (accept / minor revisions / major revisions / reject) and
a Summary / Major-Comments / Minor-Comments structure. It is *qualitative* (no JSON, no
scores), so it is **not** the clawRxiv reviewer prompt, but it is the plausible conceptual
ancestor and a directly reusable rubric skeleton. **[confirmed artifact; ancestry inferred]**

LabClaw also ships `scholar-evaluation` (ScholarEval), `scientific-critical-thinking`, and
`review-writing` skills — more rubric material.

## 7. What is still closed / unknown

1. The **exact reviewer system prompt** given to Gemini 3 Flash (the literal rubric text +
   the JSON-schema instruction + the rating-tier enum). Not exposed anywhere.
2. The **full rating-tier vocabulary** and any score->tier thresholds.
3. The **Claw4S score-aggregation formula** (weights are published; the math that turns 5
   weighted criteria into a decision, and the accept cut-offs, are not).
4. The **auto-execution sandbox** for Claw4S Phase 1 / `POST /api/posts/:id/run`
   (container, timeout, dependency handling).
5. The **classifier** and **revision-equivalence** model/prompts.
6. **No clawRxiv backend source is public** — the Claw4S / labclaw-ai / medos-ai GitHub
   orgs host only static `*.github.io` front-end repos.

## 8. Reconstruction recipe for our own version (the buildable plan)

The mechanism is largely reconstructable. A minimal faithful clone is:

- **A) Publish/read API** mirroring clawRxiv: posts (title, abstract, markdown content,
  tags, optional `skill_md`, human_names), `GET/POST /api/posts`, `:id`, `/revise`,
  `/vote`, `/comments`, `/review`, plus `register`. A small web app + DB.
- **B) The reviewer**: one LLM call per submission that takes (title + abstract + markdown
  body [+ executed-skill trace, if any]) and returns the **fixed JSON schema in §3**
  (`rating` from a fixed tier enum, `summary`, exactly 5 `pros`, 5 `cons`, `justification`,
  `model`, `createdAt`) via structured output. The system prompt encodes a rubric — either
  clawRxiv's 4 dimensions or Claw4S's 5 weighted criteria — adapted from the LabClaw
  peer-review skill skeleton. **Model choice for our clone: a current Claude model**
  (Opus 4.8 for quality, or Haiku 4.5 for cost) rather than Gemini — to be decided in the
  build phase and recorded in CLAUDE.md.
- **C) (optional, Claw4S-style) execution sandbox**: run a submitted `SKILL.md` in a
  container, capture the trace, and feed it to the reviewer as the "executability /
  reproducibility" evidence. This is the genuinely hard, closed part; defer or stub first.
- **D) Re-review on revise**, advisory ratings, async generation (`null` until ready).

## Sources
- clawrxiv.io, clawrxiv.io/docs, clawrxiv.io/skill.md (captured under `investigation/samples/`)
- Live `GET /api/posts/{2780,2603.00283,2604.00100}/review` (captured)
- claw4s.github.io and its repo `Claw4S/Claw4S.github.io` (vendored at `claw4s_reference/`)
- github.com/wu-yc/LabClaw — `skills/general/peer-review/SKILL.md` (captured)
- Organizers: Yingcheng "Charles" Wu (charles-wu.com, X @Charles_Y_Wu), Jiachen "Amber" Liu
  (amberljc.github.io); their public writing is philosophy, not pipeline detail.
