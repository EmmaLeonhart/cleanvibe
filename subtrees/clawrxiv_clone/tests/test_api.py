"""API tests via FastAPI TestClient, with the reviewer LLM mocked."""

import pytest
from fastapi.testclient import TestClient

from clawrxiv_clone.api import create_app
from clawrxiv_clone.llm import MockLLMClient

REVIEW_RESPONSE = {
    "rating": "Weak Accept",
    "summary": "A study of the thing.",
    "pros": ["p1", "p2", "p3", "p4", "p5"],
    "cons": ["c1", "c2", "c3", "c4", "c5"],
    "justification": "Strengths edge out the weaknesses.",
}


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(llm=MockLLMClient(REVIEW_RESPONSE, name="gemma3")))


def _register(client: TestClient, name="agent-1") -> str:
    res = client.post("/api/auth/register", json={"claw_name": name})
    assert res.status_code == 200
    return res.json()["api_key"]


def test_register_and_duplicate_conflict(client):
    key = _register(client)
    assert key.startswith("oc_")
    dup = client.post("/api/auth/register", json={"claw_name": "agent-1"})
    assert dup.status_code == 409


def test_publish_requires_auth(client):
    res = client.post("/api/posts", json={"title": "T", "abstract": "A"})
    assert res.status_code == 401


def test_publish_generates_review(client):
    key = _register(client)
    res = client.post("/api/posts", headers={"Authorization": f"Bearer {key}"},
                      json={"title": "T", "abstract": "A", "content": "body", "tags": ["ml"]})
    assert res.status_code == 200
    post_id = res.json()["id"]

    review = client.get(f"/api/posts/{post_id}/review").json()["review"]
    assert review is not None
    assert review["rating"] == "Weak Accept"
    assert review["model"] == "gemma3"
    assert review["postId"] == post_id
    assert len(review["pros"]) == 5 and len(review["cons"]) == 5


def test_get_and_list_and_404(client):
    key = _register(client)
    pid = client.post("/api/posts", headers={"Authorization": f"Bearer {key}"},
                      json={"title": "Hello", "abstract": "World"}).json()["id"]
    got = client.get(f"/api/posts/{pid}").json()
    assert got["title"] == "Hello" and got["tags"] == []
    listed = client.get("/api/posts").json()
    assert listed["posts"][0]["id"] == pid
    assert client.get("/api/posts/999999").status_code == 404


def test_revise_supersedes_and_re_reviews(client):
    key = _register(client)
    h = {"Authorization": f"Bearer {key}"}
    pid = client.post("/api/posts", headers=h, json={"title": "v1", "abstract": "A"}).json()["id"]
    rev = client.post(f"/api/posts/{pid}/revise", headers=h,
                      json={"title": "v2", "abstract": "A2"})
    assert rev.status_code == 200
    body = rev.json()
    assert body["supersedes"] == pid and body["id"] != pid
    # the revision got its own review
    assert client.get(f"/api/posts/{body['id']}/review").json()["review"] is not None


def test_review_null_until_generated(client):
    # a post id with no review yet returns {"review": null}
    assert client.get("/api/posts/424242/review").json() == {"review": None}


def test_vote_toggle_switch_and_tally(client):
    key = _register(client, "voter")
    h = {"Authorization": f"Bearer {key}"}
    pid = client.post("/api/posts", headers=h, json={"title": "T", "abstract": "A"}).json()["id"]
    # upvote
    r = client.post(f"/api/posts/{pid}/vote", headers=h, json={"value": 1}).json()
    assert r["voted"] == 1 and r["upvotes"] == 1 and r["downvotes"] == 0
    # same value again cancels
    r = client.post(f"/api/posts/{pid}/vote", headers=h, json={"value": 1}).json()
    assert r["voted"] is None and r["upvotes"] == 0
    # switch to downvote
    client.post(f"/api/posts/{pid}/vote", headers=h, json={"value": 1})
    r = client.post(f"/api/posts/{pid}/vote", headers=h, json={"value": -1}).json()
    assert r["voted"] == -1 and r["upvotes"] == 0 and r["downvotes"] == 1
    # tally shows on the post
    post = client.get(f"/api/posts/{pid}").json()
    assert post["upvotes"] == 0 and post["downvotes"] == 1


def test_vote_requires_auth_and_validates(client):
    key = _register(client, "voter2")
    h = {"Authorization": f"Bearer {key}"}
    pid = client.post("/api/posts", headers=h, json={"title": "T", "abstract": "A"}).json()["id"]
    assert client.post(f"/api/posts/{pid}/vote", json={"value": 1}).status_code == 401
    assert client.post(f"/api/posts/{pid}/vote", headers=h, json={"value": 5}).status_code == 400
    assert client.post("/api/posts/999/vote", headers=h, json={"value": 1}).status_code == 404


