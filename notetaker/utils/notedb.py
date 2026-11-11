import sqlite3
import struct
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import sqlite_vec

from notetaker.utils.models import Note
from notetaker.utils.helpers import compute_embedding


DB_PATH = Path(__file__).resolve().parent / "notes.sqlite3"
# Matches the default output of openai/text-embedding-3-small.
EMBEDDING_DIMENSIONS = 1536


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.enable_load_extension(True)
        try:
            sqlite_vec.load(connection)
        finally:
            connection.enable_load_extension(False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        yield connection


def _row_to_note(
    *,
    id: str,
    created_at: str,
    categories: list[str],
    linked_ids: list[str],
    content: str,
    embedding: bytes,
) -> Note:
    return Note(
        id=id,
        created_at=datetime.fromisoformat(created_at),
        categories=categories,
        linked_ids=linked_ids,
        content=content,
        embedding=list(struct.unpack(f"{EMBEDDING_DIMENSIONS}f", embedding)),
    )


def drop_db() -> None:
    with _connect() as connection, connection:
        connection.execute("DROP TABLE IF EXISTS links")
        connection.execute("DROP TABLE IF EXISTS categories")
        connection.execute("DROP TABLE IF EXISTS note_embeddings")
        connection.execute("DROP TABLE IF EXISTS notes")


def init_db() -> None:
    with _connect() as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT NOT NULL PRIMARY KEY,
                created_at TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                note_id_1 TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
                note_id_2 TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
                PRIMARY KEY (note_id_1, note_id_2)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                note_id TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
                category TEXT NOT NULL,
                PRIMARY KEY (note_id, category)
            )
            """
        )
        connection.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS note_embeddings USING vec0 (
                note_id TEXT PRIMARY KEY,
                embedding float[{EMBEDDING_DIMENSIONS}] distance_metric=cosine
            )
            """
        )


def get_note_by_ids(note_ids: list[str]) -> list[Note]:
    placeholders = ", ".join("?" for _ in note_ids)
    with _connect() as connection:
        rows = connection.execute(
            f"""
            SELECT notes.id, notes.created_at, notes.content, note_embeddings.embedding
            FROM notes
            JOIN note_embeddings ON note_embeddings.note_id = notes.id
            WHERE notes.id IN ({placeholders})
            """,
            note_ids,
        ).fetchall()
        categories = connection.execute(
            f"SELECT note_id, category FROM categories WHERE note_id IN ({placeholders})",
            note_ids,
        ).fetchall()
        links = connection.execute(
            f"""
            SELECT note_id_1 AS note_id, note_id_2 AS linked_id
            FROM links
            WHERE note_id_1 IN ({placeholders})
            UNION
            SELECT note_id_2 AS note_id, note_id_1 AS linked_id
            FROM links
            WHERE note_id_2 IN ({placeholders})
            """,
            note_ids + note_ids,
        ).fetchall()

    categories_by_id: dict[str, list[str]] = {note_id: [] for note_id in note_ids}
    links_by_id: dict[str, list[str]] = {note_id: [] for note_id in note_ids}
    for category in categories:
        categories_by_id[category["note_id"]].append(category["category"])
    for link in links:
        links_by_id[link["note_id"]].append(link["linked_id"])

    return [
        _row_to_note(
            **row,
            categories=categories_by_id[row["id"]],
            linked_ids=links_by_id[row["id"]],
        )
        for row in rows
    ]


def get_categories() -> list[str]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT DISTINCT category FROM categories ORDER BY category"
        ).fetchall()
    return [row["category"] for row in rows]


def get_note_ids_by_category(category: str) -> list[str]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT note_id FROM categories WHERE category = ?",
            (category,),
        ).fetchall()
    return [row["note_id"] for row in rows]


def get_note_ids_by_keyword(keyword: str) -> list[str]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT id FROM notes WHERE instr(content, ?) > 0",
            (keyword,),
        ).fetchall()
    return [row["id"] for row in rows]


def get_linked_note_ids(note_id: str) -> list[str]:
    with _connect() as connection:
        rows = connection.execute(
            """
            WITH RECURSIVE reachable(note_id) AS (
                SELECT ?
                UNION
                SELECT CASE
                    WHEN links.note_id_1 = reachable.note_id THEN links.note_id_2
                    ELSE links.note_id_1
                END
                FROM links
                JOIN reachable
                    ON links.note_id_1 = reachable.note_id
                    OR links.note_id_2 = reachable.note_id
            )
            SELECT note_id FROM reachable
            """,
            (note_id,),
        ).fetchall()
    return [row["note_id"] for row in rows]


def get_similar_note_ids(content: str, n: int = 10) -> list[tuple[str, float]]:
    embedding = compute_embedding(content)
    with _connect() as connection:
        rows = connection.execute(
            """
            WITH nearest AS MATERIALIZED (
                SELECT note_id, distance
                FROM note_embeddings
                WHERE embedding MATCH ?
                AND k = ?
            )
            SELECT note_id, 1.0 - distance AS similarity
            FROM nearest
            ORDER BY distance
            """,
            (struct.pack(f"{EMBEDDING_DIMENSIONS}f", *embedding), n),
        ).fetchall()
    return [(row["note_id"], row["similarity"]) for row in rows]


def insert_note(content: str) -> str:
    embedding = compute_embedding(content)
    note_id = str(uuid4())
    created_at = datetime.now(UTC).isoformat()
    with _connect() as connection, connection:
        connection.execute(
            "INSERT INTO notes (id, created_at, content) VALUES (?, ?, ?)",
            (note_id, created_at, content),
        )
        connection.execute(
            "INSERT INTO note_embeddings (note_id, embedding) VALUES (?, ?)",
            (note_id, struct.pack(f"{EMBEDDING_DIMENSIONS}f", *embedding)),
        )
    return note_id


def delete_note(note_id: str) -> None:
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,),
        )


def insert_categories(note_id: str, categories: list[str]) -> None:
    with _connect() as connection, connection:
        connection.executemany(
            "INSERT INTO categories (note_id, category) VALUES (?, ?)",
            ((note_id, category) for category in categories),
        )


def delete_category(note_id: str, category: str) -> None:
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM categories WHERE note_id = ? AND category = ?",
            (note_id, category),
        )


def delete_categories(note_id: str) -> None:
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM categories WHERE note_id = ?",
            (note_id,),
        )


def insert_links(links: list[tuple[str, str]]) -> None:
    with _connect() as connection, connection:
        connection.executemany(
            "INSERT INTO links (note_id_1, note_id_2) VALUES (?, ?)",
            (tuple(sorted(link)) for link in links),
        )


def delete_link(note_id_1: str, note_id_2: str) -> None:
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM links WHERE note_id_1 = ? AND note_id_2 = ?",
            tuple(sorted((note_id_1, note_id_2))),
        )


def delete_links(note_id: str) -> None:
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM links WHERE note_id_1 = ? OR note_id_2 = ?",
            (note_id, note_id),
        )
