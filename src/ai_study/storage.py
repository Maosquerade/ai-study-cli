from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    id: int
    topic: str
    title: str
    path: str
    content: str


class StudyStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    title TEXT NOT NULL,
                    path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL,
                    topic TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def add_document(self, topic: str, title: str, path: str, content: str) -> int:
        self.init()
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO documents (topic, title, path, content) VALUES (?, ?, ?, ?)",
                (topic, title, path, content),
            )
            return int(cursor.lastrowid)

    def list_documents(self) -> list[Document]:
        self.init()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, topic, title, path, content FROM documents ORDER BY created_at DESC"
            ).fetchall()
        return [Document(*row) for row in rows]

    def search_documents(self, query: str, topic: str | None = None, limit: int = 4) -> list[Document]:
        self.init()
        terms = [term.lower() for term in query.split() if len(term) > 1]
        docs = self.list_documents()
        if topic:
            docs = [doc for doc in docs if doc.topic == topic]
        scored: list[tuple[int, Document]] = []
        for doc in docs:
            haystack = f"{doc.title}\n{doc.topic}\n{doc.content}".lower()
            score = sum(haystack.count(term) for term in terms)
            if score or not terms:
                scored.append((score, doc))
        if topic and not scored:
            return docs[:limit]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[:limit]]

    def add_message(self, mode: str, role: str, content: str, topic: str | None = None) -> None:
        self.init()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (mode, topic, role, content) VALUES (?, ?, ?, ?)",
                (mode, topic, role, content),
            )

    def recent_messages(self, limit: int = 8) -> list[tuple[str, str, str | None, str]]:
        self.init()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT mode, role, topic, content
                FROM messages
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return list(reversed(rows))

    def add_review_question(self, topic: str, question: str) -> int:
        self.init()
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO reviews (topic, question) VALUES (?, ?)",
                (topic, question),
            )
            return int(cursor.lastrowid)

    def pending_reviews(self, limit: int = 5) -> list[tuple[int, str, str]]:
        self.init()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, topic, question
                FROM reviews
                WHERE answer IS NULL
                ORDER BY created_at ASC, id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [(int(row[0]), row[1], row[2]) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
