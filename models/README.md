# models — decompressed rituals

Derived output of the project: **missals decompressed into models of the ritual they
encode.** Where `data_lake/` holds the raw, high-compression source (missals), this
folder holds the low-compression target (the enacted service, made explicit).

## Files

- `ritual.schema.json` — JSON Schema (draft 2020-12) defining the ritual model. A ritual
  is an ordered list of **events**; each event records actor(s), action, mode
  (spoken/sung/silent/…), assembly posture, station (location), content (literal text,
  a pointer into an external book, or a dialogue), and — the key field — **`provenance`**:
  - `printed` — literal text/rubric present in the missal;
  - `pointer` — a reference the missal prints (hymn no., lection citation, named setting)
    whose target lives in an external book;
  - `inferred` — **not in the missal at all**, supplied by decompressing convention
    (with a `convention` field naming the basis, now carrying BAS/EOW citations).
  Each model's `meta.authorities` lists the rubric sources behind its inferences.
- `ccc-2026-07-05-proper-14.ritual.json` — Proper 14 (July 5), 42 events.
- `ccc-2026-06-28-proper-13.ritual.json` — Proper 13 (June 28), 40 events.
- `render_ritual.py` — turns a `.ritual.json` into a human-readable **enacted script**,
  provenance-annotated (printed / pointer / inferred colour-coded, inferred rows shaded
  with their citation). Writes `.rendered.html` + `.rendered.pdf`.
  Usage: `python3 models/render_ritual.py models/<file>.ritual.json`.
- `comparison-proper-13-vs-14.md` — the two missals side by side: the fixed ordinary frame
  vs. the proper, and how the missal's own compression varies week to week.
- `../context/` — cited real-world grounding (parish practice + BAS/EOW rubrics).

## What the examples show

Both validate against the schema. Provenance split — Proper 14: **21 printed, 14 pointer,
7 inferred** (42); Proper 13: **24 printed, 12 pointer, 4 inferred** (40). The inferred
events are exactly what the missal compresses out — entrance/Gospel/recessional
processions, the fraction gesture, the institution's manual acts, and (for Proper 14) the
sacring bell. Posture is filled on every event though the missals print almost none of it.
That gap between printed and inferred is the measure of a missal's compression, and
reconstructing it is the modelling work.

The pair is the real payoff: **Proper 13 prints the sacring bell that Proper 14 omits**, so
one missal decompresses the other — the P14 bell is an `inferred` event whose `convention`
cites the P13 missal. Comparing sibling missals is the cheapest decompression source there
is.

## Validate

```
python3 -c "import json,jsonschema; jsonschema.validate(
  json.load(open('models/ccc-2026-07-05-proper-14.ritual.json')),
  json.load(open('models/ritual.schema.json'))); print('valid')"
```
