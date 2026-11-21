"""Render the papers to the site: pages/paper/ (an index), pages/paper/hook/, pages/paper/replay/.

Run after a paper changes, then commit pages/ (the Pages workflow deploys it):

    python paper/scripts/render_pages.py

Stdlib only. The Markdown is the small subset the papers use: headings, paragraphs,
`-` and `1.` lists, pipe tables, `code`, **bold**, *italic* and [links](url).
The page shell (nav, theme toggle, styles) is paper/scripts/page_shell.html, made from
the first paper page.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "pages" / "paper"

PAPERS = [
    # (slug, source folder, clawRxiv paper id of the latest version, status line)
    ("replay", "paper-replay", "2611.02943",
     "Version 4 on clawRxiv. Its AI review has not come back yet."),
    ("hook", "paper", "2610.02907",
     "Version 4 on clawRxiv. Its AI review rated it Reject; the replay paper is the follow-up "
     "that tests the hook under control."),
]
OLD_NOTE = ("forgotten-duties", "Forgotten duties: auditing how coding agents maintain their own "
            "context in a queue-driven autonomous loop", "2610.02901")


def inline(text: str) -> str:
    out, pos = [], 0
    for m in re.finditer(r"`([^`]+)`", text):
        out.append(_inline_plain(text[pos:m.start()]))
        out.append(f"<code>{html.escape(m.group(1))}</code>")
        pos = m.end()
    out.append(_inline_plain(text[pos:]))
    return "".join(out)


def _inline_plain(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\"'>=])(https?://[^\s<)]+[^\s<).,;:])", r'<a href="\1">\1</a>', text)
    return text


def _row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def render(md: str) -> tuple[str, str, str]:
    """(title, abstract paragraph HTML, body HTML) for a paper's Markdown."""
    lines = md.replace("\r\n", "\n").split("\n")
    title, body, abstract = "", [], ""
    i, section = 0, ""
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            i += 1
            continue
        if line.startswith("## "):
            section = line[3:].strip()
            body.append(f"<h2>{inline(section)}</h2>")
            i += 1
            continue
        if line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            head = _row(rows[0])
            data = [_row(r) for r in rows[1:] if not re.fullmatch(r"[\s|:-]+", r)]
            t = ["<div class='tbl'><table><thead><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in data:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            body.append("".join(t))
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+", line)
        if m:
            tag = "ol" if m.group(2)[0].isdigit() else "ul"
            items = []
            while i < len(lines) and lines[i].strip():
                mm = re.match(r"^\s*([-*]|\d+\.)\s+(.*)$", lines[i])
                if mm:
                    items.append(mm.group(2))
                elif items:
                    items[-1] += " " + lines[i].strip()
                i += 1
            body.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") \
                and not lines[i].lstrip().startswith("|") \
                and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
            para.append(lines[i].strip())
            i += 1
        p = inline(" ".join(para))
        if section == "Abstract" and not abstract:
            abstract = p
        body.append(f"<p>{p}</p>")
    return title, abstract, "\n".join(body)


def shell(title: str, description: str, url: str, eyebrow: str, byline: str,
          links: str, article: str, note: str) -> str:
    head = (ROOT / "paper" / "scripts" / "page_shell.html").read_text(encoding="utf-8")
    return (head.replace("{{TITLE}}", html.escape(title))
                .replace("{{DESCRIPTION}}", html.escape(description))
                .replace("{{URL}}", url)
                .replace("{{EYEBROW}}", eyebrow)
                .replace("{{BYLINE}}", byline)
                .replace("{{LINKS}}", links)
                .replace("{{ARTICLE}}", article)
                .replace("{{NOTE}}", note))


def _plain(fragment: str, limit: int = 300) -> str:
    text = re.sub(r"<[^>]+>", "", fragment)
    text = html.unescape(text)
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + " ..."


def main() -> int:
    cards = []
    for slug, folder, paper_id, status in PAPERS:
        md = (ROOT / folder / "paper.md").read_text(encoding="utf-8")
        title, abstract, body = render(md)
        src = f"https://github.com/EmmaLeonhart/cleanvibe/blob/main/{folder}/paper.md"
        links = (f'<a class="btn" href="https://www.clawrxiv.io/abs/{paper_id}">clawRxiv {paper_id}</a>\n'
                 f'      <a class="btn" href="{src}">Source</a>\n'
                 f'      <a class="btn" href="/paper/">All papers</a>')
        page = shell(title, _plain(abstract), f"https://cleanvibe.emmaleonhart.com/paper/{slug}/",
                     "Research paper · Claw4S", "Emma Leonhart and Claw", links, body,
                     html.escape(status) + " This page is built from the paper's source in the "
                     "cleanvibe repository.")
        out = PAGES / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        cards.append(f'<h2><a href="/paper/{slug}/">{inline(title)}</a></h2>\n'
                     f"<p>{abstract}</p>\n<p class='byline'>{html.escape(status)}</p>")
    slug, title, paper_id = OLD_NOTE
    cards.append(f'<h2><a href="/paper/{slug}/">{html.escape(title)}</a></h2>\n'
                 f"<p>The first audit, from October 2026: duties whose cue arrives in the agent's "
                 f"context are kept, duties it has to notice lapse. Both papers above follow from it "
                 f"(clawRxiv {paper_id}).</p>")
    index = shell("cleanvibe papers", "Research on how coding agents keep their own context in "
                  "cleanvibe's autonomous loop.", "https://cleanvibe.emmaleonhart.com/paper/",
                  "Research · Claw4S", "Emma Leonhart and Claw", "", "\n".join(cards),
                  "Newest first. Each paper is posted to clawRxiv, whose AI review is part of the "
                  "loop that revises it.")
    (PAGES / "index.html").write_text(index, encoding="utf-8")
    print("wrote", ", ".join(str(p.relative_to(ROOT)) for p in sorted(PAGES.rglob("index.html"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
