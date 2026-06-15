"""Revision-equivalence tests. LLM mocked — no live model in CI."""

import pytest

from clawrxiv_clone.equivalence import EquivalenceError, check_equivalence
from clawrxiv_clone.llm import MockLLMClient
from clawrxiv_clone.schema import EquivalenceVerdict, Paper


def test_equivalence_same_work():
    llm = MockLLMClient({"equivalent": True, "reason": "Same method and results, reworded."})
    v = check_equivalence(Paper(title="A", abstract="x"),
                          Paper(title="A v2", abstract="x reworded"), llm)
    assert isinstance(v, EquivalenceVerdict) and v.equivalent is True


def test_equivalence_different_work():
    llm = MockLLMClient({"equivalent": False, "reason": "Different problem and method."})
    v = check_equivalence(Paper(title="A", abstract="x"), Paper(title="B", abstract="y"), llm)
    assert v.equivalent is False


def test_equivalence_retry_then_raise():
    bad = {"reason": "missing the equivalent key"}
    llm = MockLLMClient([bad, bad])
    with pytest.raises(EquivalenceError):
        check_equivalence(Paper(title="A", abstract="x"), Paper(title="A", abstract="x"), llm)
    assert llm.calls == 2
