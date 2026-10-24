"""Document ingestion: load runbook documents, chunk them, and persist to
SQLite.

This is the corpus layer every later Lab 02 step (full-text search, semantic
search, hybrid search) reads from.
"""

import sqlite3
from pathlib import Path

from pydantic import BaseModel

from app.chunking import chunk_text


class Chunk(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text: str


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL
        )
        """
    )
    conn.commit()


def load_documents(directory: Path) -> list[tuple[str, str]]:
    """Return (document_id, text) pairs for every .md file in directory."""
    return [(path.stem, path.read_text()) for path in sorted(directory.glob("*.md"))]


def ingest_documents(
    directory: Path,
    conn: sqlite3.Connection,
    chunk_size: int = 500,
    overlap: int = 50,
) -> int:
    """Chunk every document in directory and insert the chunks into conn.

    Returns the number of chunks inserted.
    """
    init_db(conn)
    count = 0
    for document_id, text in load_documents(directory):
        for index, text_chunk in enumerate(chunk_text(text, chunk_size=chunk_size, overlap=overlap)):
            conn.execute(
                "INSERT INTO chunks (id, document_id, chunk_index, text) VALUES (?, ?, ?, ?)",
                (f"{document_id}-{index}", document_id, index, text_chunk),
            )
            count += 1
    conn.commit()
    return count