def test_comments_add_list_and_auth(client):
    key = _register(client, "commenter")
    h = {"Authorization": f"Bearer {key}"}
    pid = client.post("/api/posts", headers=h, json={"title": "T", "abstract": "A"}).json()["id"]
    assert client.post(f"/api/posts/{pid}/comments", json={"body": "hi"}).status_code == 401
    add = client.post(f"/api/posts/{pid}/comments", headers=h, json={"body": "nice paper"})
    assert add.status_code == 200 and "id" in add.json()
    comments = client.get(f"/api/posts/{pid}/comments").json()["comments"]
    assert len(comments) == 1 and comments[0]["body"] == "nice paper"
    assert comments[0]["claw_name"] == "commenter"


def test_search_by_query_and_tag(client):
    key = _register(client, "searcher")
    h = {"Authorization": f"Bearer {key}"}
    client.post("/api/posts", headers=h,
                json={"title": "Reservoir networks", "abstract": "echo state machines",
                      "tags": ["ml", "esn"]})
    client.post("/api/posts", headers=h,
                json={"title": "Transformers", "abstract": "attention is all", "tags": ["ml", "nlp"]})
    # q matches title (case-insensitive)
    r = client.get("/api/search", params={"q": "reservoir"}).json()
    assert len(r["posts"]) == 1 and r["posts"][0]["title"] == "Reservoir networks"
    # q matches abstract
    r = client.get("/api/search", params={"q": "attention"}).json()
    assert r["posts"][0]["title"] == "Transformers"
    # tag filter
    r = client.get("/api/search", params={"tag": "nlp"}).json()
    assert len(r["posts"]) == 1 and r["posts"][0]["title"] == "Transformers"
    # q + tag combined
    r = client.get("/api/search", params={"q": "echo", "tag": "ml"}).json()
    assert len(r["posts"]) == 1 and r["posts"][0]["title"] == "Reservoir networks"
    # no match
    assert client.get("/api/search", params={"q": "nonexistent-xyz"}).json()["posts"] == []


def test_classify_endpoint_stores_category():
    app = create_app(
        llm=MockLLMClient(REVIEW_RESPONSE, name="gemma3:12b"),
        classify_llm=MockLLMClient({"category": "cs.LG", "cross_list": ["cs.CL"]}, name="gemma3:12b"),
    )
    c = TestClient(app)
    key = c.post("/api/auth/register", json={"claw_name": "clf"}).json()["api_key"]
    h = {"Authorization": f"Bearer {key}"}
    pid = c.post("/api/posts", headers=h, json={"title": "T", "abstract": "A"}).json()["id"]
    assert c.post(f"/api/posts/{pid}/classify").status_code == 401  # auth required
    res = c.post(f"/api/posts/{pid}/classify", headers=h)
    assert res.status_code == 200
    assert res.json() == {"category": "cs.LG", "cross_list": ["cs.CL"]}
    assert c.get(f"/api/posts/{pid}").json()["category"] == "cs.LG"
    assert c.post("/api/posts/999/classify", headers=h).status_code == 404


def test_check_revision_endpoint():
    app = create_app(
        llm=MockLLMClient(REVIEW_RESPONSE, name="gemma3:12b"),
        equivalence_llm=MockLLMClient({"equivalent": True, "reason": "same work"}, name="gemma3:12b"),
    )
    c = TestClient(app)
    key = c.post("/api/auth/register", json={"claw_name": "rev"}).json()["api_key"]
    h = {"Authorization": f"Bearer {key}"}
    pid = c.post("/api/posts", headers=h, json={"title": "v1", "abstract": "A"}).json()["id"]
    # a non-revision post supersedes nothing -> 400
    assert c.post(f"/api/posts/{pid}/check-revision", headers=h).status_code == 400
    new_id = c.post(f"/api/posts/{pid}/revise", headers=h,
                    json={"title": "v2", "abstract": "A2"}).json()["id"]
    res = c.post(f"/api/posts/{new_id}/check-revision", headers=h)
    assert res.status_code == 200
    assert res.json() == {"equivalent": True, "reason": "same work"}
    assert c.post(f"/api/posts/{new_id}/check-revision").status_code == 401  # auth required


def test_search_similar_ranks_same_topic_first():
    from clawrxiv_clone.embeddings import MockEmbedClient
    app = create_app(
        llm=MockLLMClient(REVIEW_RESPONSE, name="gemma3:12b"),
        embedder=MockEmbedClient(["reservoir", "graph", "transformer"]),
    )
    c = TestClient(app)
    key = c.post("/api/auth/register", json={"claw_name": "sem"}).json()["api_key"]
    h = {"Authorization": f"Bearer {key}"}
    p1 = c.post("/api/posts", headers=h,
                json={"title": "Reservoir transformers", "abstract": "echo state reservoir"}).json()["id"]
    p2 = c.post("/api/posts", headers=h,
                json={"title": "Reservoir computing primer", "abstract": "fixed reservoir dynamics"}).json()["id"]
    p3 = c.post("/api/posts", headers=h,
                json={"title": "Graph neural networks", "abstract": "graphs for molecules"}).json()["id"]
    res = c.get("/api/search/similar", params={"post_id": p1}).json()["results"]
    assert res[0]["id"] == p2  # same-topic (reservoir) ranks above the graph paper
    assert res[0]["score"] > res[-1]["score"]
    assert all(r["id"] != p1 for r in res)  # excludes the target itself
    assert c.get("/api/search/similar", params={"post_id": 999}).status_code == 404


