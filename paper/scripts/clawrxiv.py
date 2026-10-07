"""Post paper/paper.md + paper/SKILL.md to clawRxiv, and fetch the review.

    python clawrxiv.py submit [DIR]   # new post, or a revision of DIR/.post_id
    python clawrxiv.py review [DIR]   # wait for the review of DIR/.post_id, save it

DIR is the paper's folder (default: paper/); it holds paper.md, SKILL.md,
.post_id and reviews/.

The API key comes from CLAWRXIV_API_KEY (the repository secret in CI).
`submit` writes paper/.post_id; `review` writes paper/reviews/<post>.{json,md}.
In GitHub Actions both also write step outputs. Stdlib only.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://www.clawrxiv.io/api"
HERE = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else     os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(HERE, "paper.md")
SKILL = os.path.join(HERE, "SKILL.md")
POST_ID = os.path.join(HERE, ".post_id")
REVIEWS = os.path.join(HERE, "reviews")
TAGS = ["ai-agents", "agentic-workflows", "prospective-memory", "claude-code"]
HUMANS = ["Emma Leonhart"]


def _output(key, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


def _request(method, path, body=None):
    headers = {"Content-Type": "application/json", "User-Agent": "cleanvibe-paper"}
    key = os.environ.get("CLAWRXIV_API_KEY", "")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "null")


def parse_paper(text):
    """Title from the first '# ' line, abstract from '## Abstract', the rest is content."""
    title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    m = re.search(r"^## Abstract\s*\n(.*?)(?=^## )", text, re.M | re.S)
    abstract = " ".join(m.group(1).split())
    content = text[m.end():].strip() + "\n"
    return title, abstract, content


def submit():
    if not os.environ.get("CLAWRXIV_API_KEY"):
        sys.exit("CLAWRXIV_API_KEY is not set")
    title, abstract, content = parse_paper(open(PAPER, encoding="utf-8").read())
    body = {"title": title, "abstract": abstract, "content": content, "tags": TAGS,
            "human_names": HUMANS, "skill_md": open(SKILL, encoding="utf-8").read()}
    existing = open(POST_ID).read().strip() if os.path.exists(POST_ID) else ""
    # A revision gets a new post id that supersedes the recorded one. If
    # clawRxiv refuses the revision as different work, the paper has become a
    # new one: post it as a new submission.
    try:
        resp = _request("POST", f"/posts/{existing}/revise" if existing else "/posts", body)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        if not (existing and e.code == 400 and "not appear to be the same work" in detail):
            raise
        print(f"revision of {existing} refused as different work; posting new: {detail[:200]}")
        resp = _request("POST", "/posts", body)
    post = str(resp.get("id") or resp.get("post_id"))
    with open(POST_ID, "w") as f:
        f.write(post + "\n")
    print(f"posted: {post} {resp}")
    _output("post_id", post)


def review(wait_s=7200, every_s=60):
    post = open(POST_ID).read().strip()
    deadline = time.time() + wait_s
    while True:
        try:
            r = _request("GET", f"/posts/{post}/review")
            if isinstance(r, dict) and "review" in r:  # the API nests it: {"review": {...}}
                r = r["review"]
        except urllib.error.HTTPError as e:
            r = None if e.code == 404 else sys.exit(f"review fetch failed: HTTP {e.code}")
        if r and r.get("rating"):
            break
        if time.time() > deadline:
            sys.exit(f"no review for post {post} after {wait_s // 60} min")
        time.sleep(every_s)
    os.makedirs(REVIEWS, exist_ok=True)
    with open(os.path.join(REVIEWS, f"{post}.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2)
    lines = [f"# clawRxiv review of post {post}", "", f"**Rating:** {r.get('rating', '')}", "",
             r.get("summary", ""), "", "## Pros", ""]
    lines += [f"- {p}" for p in r.get("pros", [])] + ["", "## Cons", ""]
    lines += [f"- {c}" for c in r.get("cons", [])] + ["", "## Justification", "",
                                                     r.get("justification", ""), ""]
    with open(os.path.join(REVIEWS, f"{post}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"review of {post}: {r.get('rating')}")
    _output("rating", r.get("rating", ""))


if __name__ == "__main__":
    {"submit": submit, "review": review}.get(sys.argv[1] if len(sys.argv) > 1 else "",
                                              lambda: sys.exit(__doc__))()
