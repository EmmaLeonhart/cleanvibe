"""Parse a markdown paper into a `Paper` (shared by the review/submit CLIs).

Convention: the first `# H1` is the title; the first blank-line-separated block after it is
the abstract; the whole body (everything after the title line) is the content.
"""

from __future__ import annotations

from .schema import Paper


def parse_markdown_paper(md: str) -> Paper:
    lines = md.splitlines()
    title = next((ln[2:].strip() for ln in lines if ln.startswith("# ")), "Untitled")
    body = md.split("\n", 1)[1] if md.startswith("# ") else md
    blocks = [b.strip() for b in body.split("\n\n") if b.strip()]
    abstract = blocks[0] if blocks else ""
    return Paper(title=title, abstract=abstract, content=body)
