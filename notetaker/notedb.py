import json
import sqlite3
import struct
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path

import sqlite_vec

from notetaker.models import Note


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
        yield connection


def _row_to_note(row: sqlite3.Row) -> Note:
    return Note(
        id=row["id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        categories=json.loads(row["categories"]),
        links=json.loads(row["links"]),
        content=row["content"],
        embedding=list(struct.unpack(f"{EMBEDDING_DIMENSIONS}f", row["embedding"])),
    )


def init_db() -> None:
    """Create the notes table and its separate vector table."""
    with _connect() as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT NOT NULL PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                categories TEXT NOT NULL,
                links TEXT NOT NULL,
                content TEXT NOT NULL
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


def insert_note(note: Note) -> None:
    """Insert the note and its embedding in a single transaction."""
    with _connect() as connection, connection:
        connection.execute(
            """
            INSERT INTO notes (
                id, created_at, updated_at, categories, links, content
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                note.id,
                note.created_at.isoformat(),
                note.updated_at.isoformat(),
                json.dumps(note.categories),
                json.dumps(note.links),
                note.content,
            ),
        )
        connection.execute(
            "INSERT INTO note_embeddings (note_id, embedding) VALUES (?, ?)",
            (note.id, sqlite_vec.serialize_float32(note.embedding)),
        )


def update_note(note: Note) -> None:
    """Update an existing note and its embedding; do nothing if it is missing."""
    with _connect() as connection, connection:
        cursor = connection.execute(
            """
            UPDATE notes
            SET created_at = ?, updated_at = ?, categories = ?, links = ?, content = ?
            WHERE id = ?
            """,
            (
                note.created_at.isoformat(),
                note.updated_at.isoformat(),
                json.dumps(note.categories),
                json.dumps(note.links),
                note.content,
                note.id,
            ),
        )
        if cursor.rowcount == 0:
            return

        connection.execute(
            "UPDATE note_embeddings SET embedding = ? WHERE note_id = ?",
            (sqlite_vec.serialize_float32(note.embedding), note.id),
        )


def delete_note(id: str) -> None:
    """Delete a note and its embedding; do nothing if it is missing."""
    with _connect() as connection, connection:
        connection.execute("DELETE FROM notes WHERE id = ?", (id,))
        connection.execute("DELETE FROM note_embeddings WHERE note_id = ?", (id,))


def get_note_by_id(id: str) -> Note | None:
    """Return the note with the given ID, or None if it does not exist."""
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT notes.*, note_embeddings.embedding
            FROM notes
            JOIN note_embeddings ON note_embeddings.note_id = notes.id
            WHERE notes.id = ?
            """,
            (id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_note(row)


def get_similar_notes(embedding: list[float], n: int = 10) -> list[Note]:
    """Return up to n notes, ordered from highest to lowest cosine similarity."""
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT notes.*, note_embeddings.embedding
            FROM note_embeddings
            JOIN notes ON notes.id = note_embeddings.note_id
            WHERE note_embeddings.embedding MATCH ? AND k = ?
            ORDER BY note_embeddings.distance ASC
            """,
            (sqlite_vec.serialize_float32(embedding), n),
        ).fetchall()

    return [_row_to_note(row) for row in rows]


def search_notes_by_keyword(keyword: str) -> list[Note]:
    """Return notes containing the literal keyword, ignoring ASCII case."""
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT notes.*, note_embeddings.embedding
            FROM notes
            JOIN note_embeddings ON note_embeddings.note_id = notes.id
            WHERE instr(lower(notes.content), lower(?)) > 0
            """,
            (keyword,),
        ).fetchall()

    return [_row_to_note(row) for row in rows]


def get_notes_by_categories(categories: list[str]) -> list[Note]:
    """Return notes with at least one exact category match."""
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT notes.*, note_embeddings.embedding
            FROM notes
            JOIN note_embeddings ON note_embeddings.note_id = notes.id
            WHERE EXISTS (
                SELECT 1
                FROM json_each(notes.categories) AS note_category
                JOIN json_each(?) AS requested_category
                    ON note_category.value = requested_category.value
            )
            """,
            (json.dumps(categories),),
        ).fetchall()

    return [_row_to_note(row) for row in rows]


def get_linked_notes(seed: str) -> list[Note]:
    """Return all notes reachable through bidirectional links, including the seed."""
    with _connect() as connection:
        rows = connection.execute(
            """
            WITH RECURSIVE reachable(id) AS (
                SELECT id FROM notes WHERE id = ?
                UNION
                SELECT link.value
                FROM reachable
                JOIN notes ON notes.id = reachable.id
                CROSS JOIN json_each(notes.links) AS link
            )
            SELECT notes.*, note_embeddings.embedding
            FROM reachable
            JOIN notes ON notes.id = reachable.id
            JOIN note_embeddings ON note_embeddings.note_id = notes.id
            """,
            (seed,),
        ).fetchall()

    return [_row_to_note(row) for row in rows]
