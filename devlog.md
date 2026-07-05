# cleanvibe — Devlog

**This file is where "done" lives.** `queue.md` is delete-only: when a queue
item is finished, the item is **deleted from `queue.md`** and a dated entry
is **appended here**, in the same commit as the work, then pushed. Never
tick a box in place — a checked box left in `queue.md` is the failure mode
this file exists to prevent.

Also record releases (tag + a one-line note), notable milestones, and
anything else worth a chronological trail. Newest entries at the bottom.

This is the **same convention as the cleanvibe repo's own `devlog.md`** —
every cleanvibe-scaffolded project gets one for the same reason.

See `CLAUDE.md` § "Workflow Rules" and `queue.md`'s preamble.

---

## 2026-07-05 — Project scaffolded

Scaffolded with `cleanvibe new` (cleanvibe v1.17.0). Future entries
land here as queue items get deleted.

## 2026-07-05 — First missal ingested + first ritual model

Ingested the first source missal into `data_lake/missal-2026-07-05-proper-14/`:
Christ Church Cathedral (Vancouver) Choral Eucharist, Proper 14 — the whole 12-page
order of service as one missal (12 photographed pages + the official published PDFs
pulled from the Cathedral site + a QR-scan trail + a structural-notes render).

Established the project premise: a missal is a lossy, high-compression encoding of a
ritual; the work is decompressing missal → ritual. Built `models/ritual.schema.json`
(events with actor/action/mode/posture/station/content + a `provenance` field:
printed / pointer / inferred) and decompressed the Proper 14 missal into
`models/ccc-2026-07-05-proper-14.ritual.json` — 41 events (21 printed, 14 pointer,
6 inferred), validates against the schema. Renamed the folder bulletin→missal per
the "entire thing is a single missal" framing.

## 2026-07-05 — Second missal, renderer, agentic RAG, cross-missal comparison

Expanded from one missal to a small corpus + tooling:
- **Second missal:** pulled the Proper 13 (June 28) Choral Eucharist PDFs from the church
  site into `data_lake/missal-2026-06-28-proper-13/`, and decompressed it into
  `models/ccc-2026-06-28-proper-13.ritual.json` (40 events). Key finding: this missal
  PRINTS "Ringing of the bell. (x3)" — the sacring bell Proper 14 omits — so one missal
  decompresses another.
- **Renderer:** `models/render_ritual.py` turns any `.ritual.json` into a provenance-
  annotated enacted script (HTML + PDF), inferred rows shaded with their citation.
- **Agentic RAG:** two research agents gathered cited context, saved under `context/`:
  parish practice (Broad Church → incense at Compline not the Eucharist; Topping is a VST
  guest preacher; Robertson/Quartet are summer stand-ins for Cockburn/Cathedral Choir) and
  BAS/EOW rubrics (page-cited postures, processions, manual acts, fraction, dismissal).
  Folded citations into each model's inferred `convention` fields + `meta.authorities`.
- **Deepened Proper 14:** added the sacring bell as a justified `inferred` event (cites the
  P13 missal) → 42 events. Corrected attributions from the RAG findings.
- **Comparison:** `models/comparison-proper-13-vs-14.md` separates the fixed ordinary frame
  from the proper and documents how the missal's compression varies week to week.
