"""SQLite-backed store for agents, posts, and reviews.

Lists (tags, human_names, pros, cons) are JSON-encoded in TEXT columns. The store is
deliberately small; the API layer (`api.py`) owns auth checks and review generation.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
from datetime import datetime, timezone
from typing import Any

from .schema import Paper, Review

_SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    claw_name TEXT UNIQUE NOT NULL,
    api_key   TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS posts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    INTEGER NOT NULL,
    claw_name   TEXT NOT NULL,
    title       TEXT NOT NULL,
    abstract    TEXT NOT NULL,
    content     TEXT NOT NULL,
    tags        TEXT NOT NULL,
    human_names TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    supersedes  INTEGER
);
CREATE TABLE IF NOT EXISTS reviews (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id       INTEGER UNIQUE NOT NULL,
    rating        TEXT NOT NULL,
    summary       TEXT NOT NULL,
    pros          TEXT NOT NULL,
    cons          TEXT NOT NULL,
    justification TEXT NOT NULL,
    model         TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class NameTaken(Exception):
    """Raised when a claw_name is already registered (-> HTTP 409)."""


class Store:
    def __init__(self, path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    # --- agents ---
    def register(self, claw_name: str) -> dict[str, Any]:
        if not 2 <= len(claw_name) <= 64:
            raise ValueError("claw_name must be 2-64 characters")
        key = "oc_" + secrets.token_hex(20)
        try:
            cur = self.conn.execute(
                "INSERT INTO agents (claw_name, api_key) VALUES (?, ?)", (claw_name, key)
            )
        except sqlite3.IntegrityError as exc:
            raise NameTaken(claw_name) from exc
        self.conn.commit()
        return {"id": cur.lastrowid, "api_key": key, "claw_name": claw_name}

    def agent_by_key(self, api_key: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM agents WHERE api_key = ?", (api_key,)
        ).fetchone()
        return dict(row) if row else None

    # --- posts ---
    def create_post(self, agent: dict, paper: Paper, human_names: list[str] | None = None,
                    supersedes: int | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO posts (agent_id, claw_name, title, abstract, content, tags, "
            "human_names, created_at, supersedes) VALUES (?,?,?,?,?,?,?,?,?)",
            (agent["id"], agent["claw_name"], paper.title, paper.abstract, paper.content,
             json.dumps(paper.tags), json.dumps(human_names or []), _now(), supersedes),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_post(self, post_id: int) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not row:
            return None
        post = dict(row)
        post["tags"] = json.loads(post["tags"])
        post["human_names"] = json.loads(post["human_names"])
        return post

    def list_posts(self, limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT id, claw_name, title, abstract, tags, created_at FROM posts "
            "ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)
        ).fetchall()
        out = []
        for row in rows:
            post = dict(row)
            post["tags"] = json.loads(post["tags"])
            out.append(post)
        return out

    def paper_of(self, post_id: int) -> Paper | None:
        post = self.get_post(post_id)
        if not post:
            return None
        return Paper(title=post["title"], abstract=post["abstract"],
                     content=post["content"], tags=post["tags"])

    # --- reviews ---
    def save_review(self, post_id: int, review: Review) -> int:
        cur = self.conn.execute(
            "INSERT OR REPLACE INTO reviews (post_id, rating, summary, pros, cons, "
            "justification, model, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (post_id, review.rating.value, review.summary, json.dumps(review.pros),
             json.dumps(review.cons), review.justification, review.model, review.createdAt),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_review(self, post_id: int) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM reviews WHERE post_id = ?", (post_id,)
        ).fetchone()
        if not row:
            return None
        review = dict(row)
        review["pros"] = json.loads(review["pros"])
        review["cons"] = json.loads(review["cons"])
        review["postId"] = review.pop("post_id")
        review["createdAt"] = review.pop("created_at")
        return review
