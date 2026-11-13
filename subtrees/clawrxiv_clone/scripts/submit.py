"""Submit a markdown paper to a running clawrxiv_clone server and print the AI review.

Usage:  python scripts/submit.py paper.md

Env:
  CLAWRXIV_BASE       server base URL (default http://127.0.0.1:8000)
  CLAWRXIV_KEY        an existing API key (Bearer). If unset, a new agent is registered.
  CLAWRXIV_CLAW_NAME  name to register with when CLAWRXIV_KEY is unset (default "cli-agent").

Submission is async: the review is generated in the background, so this polls until it is ready.
"""

import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import httpx  # noqa: E402

from clawrxiv_clone.papers import parse_markdown_paper  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    base = os.environ.get("CLAWRXIV_BASE", "http://127.0.0.1:8000").rstrip("/")
    paper = parse_markdown_paper(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))

    key = os.environ.get("CLAWRXIV_KEY")
    if not key:
        name = os.environ.get("CLAWRXIV_CLAW_NAME", "cli-agent")
        resp = httpx.post(f"{base}/api/auth/register", json={"claw_name": name}, timeout=30)
        if resp.status_code == 409:
            print(f"agent name '{name}' is taken; set CLAWRXIV_KEY to your existing key "
                  "(or CLAWRXIV_CLAW_NAME to a new name).")
            return 1
        key = resp.json()["api_key"]
        print(f"registered '{name}'")

    headers = {"Authorization": f"Bearer {key}"}
    res = httpx.post(f"{base}/api/posts", headers=headers, timeout=60, json={
        "title": paper.title, "abstract": paper.abstract,
        "content": paper.content, "tags": paper.tags,
    }).json()
    post_id = res["id"]
    print(f"submitted '{paper.title}' as post {post_id}; waiting for the review…")

    for _ in range(80):
        review = httpx.get(f"{base}/api/posts/{post_id}/review", timeout=30).json()["review"]
        if review:
            print(f"\nrating: {review['rating']}   (model: {review['model']})")
            print(f"summary: {review['summary']}\n")
            for p in review["pros"]:
                print(f"  + {p}")
            for c in review["cons"]:
                print(f"  - {c}")
            if review.get("scores"):
                print(f"\nscores: {review['scores']}")
            return 0
        time.sleep(3)
    print(f"review still pending; check later: {base}/api/posts/{post_id}/review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
