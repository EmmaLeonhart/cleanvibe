"""Embedding/cosine tests (no live model)."""

from clawrxiv_clone.embeddings import MockEmbedClient, cosine, embed_text


def test_cosine():
    assert cosine([1, 0, 0], [1, 0, 0]) == 1.0
    assert cosine([1, 0], [0, 1]) == 0.0
    assert cosine([], [1]) == 0.0
    assert cosine([0, 0], [1, 1]) == 0.0
    assert abs(cosine([1, 1], [1, 1]) - 1.0) < 1e-9  # identical vectors (float-safe)


def test_mock_embed_keyword_vector():
    emb = MockEmbedClient(["reservoir", "graph"])
    assert emb.embed("A reservoir paper") == [1.0, 0.0]
    assert emb.embed("GRAPH networks") == [0.0, 1.0]
    assert emb.embed("neither here") == [0.0, 0.0]


def test_embed_text():
    assert embed_text("Title", "Abstract") == "Title\nAbstract"
