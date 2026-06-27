"""Run a real Gemma review of a paper and print the review as JSON.

Usage:  python scripts/review.py PATH [-o OUTPUT.json]

PATH may be `.md`/`.markdown`/`.txt` (read as-is), `.tex` (lightly de-LaTeXed), or
`.pdf` (extracted with pypdf). The first H1 (# ...) is the title, the first
blank-line-separated block after it is the abstract, and the rest is the body.
The review JSON is printed to stdout; with `-o/--output PATH` it is also written
there (the saved path is announced on stderr so stdout stays pure JSON).

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
        description="Run a local Gemma peer review of a paper and print the review JSON.",
    )
    parser.add_argument("paper_path", help="Path to the paper (.md/.tex/.pdf/.txt).")
    parser.add_argument(
        "-o", "--output", default=None,
        help="Also write the review JSON to this path (stdout still gets it).",
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

    if args.output:
        out_path = pathlib.Path(args.output).expanduser().resolve()
        out_path.write_text(blob + "\n", encoding="utf-8")
        print(f"wrote review to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
