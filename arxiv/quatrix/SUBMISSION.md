# Quatrix — arXiv submission sheet

Upload: `quatrix-arxiv.tar.gz` (LaTeX source rebuilt from the Zenodo PDF,
10.5281/zenodo.19839718; compiles with pdfLaTeX to the same 32 pages).

| Field | Value |
|---|---|
| Title | Quatrix: An Empirical Evaluation of Q-Compass and SAVO on Multimodal Sequence Modeling |
| Authors | Syed Abdur Rehman Ali |
| Primary category | cs.LG |
| Cross-list (optional) | cs.CL |
| License | CC BY 4.0 (same as the Zenodo record) |
| Comments | 32 pages, 18 figures, 11 tables. Code: https://github.com/Abd0r/quatrix |
| Journal-ref / DOI | leave empty (Zenodo is not a journal) |

## Metadata abstract (form limit 1,920 characters)

The paper's own abstract is about 2,480 characters, so it does not fit the
arXiv form field. The text below (1,754 characters) is a **draft condensed
version**: clauses cut and a few sentences merged, no new claims, all numbers
unchanged. The author should approve it before submission. The PDF keeps the
full abstract.

```
We evaluate Q-Compass - a value-projection-free attention primitive grounded in the reinforcement-learning Q-function - at three parameter scales (57M, 121M, 179M) across four modalities (WikiText-103, MS-COCO captions, LibriSpeech clean-100, MiniGrid 3D navigation). We evaluate the SAVO four-projection variant in which the V projects the state-action product instead of the raw input, and report multi-head Q-Compass (MH-QC) as a null result. Text-LM parity (controlled ablation): SAVO sits +12.33 +/- 0.87 perplexity above the rank-matched transformer at 60m (paired-difference, 4 seeds, p = 7.6e-4); full-rank 8-head MHA at the same recipe reaches 257.96 +/- 2.12 val ppl, and SAVO is +5.79 ppl above it. The same ~12-ppl gap to rank-matched holds at 120m and 180m (single seed each). Cross-modal non-interference: at matched text compute, joint four-modality training reaches the same per-text-token loss as text-only training, through 180m. Out-of-distribution: the 60m W_V-free SAO has a small OOD edge on arxiv and pubmed that does not replicate at 120m or 180m; we report this as a null result. Cross-field demonstration: the same SAVO block class runs on four computational-oncology tasks - signature decomposition (cosine 0.975 vs NNLS 0.987, NNLS higher), 27-class pan-cancer (top-1 0.517 vs majority 0.087), GDSC2 drug-response (Pearson 0.903; drug-only baseline 0.864), and TCGA 5-year survival (C-index 0.701; clinical-only 0.708, within seed noise). World-model branch: world MSE drops from 1.125 to 0.071 over 10,000 steps while training concurrently with text/vision/audio; the predict-mean baseline is 0.033, reflecting MiniGrid-Empty-8x8's low next-state variance. The unification claim is a structural property of the routing block.
```

## Before submitting

- arXiv's third-party submission rules require the metadata to be validated by
  an author, and a corresponding-author email on the submission.
- The author name on Zenodo is "Ali, Abdur Rehman"; the PDF says
  "Syed Abdur Rehman Ali". The form above uses the PDF's version.
