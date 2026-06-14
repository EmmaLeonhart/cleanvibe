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
