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


def drop_db() -> None:
    """Permanently delete all notes, categories, links, and embeddings.

    Drops the application tables. Call init_db before using the database again.
    """
    with _connect() as connection, connection:
        connection.execute("DROP TABLE IF EXISTS links")
        connection.execute("DROP TABLE IF EXISTS categories")
        connection.execute("DROP TABLE IF EXISTS note_embeddings")
        connection.execute("DROP TABLE IF EXISTS notes")


def init_db() -> None:
    """Initialize note storage, preserving any existing tables and data.

    Creates missing tables for notes, embeddings, categories, and links.
    """
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
    """Retrieve the full notes for a list of known note IDs.

    Args:
        note_ids: IDs of the notes to retrieve.

    Returns:
        Matching notes, including their ID, creation timestamp, content,
        embedding, categories, and directly linked note IDs. Missing IDs are
        omitted, duplicate IDs produce one result, and result order is unspecified.
    """
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
    """List existing category names to discover how notes are organized.

    Returns:
        Distinct category names in alphabetical order, or an empty list if no
        categories have been assigned.
    """
    with _connect() as connection:
        rows = connection.execute(
            "SELECT DISTINCT category FROM categories ORDER BY category"
        ).fetchall()
    return [row["category"] for row in rows]


def get_note_ids_by_category(category: str) -> list[str]:
    """Find notes assigned to an exact category name.

    Args:
        category: Category name to match exactly, including case.

    Returns:
        Matching note IDs, or an empty list if the category has no notes.
        Use get_note_by_ids to retrieve their full content.
    """
    with _connect() as connection:
        rows = connection.execute(
            "SELECT note_id FROM categories WHERE category = ?",
            (category,),
        ).fetchall()
    return [row["note_id"] for row in rows]


def get_note_ids_by_keyword(keyword: str) -> list[str]:
    """Search note content for a literal, case-sensitive substring.

    Args:
        keyword: Text to find anywhere in note content. This is a literal
            substring, not a regular expression or whole-word search. An empty
            string matches every note.

    Returns:
        Matching note IDs, or an empty list if no content matches.
        Use get_note_by_ids to retrieve their full content.
    """
    with _connect() as connection:
        rows = connection.execute(
            "SELECT id FROM notes WHERE instr(content, ?) > 0",
            (keyword,),
        ).fetchall()
    return [row["id"] for row in rows]


def get_linked_note_ids(note_id: str) -> list[str]:
    """Find all notes connected to a note through any number of links.

    Links are traversed in both directions, including indirect connections.

    Args:
        note_id: Starting note ID for exploring connected notes.

    Returns:
        Unique reachable note IDs, including the starting ID. The starting ID
        is returned even if it does not exist. Result order is unspecified.
        Use get_note_by_ids to retrieve the notes themselves.
    """
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


def get_similar_note_ids(note_id: str, n: int = 10) -> list[tuple[str, float]]:
    """Find notes with content semantically similar to an existing note.

    Args:
        note_id: ID of an existing note whose embedding is used for the search.
        n: Maximum number of other notes to return. Must be a positive integer;
            defaults to 10.

    Returns:
        Pairs of note ID and cosine similarity score, ordered from most to least
        similar. Higher scores indicate greater similarity. Excludes the source
        note and may return fewer than n results. Use get_note_by_ids to retrieve
        the matching notes.
    """
    with _connect() as connection:
        rows = connection.execute(
            """
            WITH nearest AS MATERIALIZED (
                SELECT note_id, distance
                FROM note_embeddings
                WHERE embedding MATCH (
                    SELECT embedding FROM note_embeddings WHERE note_id = ?
                )
                AND k = ?
            )
            SELECT note_id, 1.0 - distance AS similarity
            FROM nearest
            WHERE note_id != ?
            ORDER BY distance
            LIMIT ?
            """,
            (note_id, n + 1, note_id, n),
        ).fetchall()
    return [(row["note_id"], row["similarity"]) for row in rows]


def insert_note(content: str) -> str:
    """Create a note and compute its embedding for semantic similarity searches.

    Assigns a new UUID and the current UTC creation timestamp. Categories and
    links can be added separately with insert_categories and insert_links.

    Args:
        content: Full text to store as the note's content.

    Returns:
        The new note's ID, for retrieving, categorizing, linking, or deleting it.
    """
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
    """Permanently delete a note and its associated categories and links.

    The stored embedding is retained. Does nothing if the note does not exist.

    Args:
        note_id: ID of the note to delete.
    """
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,),
        )


def insert_categories(note_id: str, categories: list[str]) -> None:
    """Assign additional categories to an existing note.

    Preserves current categories. A duplicate category assignment raises a
    database integrity error and rolls back this call's changes.

    Args:
        note_id: ID of the existing note to categorize.
        categories: Category names to add. Names must be distinct within this
            list and must not already be assigned to the note. An empty list
            makes no changes.
    """
    with _connect() as connection, connection:
        connection.executemany(
            "INSERT INTO categories (note_id, category) VALUES (?, ?)",
            ((note_id, category) for category in categories),
        )


def delete_categories(note_id: str) -> None:
    """Remove every category assignment from a note, preserving the note itself.

    Does nothing if the note does not exist or has no categories.

    Args:
        note_id: ID of the note whose category assignments should be removed.
    """
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM categories WHERE note_id = ?",
            (note_id,),
        )


def insert_links(links: list[tuple[str, str]]) -> None:
    """Create bidirectional links between existing notes.

    Each pair is stored in sorted ID order, so reversing a pair represents the
    same link. An existing link or duplicate pair raises a database integrity
    error and rolls back this call's changes.

    Args:
        links: Pairs of existing note IDs to connect. Each pair must represent a
            new, distinct link. An empty list makes no changes.
    """
    with _connect() as connection, connection:
        connection.executemany(
            "INSERT INTO links (note_id_1, note_id_2) VALUES (?, ?)",
            (tuple(sorted(link)) for link in links),
        )


def delete_links(note_id: str) -> None:
    """Remove every direct link to or from a note, preserving the notes.

    Does nothing if the note does not exist or has no links.

    Args:
        note_id: ID of the note whose direct links should be removed.
    """
    with _connect() as connection, connection:
        connection.execute(
            "DELETE FROM links WHERE note_id_1 = ? OR note_id_2 = ?",
            (note_id, note_id),
        )
