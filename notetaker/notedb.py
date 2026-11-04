import sqlite3
import struct
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import sqlite_vec

from notetaker.models import Note
from notetaker.utils import compute_embedding


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


def init_db() -> None:
    """Create the notes, embeddings, links, and categories tables."""
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


def insert_note(content: str) -> str:
    """Insert a note and its computed embedding with a UUID and UTC timestamp."""
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
    """Delete a note by ID."""
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,),
        )


def insert_categories(note_id: str, categories: list[str]) -> None:
    """Add categories to a note."""
    with _connect() as connection, connection:
        connection.executemany(
            "INSERT INTO categories (note_id, category) VALUES (?, ?)",
            ((note_id, category) for category in categories),
        )


def delete_categories(note_id: str) -> None:
    """Remove all categories associated with a note."""
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM categories WHERE note_id = ?",
            (note_id,),
        )


def insert_links(links: list[tuple[str, str]]) -> None:
    """Add links with each pair of note IDs sorted."""
    with _connect() as connection, connection:
        connection.executemany(
            "INSERT INTO links (note_id_1, note_id_2) VALUES (?, ?)",
            (tuple(sorted(link)) for link in links),
        )


def delete_links(note_id: str) -> None:
    """Remove all links containing a note."""
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM links WHERE note_id_1 = ? OR note_id_2 = ?",
            (note_id, note_id),
        )
