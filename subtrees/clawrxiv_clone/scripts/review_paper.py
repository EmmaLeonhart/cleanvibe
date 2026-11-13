"""Review a paper and save the review JSON next to it. The experiment entry point.

Usage:  python scripts/review_paper.py PATH [-o OUTPUT.json]

Like `scripts/review.py`, PATH may be `.md`/`.tex`/`.pdf`/`.txt`. The review JSON is
printed to stdout AND written to `<paper_stem>.review.json` in the paper's own
directory (e.g. `paper.md` -> `paper.review.json`), unless `-o/--output` overrides
the destination. The saved path is printed to stderr so stdout stays pure JSON.

Requires a local Ollama running the model ($CLAWRXIV_REVIEW_MODEL, default
gemma3:12b) at $OLLAMA_HOST (default http://localhost:11434).
"""

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from clawrxiv_clone.extract import extract_text  # noqa: E402
from clawrxiv_clone.llm import OllamaGemmaClient  # noqa: E402
from clawrxiv_clone.papers import parse_markdown_paper  # noqa: E402
from clawrxiv_clone.reviewer import generate_review  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review a paper and save the review JSON next to it.",
    )
    parser.add_argument("paper_path", help="Path to the paper (.md/.tex/.pdf/.txt).")
    parser.add_argument(
        "-o", "--output", default=None,
        help="Write the review here instead of <paper_stem>.review.json.",
    )
    args = parser.parse_args()

    paper_path = pathlib.Path(args.paper_path).expanduser().resolve()
    if not paper_path.exists():
        print(f"error: no such file: {paper_path}", file=sys.stderr)
        return 2

    paper = parse_markdown_paper(extract_text(paper_path))
    review = generate_review(paper, OllamaGemmaClient())
    blob = json.dumps(review.model_dump(mode="json"), indent=2)
    print(blob)

    out_path = (
        pathlib.Path(args.output).expanduser().resolve()
        if args.output
        else paper_path.with_suffix(".review.json")
    )
    out_path.write_text(blob + "\n", encoding="utf-8")
    print(f"wrote review to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
