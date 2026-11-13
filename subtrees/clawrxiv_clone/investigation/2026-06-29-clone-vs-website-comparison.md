# Clone vs. live clawRxiv — head-to-head on our own papers (2026-06-29)

**What this measures.** How well our local Gemma reviewer (`scripts/review.py`, `gemma3:12b`
+ the recent-papers policy) imitates the live clawRxiv website reviewer (a single **Gemini 3
Flash** call), on **recent versions of our own papers** — the original **Sutra** paper and the
**latent-space-cartography (LSC)** paper. The motivating question (Emma): the website is slow AND
**false-flags recent (2026) citations/dates/software-versions as hallucinated**, which has been the
single biggest reason to stop relying on it. Does our clone remove that failure mode?

**Method.** Same two papers, both reviewers, same day:
- Website reviews: the latest clawRxiv-CI-committed reviews — Sutra **post 2821** (`paper/reviews/`
  in the Sutra repo) and LSC **post 2828** (`reviews/` in the latent-space-cartography repo).
- Clone reviews: `python scripts/review.py <paper.md>` on `gemma3:12b` via local Ollama, 2026-06-29
  (raw JSON archived in the session scratchpad; verdicts/scores reproduced below).

## Result — the clone fixes the defining failure mode (2/2 papers)

| | Website (Gemini 3 Flash) | Clone (Gemma + recent-papers policy) |
|---|---|---|
| **Sutra** | **Reject** | **Borderline** (orig 3 / meth 4 / clar 2 / sig 3) |
| **LSC** | **Strong Reject** | **Borderline** (orig 4 / meth 4 / clar 2 / **sig 5**) |

**The website rejects BOTH papers primarily/entirely on FALSE temporal-hallucination flags:**
- Sutra (Reject), verbatim: *"significant temporal hallucination, claiming to have reviewed
  literature 'through early 2026'"*; *"references a GitHub repository and a replication package that
  likely do not exist … AI-generated content"*; justification: *"disqualified by clear evidence of AI
  hallucination, specifically the reference to literature from 2026."*
- LSC (Strong Reject), verbatim: *"based on a massive temporal hallucination: it cites Ollama
  v0.14.0 … and evaluates releases up to v0.24.0 in May 2026 … in the future"*; *"The primary
  'discovery' … is entirely fabricated"*; justification: *"a sophisticated hallucination … factually
  impossible … rendering the entire contribution fraudulent."*

It is **2026.** Those citations, dates, and Ollama versions are **real**; the LSC Ollama
diacritic-collapse bug is a **real, reproduced** finding. Gemini 3 Flash's training cutoff makes it
read "2026" as "the future" and disqualify legitimate current work as fraud.

**The clone produces ZERO temporal false-flags on either paper** (keyword-checked: no
hallucination / fabrication / fraud / "does not exist" / "in the future" in either review). Instead it
engages the actual content and even **credits what the website dismissed as fabricated**:
- Clone on LSC: *"The discovery of a real-world, previously unknown bug in a popular runtime (Ollama)
  is a significant contribution"* (significance **5**) — vs. the website calling that same finding
  "fraudulent."
- Clone on Sutra: substantive cons only (niche language, assumes fuzzy-logic/PyTorch familiarity,
  `.su`/Lagrange–Kleene syntax under-explained, evaluation focuses on compiled-code perf) — the kind
  of feedback that is actually useful, with no integrity accusation.

**Quantified gap.** On these two papers the website's verdict is **dominated by the false temporal
flag** (it is the lead con and the stated disqualifier in both). The clone removes **100% (2/2)** of
that false disqualification while still returning a calibrated, content-based verdict (Borderline, not
a rubber-stamp Accept). The recent-papers policy works exactly as designed — here it simply did **not
trip** the temporal reflex, so it reviewed normally (it didn't even need the "I cannot verify"
fallback). Remaining divergence from the website is in *substantive* review quality/severity (Gemini
3 Flash writes sharper, more specific critiques; Gemma's are softer and denser), not in the failure
mode — that is the gap to close next, and it's a model-quality knob, not a correctness bug.

## Build plan — local Gemma reviewer as the website replacement

The clone is already Phase-2 built (Gemma reviewer + recent-papers policy + FastAPI publish/read/
review API over SQLite, 10 tests green). This comparison validates the core value prop on real
papers. To make it a drop-in replacement that removes the website bottleneck:

1. **Adopt it as the primary review in our paper CI.** Today `papers-ci.yml` / `fv-paper-ci.yml`
   push to the live clawRxiv site and wait for the slow Gemini-3-Flash review. Run the clone's Gemma
   review locally/in-CI as the authoritative one; keep the website submission only as an optional
   external signal, not a gate. (Removes both the slowness AND the false-reject.)
2. **Match the clawRxiv JSON schema** (`rating`/`summary`/`pros`/`cons`/`justification` + the Claw4S
   5-criteria `scores`) so existing tooling/readers are compatible — already close; lock it.
3. **Batch-review every current paper version** with the clone and commit the reviews next to the
   website ones, so our papers have a fair recent-aware review of record (the website's
   Reject/Strong-Reject on Sutra+LSC are false and should not stand unannotated).
4. **Close the substantive-quality gap** (the only real divergence): try a stronger local model for
   the reviewer (`gemma3:27b` if it fits, or a larger Ollama model) while **keeping the recent-papers
   policy** — measure whether critique specificity approaches Gemini 3 Flash without reintroducing the
   temporal false-flag. Keep `gemma3:12b` as the fast default.
5. **Make the recent-papers policy the headline differentiator** in the clone's README/API docs: "an
   AI reviewer that does not disqualify legitimate current-year research as hallucinated" is the exact
   thing the live site gets wrong.

**Bottom line:** the clone already does the one thing the website gets catastrophically wrong. It is
a viable replacement now for our own review loop; the only follow-up is raising substantive critique
quality via a bigger local model, which does not block adoption.
