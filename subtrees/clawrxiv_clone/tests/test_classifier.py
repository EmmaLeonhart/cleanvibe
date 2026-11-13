"""Classifier tests. LLM mocked — no live model in CI."""

import pytest

from clawrxiv_clone.classifier import ARXIV_CATEGORIES, ClassificationError, classify_paper
from clawrxiv_clone.llm import MockLLMClient
from clawrxiv_clone.schema import Classification, Paper


def test_classify_valid():
    llm = MockLLMClient({"category": "cs.LG", "cross_list": ["cs.CL"]})
    c = classify_paper(Paper(title="Reservoirs in transformers", abstract="echo state"), llm)
    assert isinstance(c, Classification)
    assert c.category == "cs.LG" and c.cross_list == ["cs.CL"]


def test_classify_filters_out_of_set_and_self_crosslist():
    llm = MockLLMClient({"category": "cs.LG", "cross_list": ["bogus.X", "cs.LG", "cs.CL"]})
    c = classify_paper(Paper(title="T", abstract="A"), llm)
    assert c.category == "cs.LG"
    assert c.cross_list == ["cs.CL"]  # bogus dropped, self-category dropped


def test_classify_retries_then_raises_on_bad_category():
    llm = MockLLMClient([{"category": "not-a-cat", "cross_list": []},
                         {"category": "also-bad", "cross_list": []}])
    with pytest.raises(ClassificationError):
        classify_paper(Paper(title="T", abstract="A"), llm)
    assert llm.calls == 2


def test_categories_are_arxiv_like():
    assert "cs.LG" in ARXIV_CATEGORIES and "cs.CL" in ARXIV_CATEGORIES
