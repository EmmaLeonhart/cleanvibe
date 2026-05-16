"""Entry point CI (or a human) invokes to run the replication.

Writes metrics to results/metrics.json. Defaults are a *reduced-scale*
demonstration run (bounded steps) so it finishes quickly on CPU; pass
--steps for a longer run that can actually exhibit grokking.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grokking import train  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=67)
    ap.add_argument("--train-frac", type=float, default=0.5)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    results = Path(__file__).resolve().parents[1] / "results"
    results.mkdir(exist_ok=True)
    metrics_path = results / "metrics.json"
    t0 = time.time()

    def dump(history):
        metrics_path.write_text(json.dumps({
            "paper": "arXiv:2201.02177",
            "config": vars(args),
            "elapsed_seconds": round(time.time() - t0, 1),
            "final": history[-1],
            "history": history,
        }, indent=2), encoding="utf-8")

    history = train(
        p=args.p, train_frac=args.train_frac, steps=args.steps,
        lr=args.lr, weight_decay=args.weight_decay, seed=args.seed,
        on_log=dump,
    )
    dump(history)
    elapsed = round(time.time() - t0, 1)
    last = history[-1]

    print(f"done in {elapsed}s | step {last['step']} "
          f"train_acc={last['train_acc']} val_acc={last['val_acc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
