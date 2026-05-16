# Findings — Replicating *Grokking* (arXiv:2201.02177)

> This is a **cleanvibe worked example**: a real run of the `cleanvibe
> replicate` pipeline, kept in-repo so the replication website has a genuine
> example. It is a *reduced-scale demonstration*, framed honestly below per
> the `SKILL.md` budget guardrails — not a claim of full reproduction.

## Paper

Power, Burda, Edwards, Babuschkin, Misra — *Grokking: Generalization Beyond
Overfitting on Small Algorithmic Datasets* (2022). Headline phenomenon:
on small algorithmic datasets a network first **memorizes** the training set
(train accuracy → ~100%, validation near chance), then — long after
overfitting, with weight decay — **suddenly generalizes** (validation
accuracy → ~100%). The delay can span orders of magnitude more optimizer
steps than memorization.

## What was run

Faithful minimal setup (`src/grokking.py`, `scripts/run.py`):

- Task: modular addition `(a + b) mod p`, `p = 67`, as a sequence model over
  tokens `[a, b, "="]` predicting the result token.
- 50% of all `p·p` pairs for training, 50% held out for validation.
- Tiny decoder-only transformer (1 layer, d_model 64, 4 heads), full-batch
  AdamW, **weight_decay = 1.0** (the ingredient the paper identifies as
  critical for grokking).
- **300 optimizer steps**, ~20 s on CPU (bounded demonstration run).

## Reproduced vs. reported

| Quantity | Paper (qualitative) | This reduced-scale run (step 300) |
|---|---|---|
| Train accuracy | → ~1.00 (memorization) | **0.706** (rising — memorizing) |
| Validation accuracy | → ~1.00 *eventually*, after a long delay | **0.127** (still near-chance) |
| Train/val gap | Large, then closes abruptly ("grokking") | Large and **open** — pre-grokking regime |

The trajectory (`results/metrics.json`, 16 logged points) shows train
accuracy climbing steadily while validation stays near chance — i.e. the
**memorization-before-generalization** phase that *precedes* grokking. The
setup and the onset of the characteristic gap reproduce cleanly.

## Gaps and honest divergence

- **Grokking itself (the delayed generalization) was not reached here.** The
  paper's grokking transition occurs after train accuracy saturates and
  typically requires on the order of 10^4–10^5 optimizer steps; this demo
  runs 300. This is an intentional, documented reduced-scale variant, not a
  negative result about the paper.
- To actually observe the transition, run longer:
  `python scripts/run.py --steps 60000 --p 97`. Compute envelope: minutes on
  a single consumer GPU; impractical as a default CPU CI job (so this is
  marked **not CI-runnable at full scale** — CI runs the bounded demo only).
- Single seed, single `p`; the paper sweeps data fractions and operations.

## Definition of done (for this worked example)

- ✅ `cleanvibe replicate` scaffolded this project from the live arXiv link.
- ✅ Paper downloaded via `download_paper.py` (`replication_target/paper.pdf`,
  gitignored; the project itself is tracked in the cleanvibe repo).
- ✅ Faithful reimplementation runs end-to-end from a clean checkout and
  reports a headline quantity (train/val accuracy) with reproduced values.
- ✅ Divergence (no full grokking at 300 steps) documented honestly with the
  command and compute envelope to reach it.
