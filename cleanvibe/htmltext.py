"""Stdlib HTML -> Markdown for replication papers downloaded from a web URL.

A paper page saved as ``paper.html`` is expensive to read: scripts, styles,
navigation and figures inlined as base64 data URIs. ``html_to_markdown`` keeps
the text and its structure (headings, paragraphs, lists, links, code, simple
tables) and drops the rest, so the agent reads ``paper.md`` instead.

This file is also embedded verbatim in the generated ``download_paper.py``
(``templates.url_download_paper_py``), so it must stay self-contained: stdlib
imports only, no imports from cleanvibe.
"""

import re as _re
from html.parser import HTMLParser as _HTMLParser

# Elements whose whole content is dropped.
_SKIP = {"script", "style", "noscript", "nav", "header", "footer", "svg",
         "button", "form", "iframe", "template", "math"}
_BLOCK = {"p", "div", "section", "article", "main", "figure", "figcaption",
          "blockquote", "table", "tr", "ul", "ol", "dl", "dt", "dd", "br", "hr"}
_HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}


class _Converter(_HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0
        self.pre = 0
        self.lists = []
        self.href = None
        self.link_text = []
        self.cells = None
        self.rows = 0

    def _emit(self, text):
        if self.href is not None:
            self.link_text.append(text)
        elif self.cells is not None:
            if not self.cells:
                self.cells.append([])
            self.cells[-1].append(text)
        else:
            self.out.append(text)

    def _block(self):
        self.out.append("\n\n")

    def handle_starttag(self, tag, attrs):
        if self.skip or tag in _SKIP:
            if tag in _SKIP:
                if not self.skip and tag == "math":
                    # arXiv/LaTeXML HTML keeps the LaTeX in alttext.
                    tex = _squash(dict(attrs).get("alttext") or "")
                    if tex:
                        self._emit(f"${tex}$")
                self.skip += 1
            return
        a = dict(attrs)
        if tag in _HEADINGS:
            self._block()
            self.out.append("#" * _HEADINGS[tag] + " ")
        elif tag == "pre":
            self._block()
            self.out.append("```\n")
            self.pre += 1
        elif tag == "code" and not self.pre:
            self._emit("`")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag in ("ul", "ol"):
            if not self.lists:
                self._block()
            self.lists.append([tag, 0])
        elif tag == "li":
            depth = max(len(self.lists) - 1, 0)
            kind = self.lists[-1] if self.lists else ["ul", 0]
            kind[1] += 1
            bullet = f"{kind[1]}." if kind[0] == "ol" else "-"
            self.out.append("\n" + "  " * depth + bullet + " ")
        elif tag == "a" and a.get("href") and not a["href"].startswith(("#", "javascript:")):
            self.href = a["href"]
            self.link_text = []
        elif tag == "img":
            alt = (a.get("alt") or "").strip()
            if alt:
                self._emit(f"[image: {alt}]")
        elif tag == "table":
            self.rows = 0
            self._block()
        elif tag == "tr":
            self.cells = []
        elif tag in ("td", "th") and self.cells is not None:
            self.cells.append([])
        elif tag in _BLOCK:
            self._block()

    def handle_endtag(self, tag):
        if self.skip:
            if tag in _SKIP:
                self.skip -= 1
            return
        if tag in _HEADINGS:
            self._block()
        elif tag == "pre" and self.pre:
            self.pre -= 1
            self.out.append("\n```")
            self._block()
        elif tag == "code" and not self.pre:
            self._emit("`")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag in ("ul", "ol") and self.lists:
            self.lists.pop()
            if not self.lists:
                self._block()
        elif tag == "a" and self.href is not None:
            text = _squash("".join(self.link_text)) or self.href
            href, self.href = self.href, None
            self._emit(f"[{text}]({href})")
        elif tag == "tr" and self.cells is not None:
            row = [_squash("".join(c)).replace("|", "\\|") for c in self.cells]
            self.cells = None
            if any(row):
                self.out.append("\n| " + " | ".join(row) + " |")
                self.rows += 1
                if self.rows == 1:
                    self.out.append("\n|" + "---|" * len(row))
        elif tag in _BLOCK:
            self._block()

    def handle_data(self, data):
        if self.skip:
            return
        if self.pre:
            self.out.append(data)
        else:
            self._emit(_re.sub(r"\s+", " ", data))


def _squash(text):
    return _re.sub(r"\s+", " ", text).strip()


def html_to_markdown(source):
    """Convert an HTML page (str) to readable Markdown (str)."""
    conv = _Converter()
    conv.feed(source)
    conv.close()
    text = "".join(conv.out)
    # Drop stray inline data URIs that survived as text.
    text = _re.sub(r"data:[\w/+.-]+;base64,[A-Za-z0-9+/=]{40,}", "", text)
    lines, fenced = [], False
    for ln in text.split("\n"):
        if ln.startswith("```"):
            fenced = not fenced
        elif not fenced and not _re.match(r"\s*(?:-|\d+\.) ", ln):
            ln = ln.lstrip()
        lines.append(ln.rstrip())
    text = "\n".join(lines)
    text = _re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"
