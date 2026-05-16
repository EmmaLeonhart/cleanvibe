"""Minimal, faithful reimplementation of the Grokking setup.

Paper: "Grokking: Generalization Beyond Overfitting on Small Algorithmic
Datasets" (Power et al., 2022, arXiv:2201.02177).

Task: learn modular addition  (a + b) mod p  as a sequence model. Every pair
(a, b) with 0 <= a, b < p is an example; the model sees the token sequence
[a, b, "="] and must predict the result token. A fixed fraction of all p*p
pairs is used for training, the rest for validation. The paper's key
ingredients for the grokking phenomenon are (1) heavy weight decay and
(2) training far past the point of memorising the train set.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn


def make_dataset(p: int, train_frac: float, seed: int):
    a = np.repeat(np.arange(p), p)
    b = np.tile(np.arange(p), p)
    y = (a + b) % p
    eq = np.full_like(a, p)  # the "=" token id is p
    x = np.stack([a, b, eq], axis=1)  # [N, 3]

    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(x))
    n_train = int(len(x) * train_frac)
    tr, va = perm[:n_train], perm[n_train:]
    to_t = lambda arr: torch.tensor(arr, dtype=torch.long)
    return (to_t(x[tr]), to_t(y[tr])), (to_t(x[va]), to_t(y[va]))


class TinyTransformer(nn.Module):
    """A small decoder-only transformer; predicts from the final position."""

    def __init__(self, vocab: int, d_model: int = 64, n_layers: int = 1,
                 n_heads: int = 4, seq_len: int = 3):
        super().__init__()
        self.tok = nn.Embedding(vocab, d_model)
        self.pos = nn.Embedding(seq_len, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model, n_heads, dim_feedforward=4 * d_model,
            batch_first=True, activation="gelu",
        )
        self.blocks = nn.TransformerEncoder(layer, n_layers)
        self.head = nn.Linear(d_model, vocab)

    def forward(self, x):
        pos = torch.arange(x.shape[1], device=x.device)
        h = self.tok(x) + self.pos(pos)[None]
        h = self.blocks(h)
        return self.head(h[:, -1])  # logits at the final ("=") position


@torch.no_grad()
def accuracy(model, x, y) -> float:
    model.eval()
    pred = model(x).argmax(-1)
    return (pred == y).float().mean().item()


def train(p=67, train_frac=0.5, steps=300, lr=1e-3, weight_decay=1.0,
          seed=0, log_every=20, on_log=None):
    """Run a (reduced-scale) grokking experiment.

    ``on_log(history)`` is called at every log point with the history so far,
    so the caller can persist partial results (a bounded CPU demo may be cut
    short). Returns the full metric history.
    """
    torch.manual_seed(seed)
    (xtr, ytr), (xva, yva) = make_dataset(p, train_frac, seed)
    model = TinyTransformer(vocab=p + 1)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.CrossEntropyLoss()

    history = []
    for step in range(1, steps + 1):
        model.train()
        opt.zero_grad()
        loss = loss_fn(model(xtr), ytr)  # full-batch GD (small dataset)
        loss.backward()
        opt.step()
        if step % log_every == 0 or step == 1:
            history.append({
                "step": step,
                "train_loss": round(loss.item(), 5),
                "train_acc": round(accuracy(model, xtr, ytr), 4),
                "val_acc": round(accuracy(model, xva, yva), 4),
            })
            if on_log is not None:
                on_log(history)
    return history
