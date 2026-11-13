import json
from pathlib import Path

import pytest

from replication_skill.arxiv import ArxivPaper
from replication_skill.scaffold import scaffold_replication


def _paper() -> ArxivPaper:
    return ArxivPaper(
        arxiv_id="1706.03762",
        title="Attention Is All You Need",
        authors=("Ashish Vaswani", "Noam Shazeer"),
        summary="A new simple network architecture called the Transformer.",
        published="2017-06-12T17:57:34Z",
        pdf_url="https://arxiv.org/pdf/1706.03762v5.pdf",
    )


def test_scaffold_writes_expected_tree(tmp_path: Path):
    target = scaffold_replication(_paper(), tmp_path)
    assert target == tmp_path / "attention-is-all-you-need"
    for name in ("README.md", "SKILL.md", "download_paper.py", ".gitignore", "paper.json"):
        assert (target / name).is_file(), f"missing {name}"
    assert (target / "paper" / ".gitkeep").is_file()


def test_scaffold_substitutes_fields(tmp_path: Path):
    target = scaffold_replication(_paper(), tmp_path)
    skill = (target / "SKILL.md").read_text(encoding="utf-8")
    assert "arXiv:1706.03762" in skill
    assert "Attention Is All You Need" in skill
    assert "Ashish Vaswani" in skill
    meta = json.loads((target / "paper.json").read_text(encoding="utf-8"))
    assert meta["arxiv_id"] == "1706.03762"
    assert meta["authors"] == ["Ashish Vaswani", "Noam Shazeer"]


def test_scaffold_refuses_to_overwrite(tmp_path: Path):
    scaffold_replication(_paper(), tmp_path)
    with pytest.raises(FileExistsError):
        scaffold_replication(_paper(), tmp_path)


def test_scaffold_overwrite_flag(tmp_path: Path):
    target = scaffold_replication(_paper(), tmp_path)
    (target / "README.md").write_text("stale", encoding="utf-8")
    scaffold_replication(_paper(), tmp_path, overwrite=True)
    assert "Attention Is All You Need" in (target / "README.md").read_text(encoding="utf-8")
