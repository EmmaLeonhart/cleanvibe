"""Scaffold an arXiv paper into an agent-executable replication repo."""

from replication_skill.arxiv import ArxivPaper, fetch_paper, parse_arxiv_id
from replication_skill.scaffold import scaffold_replication

__all__ = ["ArxivPaper", "fetch_paper", "parse_arxiv_id", "scaffold_replication"]
__version__ = "0.1.0"
