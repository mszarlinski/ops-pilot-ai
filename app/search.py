"""Keyword (full-text) search over the chunk corpus using SQLite FTS5.

This is the traditional-retrieval baseline Lab 02 Step 3 (semantic search)
and Step 4 (hybrid search) will be compared against.
"""

import sqlite3

from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    score: float


def create_fts_index(conn: sqlite3.Connection) -> None:
    """Create the chunks_fts virtual table, if it doesn't already exist.

    `id` and `document_id` are UNINDEXED: they come back with every hit as
    metadata, but FTS5 does not tokenize them, so a query can never match a
    chunk on its identifier.
    """
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5 (
            id UNINDEXED,
            document_id UNINDEXED,
            text
        )
        """
    )
    conn.commit()


def index_chunks(conn: sqlite3.Connection) -> None:
    """Populate chunks_fts from the existing chunks table.

    Rebuilds the index from scratch so repeated calls stay idempotent rather
    than inserting every chunk a second time.
    """
    conn.execute("DELETE FROM chunks_fts")
    conn.execute("INSERT INTO chunks_fts (id, document_id, text) SELECT id, document_id, text FROM chunks")
    conn.commit()


def search_fulltext(conn: sqlite3.Connection, query: str, k: int = 5) -> list[SearchResult]:
    """Return the top-k chunks matching query, ranked by BM25 relevance.

    SQLite's bm25() is more negative for better matches, so rows are ordered
    ascending and the sign is flipped on the way out: a higher `score` means
    a better match, which is the convention Step 4's hybrid ranking needs.
    """
    rows = conn.execute(
        """
        SELECT id, document_id, text, bm25(chunks_fts) AS rank
        FROM chunks_fts
        WHERE chunks_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (query, k),
    ).fetchall()
    return [
        SearchResult(chunk_id=row[0], document_id=row[1], text=row[2], score=-row[3])
        for row in rows
    ]
