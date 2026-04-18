# An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale

**arXiv:** [2010.11929](https://arxiv.org/pdf/2010.11929v2)
**Authors:** Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, Neil Houlsby
**Published:** 2020-10-22T17:55:59Z

## Abstract

While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited. In vision, attention is either applied in conjunction with convolutional networks, or used to replace certain components of convolutional networks while keeping their overall structure in place. We show that this reliance on CNNs is not necessary and a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks. When pre-trained on large amounts of data and transferred to multiple mid-sized or small image recognition benchmarks (ImageNet, CIFAR-100, VTAB, etc.), Vision Transformer (ViT) attains excellent results compared to state-of-the-art convolutional networks while requiring substantially fewer computational resources to train.

## Replication status

Not started. See [`SKILL.md`](./SKILL.md) for the agent-executable replication plan.

## Layout

- `paper/` — the downloaded PDF (gitignored; populate with `python download_paper.py`).
- `paper.json` — frozen metadata pulled from the arXiv API.
- `SKILL.md` — instructions for an agent (or human) to carry out the replication.
- `download_paper.py` — fetches the PDF into `paper/`.
