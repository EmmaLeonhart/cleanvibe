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

- `bulletin-2026-07-05-proper-14/` — a complete Choral Eucharist missal from Christ
  Church Cathedral, Vancouver (Proper 14, July 5 2026): 12 photographed pages, the
  official published PDFs (bulletin, readings, evening prayer), the cover-QR scan, and
  a first-pass structural model. See that folder's `index.md` for the liturgy outline,
  ministers, sources, and modelling notes.