def test_auto_classify_and_equivalence_on_publish_revise():
    app = create_app(
        llm=MockLLMClient(REVIEW_RESPONSE, name="gemma3:12b"),
        classify_llm=MockLLMClient({"category": "cs.LG", "cross_list": []}, name="gemma3:12b"),
        equivalence_llm=MockLLMClient({"equivalent": True, "reason": "same work"}, name="gemma3:12b"),
    )
    c = TestClient(app)
    key = c.post("/api/auth/register", json={"claw_name": "auto"}).json()["api_key"]
    h = {"Authorization": f"Bearer {key}"}
    pid = c.post("/api/posts", headers=h, json={"title": "v1", "abstract": "A"}).json()["id"]
    # auto-reviewed and auto-classified on publish
    assert c.get(f"/api/posts/{pid}/review").json()["review"]["rating"] == "Weak Accept"
    assert c.get(f"/api/posts/{pid}").json()["category"] == "cs.LG"
    # revise -> auto-classified + auto-equivalence verdict stored on the revision
    new_id = c.post(f"/api/posts/{pid}/revise", headers=h,
                    json={"title": "v2", "abstract": "A2"}).json()["id"]
    rev = c.get(f"/api/posts/{new_id}").json()
    assert rev["category"] == "cs.LG"
    assert rev["revision_equivalent"] is True
    assert rev["revision_reason"] == "same work"


def test_no_auto_subsystems_without_configured_clients(client):
    # the default fixture has only a review llm; publishing must NOT auto-classify
    key = _register(client, "noauto")
    h = {"Authorization": f"Bearer {key}"}
    pid = client.post("/api/posts", headers=h, json={"title": "T", "abstract": "A"}).json()["id"]
    assert client.get(f"/api/posts/{pid}").json()["category"] is None


def test_frontend_index_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "clawrxiv_clone" in res.text and "/api/posts" in res.text


def test_review_includes_scores():
    resp = {"rating": "Accept", "summary": "s",
            "pros": ["a", "b", "c", "d", "e"], "cons": ["a", "b", "c", "d", "e"],
            "justification": "j",
            "scores": {"originality": 5, "methodology": 4, "clarity": 4, "significance": 5}}
    app = create_app(llm=MockLLMClient(resp, name="gemma3:12b"))
    c = TestClient(app)
    key = c.post("/api/auth/register", json={"claw_name": "sc"}).json()["api_key"]
    h = {"Authorization": f"Bearer {key}"}
    pid = c.post("/api/posts", headers=h, json={"title": "T", "abstract": "A"}).json()["id"]
    review = c.get(f"/api/posts/{pid}/review").json()["review"]
    assert review["scores"] == {"originality": 5, "methodology": 4, "clarity": 4, "significance": 5}


def test_skill_md_stored_and_served(client):
    key = _register(client, "skiller")
    h = {"Authorization": f"Bearer {key}"}
    skill = "---\nname: repro\nallowed-tools: Bash(python *)\n---\n# Steps\n1. python run.py"
    pid = client.post("/api/posts", headers=h,
                      json={"title": "T", "abstract": "A", "skill_md": skill}).json()["id"]
    assert client.get(f"/api/posts/{pid}").json()["skill_md"] == skill
    pid2 = client.post("/api/posts", headers=h, json={"title": "T2", "abstract": "A2"}).json()["id"]
    assert client.get(f"/api/posts/{pid2}").json()["skill_md"] is None


def test_regenerate_key_invalidates_old(client):
    key = _register(client, "rotator")
    h = {"Authorization": f"Bearer {key}"}
    res = client.post("/api/auth/key", headers=h)
    assert res.status_code == 200
    new_key = res.json()["api_key"]
    assert new_key != key
    assert client.post("/api/posts", headers=h,
                       json={"title": "T", "abstract": "A"}).status_code == 401  # old key dead
    nh = {"Authorization": f"Bearer {new_key}"}
    assert client.post("/api/posts", headers=nh,
                       json={"title": "T", "abstract": "A"}).status_code == 200  # new key works
    assert client.post("/api/auth/key").status_code == 401  # auth required


def test_review_panel_in_app():
    base = {"summary": "s", "pros": ["a", "b", "c", "d", "e"],
            "cons": ["a", "b", "c", "d", "e"], "justification": "j"}
    seq = [dict(base, rating="Reject"), dict(base, rating="Weak Accept"), dict(base, rating="Accept")]
    app = create_app(llm=MockLLMClient(seq, name="gemma3:12b"), review_panel_size=3)
    c = TestClient(app)
    key = c.post("/api/auth/register", json={"claw_name": "panel"}).json()["api_key"]
    h = {"Authorization": f"Bearer {key}"}
    pid = c.post("/api/posts", headers=h, json={"title": "T", "abstract": "A"}).json()["id"]
    review = c.get(f"/api/posts/{pid}/review").json()["review"]
    assert review["rating"] == "Weak Accept"  # median of [Reject, Weak Accept, Accept]
