#!/usr/bin/env python3
"""
render_ritual.py — turn a .ritual.json (see ritual.schema.json) into a human-readable
enacted script, provenance-annotated so you can see at a glance what the missal printed
vs. what was decompressed from convention.

Usage:
    python3 models/render_ritual.py models/<file>.ritual.json [out_basename]

Writes <out_basename>.html next to the input (default: same name, .rendered.html).
If Chromium is found, also writes <out_basename>.pdf.

No third-party deps (stdlib only) so it runs anywhere.
"""
import json, sys, os, html, subprocess, glob

PROV = {
    "printed": ("PRINTED", "in the missal, verbatim"),
    "pointer": ("POINTER", "a reference the missal prints; target lives in an external book"),
    "inferred": ("INFERRED", "not in the missal — decompressed from convention"),
}
POSTURE_GLYPH = {"stand": "↑ stand", "sit": "• sit", "kneel": "⤓ kneel",
                 "process": "→ process", "bow": "⤈ bow", None: ""}
SECTION_TITLE = {"gathering": "I · The Gathering of the Community",
                 "word": "II · The Proclamation of the Word",
                 "eucharist": "III · The Celebration of the Eucharist",
                 "sending": "IV · The Sending Forth"}

def esc(s): return html.escape(str(s)) if s is not None else ""

def content_html(c, roles):
    if not c: return ""
    t = c.get("type")
    if t == "text":
        return f'<div class="text">{esc(c.get("text",""))}</div>'
    if t == "dialogue":
        rows = "".join(
            f'<div class="vr"><span class="by">{esc(roles.get(d.get("by"), d.get("by","")))}</span>'
            f'<span class="says">{esc(d.get("says",""))}</span></div>'
            for d in c.get("dialogue", []))
        return f'<div class="dialogue">{rows}</div>'
    if t == "pointer":
        p = c.get("pointer", {})
        bits = [b for b in [p.get("title"), p.get("ref"), p.get("source")] if b]
        kind = p.get("kind", "ref")
        out = (f'<div class="pointer">▸ <span class="pk">{esc(kind)}</span> '
               f'{esc(" · ".join(bits))}</div>')
        # full text decompressed from the QR-linked source, shown under the citation
        if c.get("text"):
            out += (f'<div class="fulltext"><span class="ft-tag">full text (via QR)</span>'
                    f'{esc(c["text"])}</div>')
        return out
    return ""

