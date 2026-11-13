"""Extract paper text from a path, dispatching on file type.

`extract_text` lets the review CLI accept more than `.md`: markdown/text pass
through unchanged, `.tex` is lightly de-LaTeXed into something
`parse_markdown_paper` can read (title + sections + body), and `.pdf` is run
through `pypdf` if it is installed. The output is plain markdown-ish text — the
first `# H1` becomes the title, the first blank-line block the abstract.
"""

from __future__ import annotations

import pathlib
import re

_MARKDOWN_SUFFIXES = {".md", ".markdown", ".txt"}


def _detex(text: str) -> str:
    """Lightly convert LaTeX source into markdown-ish text.

    Not a real LaTeX parser — just enough that `parse_markdown_paper` finds a
    title, sections, and body: take from `\\begin{document}` onward if present,
    drop `%` comment lines, and turn `\\title{X}` / `\\section{X}` (and
    sub/subsub) into `#`-prefixed headings.
    """
    begin = text.find(r"\begin{document}")
    if begin != -1:
        text = text[begin + len(r"\begin{document}"):]
    end = text.find(r"\end{document}")
    if end != -1:
        text = text[:end]

    out_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue  # whole-line LaTeX comment
        line = re.sub(r"\\title\*?\{([^}]*)\}", r"# \1", line)
        line = re.sub(r"\\section\*?\{([^}]*)\}", r"# \1", line)
        line = re.sub(r"\\subsection\*?\{([^}]*)\}", r"## \1", line)
        line = re.sub(r"\\subsubsection\*?\{([^}]*)\}", r"### \1", line)
        out_lines.append(line)
    return "\n".join(out_lines)


def extract_text(path: pathlib.Path) -> str:
    """Return the paper text from `path`, dispatching on its suffix.

    - `.md` / `.markdown` / `.txt` → read as UTF-8, unchanged.
    - `.tex` → read and lightly de-LaTeX (see `_detex`).
    - `.pdf` → extract with `pypdf`; raises `RuntimeError` if `pypdf` is not
      installed.
    - anything else → fall back to reading it as UTF-8 text.
    """
    suffix = path.suffix.lower()
    if suffix in _MARKDOWN_SUFFIXES:
        return path.read_text(encoding="utf-8")
    if suffix == ".tex":
        return _detex(path.read_text(encoding="utf-8"))
    if suffix == ".pdf":
        try:
            import pypdf
        except ImportError as exc:  # pragma: no cover - depends on env
            raise RuntimeError(
                "reading a .pdf needs the `pypdf` package (pip install pypdf)"
            ) from exc
        reader = pypdf.PdfReader(str(path))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    return path.read_text(encoding="utf-8")
