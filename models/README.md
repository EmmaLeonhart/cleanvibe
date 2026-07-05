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
    (with a `convention` field naming the basis).
- `ccc-2026-07-05-proper-14.ritual.json` — first worked example: the Proper 14 Choral
  Eucharist (`data_lake/missal-2026-07-05-proper-14/`) decompressed into 41 events.

## What the first example shows

Validated against the schema. Of 41 events: **21 printed, 14 pointer, 6 inferred.** The
inferred events are exactly what the missal compresses out — the entrance and Gospel and
recessional processions, the fraction gesture, the institution narrative's manual acts —
none printed, all enacted. Posture (stand/sit/kneel/process) is filled on every event
though the missal prints almost none of it. That gap between printed and inferred is the
measure of the missal's compression, and reconstructing it is the modelling work.

## Validate

```
python3 -c "import json,jsonschema; jsonschema.validate(
  json.load(open('models/ccc-2026-07-05-proper-14.ritual.json')),
  json.load(open('models/ritual.schema.json'))); print('valid')"
```
