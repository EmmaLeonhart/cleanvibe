# data_lake

Raw, unprocessed artifacts dropped in as-is — the landing zone for this project.
Nothing here is refined or schema'd; it's the pool things get fished out of later.

This project is **liturgical world modelling**. The premise: a **missal (order of
service) is a high-compression, lossy encoding of a ritual** — it records only enough
to cue people who already hold the conventions, and omits most of what actually
happens (postures, movements, processions, timing, roles, sung-vs-said, silences).
The goal is to **decompress missals into models of the ritual they encode** — what the
liturgy actually looks like when enacted. Direction for now is **missal → ritual**;
generating new liturgies is a possible later phase.

Source material is real missals (photographed pages + the official PDFs churches
publish). The "content and context" a missal leaves out is the decompression key: the
world knowledge the document assumes.

## Contents

Source missals (each folder = one missal). Both are the 10:30 Choral Eucharist at Christ
Church Cathedral, Vancouver, one week apart — a deliberate pair for separating the fixed
rite from what changes week to week:

- `missal-2026-07-05-proper-14/` — Proper 14 (July 5 2026). 12 photographed pages + the
  official published PDFs + cover-QR scan + a structural-notes render. See its `index.md`.
- `missal-2026-06-28-proper-13/` — Proper 13 (June 28 2026). The official PDFs, pulled
  from the church site. Notable: this missal **prints the sacring bell** that Proper 14
  omits. See its `index.md`.

Derived from these missals (elsewhere in the repo):
- `../models/` — the decompressed **ritual models** (one `.ritual.json` per missal), the
  `ritual.schema.json`, the renderer, and `comparison-proper-13-vs-14.md`.
- `../context/` — RAG-gathered, cited reference on the parish's actual practice and the
  BAS/EOW rubrics — the "decompression key" for turning these missals into rituals.
