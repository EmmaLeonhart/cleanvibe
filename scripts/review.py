"""Run a real Gemma review of a markdown paper and print the review as JSON.

Usage:  python scripts/review.py path/to/paper.md
The first H1 (# ...) is the title; the first blank-line-separated block after it is the
abstract; the rest is the body. Requires a local Ollama running the model
($CLAWRXIV_REVIEW_MODEL, default gemma3:12b).
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from clawrxiv_clone.llm import OllamaGemmaClient  # noqa: E402
from clawrxiv_clone.papers import parse_markdown_paper  # noqa: E402
from clawrxiv_clone.reviewer import generate_review  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    paper = parse_markdown_paper(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    review = generate_review(paper, OllamaGemmaClient())
    print(json.dumps(review.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
