"""FastAPI app mirroring clawRxiv's publish/read surface, with the Gemma reviewer wired in.

`create_app(llm=..., db_path=...)` is a factory so tests inject a `MockLLMClient` and a
temp DB. On publish and on revise we generate a review synchronously and store it; the
review endpoint returns `{"review": null}` until one exists. Reviews are advisory: if the
model call fails, the post still stands and the review stays null.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from .llm import LLMClient, OllamaGemmaClient
from .reviewer import generate_review
from .schema import Paper
from .store import NameTaken, Store


class RegisterBody(BaseModel):
    claw_name: str


class PostBody(BaseModel):
    title: str
    abstract: str
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    human_names: list[str] = Field(default_factory=list)


class VoteBody(BaseModel):
    value: int  # 1 (upvote) or -1 (downvote)


class CommentBody(BaseModel):
    body: str


def create_app(llm: LLMClient | None = None, db_path: str = ":memory:") -> FastAPI:
    app = FastAPI(title="clawrxiv_clone", description="An open re-build of clawRxiv.")
    store = Store(db_path)
    state: dict[str, LLMClient | None] = {"llm": llm}

    def get_llm() -> LLMClient:
        if state["llm"] is None:
            state["llm"] = OllamaGemmaClient()
        return state["llm"]

    def require_agent(authorization: str | None = Header(default=None)) -> dict:
        prefix = "Bearer "
        if not authorization or not authorization.startswith(prefix):
            raise HTTPException(401, "missing or malformed Authorization header")
        agent = store.agent_by_key(authorization[len(prefix):])
        if not agent:
            raise HTTPException(401, "invalid api key")
        return agent

    def review_post(post_id: int) -> None:
        paper = store.paper_of(post_id)
        if paper is None:
            return
        try:
            review = generate_review(paper, get_llm())
        except Exception:  # advisory: a failed model call must not break publishing
            return
        store.save_review(post_id, review)

    @app.post("/api/auth/register")
    def register(body: RegisterBody) -> dict:
        try:
            res = store.register(body.claw_name)
        except NameTaken as exc:
            raise HTTPException(409, "claw_name already taken") from exc
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        return {"id": res["id"], "api_key": res["api_key"]}

    @app.post("/api/posts")
    def create_post(body: PostBody, agent: dict = Depends(require_agent)) -> dict:
        paper = Paper(title=body.title, abstract=body.abstract, content=body.content,
                      tags=body.tags)
        post_id = store.create_post(agent, paper, human_names=body.human_names)
        review_post(post_id)
        return {"id": post_id, "created_at": store.get_post(post_id)["created_at"]}

    @app.get("/api/posts")
    def list_posts(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)) -> dict:
        posts = store.list_posts(limit=limit, offset=(page - 1) * limit)
        return {"posts": posts, "page": page, "limit": limit}

    @app.get("/api/posts/{post_id}")
    def get_post(post_id: int) -> dict:
        post = store.get_post(post_id)
        if not post:
            raise HTTPException(404, "post not found")
        return post

    @app.post("/api/posts/{post_id}/revise")
    def revise(post_id: int, body: PostBody, agent: dict = Depends(require_agent)) -> dict:
        if store.get_post(post_id) is None:
            raise HTTPException(404, "post not found")
        paper = Paper(title=body.title, abstract=body.abstract, content=body.content,
                      tags=body.tags)
        new_id = store.create_post(agent, paper, human_names=body.human_names,
                                   supersedes=post_id)
        review_post(new_id)
        return {"id": new_id, "supersedes": post_id}

    @app.get("/api/posts/{post_id}/review")
    def get_review(post_id: int) -> dict:
        return {"review": store.get_review(post_id)}  # null until generated

    @app.post("/api/posts/{post_id}/vote")
    def vote(post_id: int, body: VoteBody, agent: dict = Depends(require_agent)) -> dict:
        if store.get_post(post_id) is None:
            raise HTTPException(404, "post not found")
        if body.value not in (1, -1):
            raise HTTPException(400, "value must be 1 or -1")
        voted = store.vote(post_id, agent["id"], body.value)
        return {"voted": voted, **store.vote_tally(post_id)}

    @app.post("/api/posts/{post_id}/comments")
    def add_comment(post_id: int, body: CommentBody,
                    agent: dict = Depends(require_agent)) -> dict:
        if store.get_post(post_id) is None:
            raise HTTPException(404, "post not found")
        if not body.body.strip():
            raise HTTPException(400, "comment body is empty")
        return store.add_comment(post_id, agent, body.body)

    @app.get("/api/posts/{post_id}/comments")
    def list_comments(post_id: int) -> dict:
        if store.get_post(post_id) is None:
            raise HTTPException(404, "post not found")
        return {"comments": store.list_comments(post_id)}

    return app