def render(data):
    roles = {r["id"]: r["label"] for r in data.get("roles", [])}
    role_short = {r["id"]: r["label"].split(" (")[0] for r in data.get("roles", [])}
    stations = {s["id"]: s["label"] for s in data.get("stations", [])}
    m = data.get("meta", {})
    cal = m.get("calendar", {})
    events = sorted(data.get("events", []), key=lambda e: e["seq"])

    # provenance tally
    tally = {}
    for e in events:
        tally[e["provenance"]] = tally.get(e["provenance"], 0) + 1
    tally_str = " · ".join(f'{PROV[k][0].lower()}: {v}' for k, v in
                           sorted(tally.items(), key=lambda kv: -kv[1]))

    mins = "".join(f"<b>{esc(k)}:</b> {esc(v)}<br>" for k, v in m.get("ministers", {}).items())
    settings = "".join(f"<li>{esc(s)}</li>" for s in m.get("music_settings", []))

    rows = []
    cur = None
    for e in events:
        if e["section"] != cur:
            cur = e["section"]
            rows.append(f'<tr class="sec"><td colspan="4">{esc(SECTION_TITLE.get(cur, cur))}</td></tr>')
        prov = e["provenance"]
        actors = ", ".join(role_short.get(a, a) for a in e.get("actor", [])) or "&mdash;"
        posture = POSTURE_GLYPH.get(e.get("assembly_posture"), esc(e.get("assembly_posture") or ""))
        station = stations.get(e.get("station"), "")
        conv = (f'<div class="conv"><b>inferred from:</b> {esc(e["convention"])}</div>'
                if prov == "inferred" and e.get("convention") else "")
        note = f'<div class="note">{esc(e["notes"])}</div>' if e.get("notes") else ""
        src = e.get("missal_source")
        srcbadge = f'<span class="src">{esc(src)}</span>' if src else '<span class="src none">not printed</span>'
        rows.append(
            f'<tr class="ev {prov}">'
            f'<td class="seq">{e["seq"]}</td>'
            f'<td class="who"><div class="actor">{actors}</div>'
            f'<div class="posture">{posture}</div>'
            f'{("<div class=st>"+esc(station)+"</div>") if station else ""}</td>'
            f'<td class="body"><div class="unit">{esc(e["unit"])} '
            f'<span class="action">[{esc(e["action"])}/{esc(e.get("mode",""))}]</span></div>'
            f'{content_html(e.get("content"), role_short)}{conv}{note}</td>'
            f'<td class="prov"><span class="badge {prov}">{PROV[prov][0]}</span>{srcbadge}</td>'
            f'</tr>')

    return f"""<style>
 @page {{ size: Letter; margin: 16mm 14mm; }}
 * {{ box-sizing: border-box; }}
 body {{ font-family: Georgia, 'Times New Roman', serif; color:#1a1a1a; font-size:10.5pt; line-height:1.4; }}
 h1 {{ font-size: 20pt; margin:0 0 2pt; }}
 .sub {{ color:#555; font-style:italic; margin:0 0 8pt; }}
 .head {{ border-bottom:2px solid #333; padding-bottom:8pt; margin-bottom:8pt; }}
 .metagrid {{ display:flex; gap:18pt; font-size:9pt; color:#444; flex-wrap:wrap; }}
 .metagrid ul {{ margin:2pt 0; padding-left:14pt; }}
 .legend {{ font-size:8.5pt; margin:6pt 0 10pt; color:#555; }}
 .legend .badge {{ margin-right:3px; }}
 table {{ border-collapse:collapse; width:100%; }}
 td {{ vertical-align:top; padding:5px 7px; border-bottom:1px solid #e4e4e4; }}
 tr.sec td {{ background:#2b2b2b; color:#fff; font-size:11pt; font-weight:bold;
             letter-spacing:.4px; padding:6px 8px; border:none; }}
 .seq {{ width:20px; color:#999; font-size:8.5pt; }}
 .who {{ width:150px; }}
 .actor {{ font-weight:bold; font-size:9.5pt; }}
 .posture {{ color:#7a1414; font-size:8.5pt; }}
 .st {{ color:#2e5a7a; font-size:8pt; font-style:italic; }}
 .unit {{ font-weight:bold; }}
 .action {{ font-weight:normal; color:#999; font-size:8pt; }}
 .text {{ margin-top:2px; }}
 .pointer {{ margin-top:2px; color:#1c5b8c; }}
 .pk {{ font-variant:small-caps; font-size:8.5pt; color:#555; }}
 .fulltext {{ margin-top:4px; padding:5px 9px; background:#eef4f8; border-left:3px solid #1c5b8c;
             color:#233; font-size:9pt; line-height:1.35; }}
 .ft-tag {{ display:block; font-variant:small-caps; font-size:7.5pt; letter-spacing:.5px;
           color:#1c5b8c; margin-bottom:2px; }}
 .dialogue {{ margin-top:2px; }}
 .vr {{ display:flex; gap:8px; margin:1px 0; }}
 .vr .by {{ min-width:64px; font-style:italic; color:#555; font-size:8.5pt; }}
 .conv {{ margin-top:3px; background:#f7f0dc; border-left:3px solid #b08d2e; padding:3px 7px; font-size:8.5pt; }}
 .note {{ margin-top:3px; color:#666; font-size:8.5pt; font-style:italic; }}
 .prov {{ width:78px; text-align:right; }}
 .badge {{ display:inline-block; font-size:7.5pt; font-weight:bold; letter-spacing:.4px;
           padding:1px 5px; border-radius:3px; color:#fff; }}
 .badge.printed {{ background:#3a3a3a; }}
 .badge.pointer {{ background:#1c5b8c; }}
 .badge.inferred {{ background:#b08d2e; }}
 .src {{ display:block; font-size:7.5pt; color:#999; margin-top:3px; }}
 .src.none {{ color:#b08d2e; font-style:italic; }}
 tr.ev.inferred {{ background:#fcf9f0; }}
</style>
<div class="head">
 <h1>{esc(m.get('title','Ritual'))}</h1>
 <p class="sub">{esc(m.get('rite',''))} &middot; {esc(m.get('date',''))} &middot; {esc(m.get('tradition',''))}</p>
 <div class="metagrid">
  <div><b>Calendar:</b> {esc(cal.get('proper_local',''))}
       ({esc(cal.get('proper_rcl',''))}); {esc(cal.get('lectionary_year',''))}, {esc(cal.get('track',''))}</div>
  <div>{mins}</div>
  <div><b>Music settings:</b><ul>{settings}</ul></div>
 </div>
 <div class="legend">Enacted script, decompressed from the missal. Provenance of each event:
  <span class="badge printed">PRINTED</span> in the missal &nbsp;
  <span class="badge pointer">POINTER</span> reference resolved elsewhere &nbsp;
  <span class="badge inferred">INFERRED</span> not printed &mdash; from convention (shaded rows).
  &nbsp;&mdash;&nbsp; <b>this service:</b> {tally_str}.</div>
</div>
<table>{''.join(rows)}</table>
"""

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    inp = sys.argv[1]
    data = json.load(open(inp, encoding="utf-8"))
    base = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(inp)[0] + ".rendered"
    out_html = base + ".html"
    open(out_html, "w", encoding="utf-8").write(render(data))
    print("wrote", out_html)
    # try chromium -> pdf
    cands = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")
    if cands:
        pdf = base + ".pdf"
        subprocess.run([cands[0], "--headless", "--no-sandbox", "--disable-gpu",
                        "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                        "file://" + os.path.abspath(out_html)],
                       stderr=subprocess.DEVNULL, timeout=120)
        if os.path.exists(pdf):
            print("wrote", pdf)

if __name__ == "__main__":
    main()
