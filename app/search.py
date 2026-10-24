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

    Lab 02 Step 2 exercise: create an FTS5 virtual table with columns
    (id, document_id, text), where `id` and `document_id` are metadata you
    want to retrieve but not search against (mark them UNINDEXED), and
    `text` is the column FTS5 should tokenize and index.
    """
    raise NotImplementedError("Lab 02 Step 2 exercise: create the chunks_fts FTS5 virtual table")


def index_chunks(conn: sqlite3.Connection) -> None:
    """Populate chunks_fts from the existing chunks table.

    Lab 02 Step 2 exercise: copy (id, document_id, text) from `chunks` into
    `chunks_fts` so it becomes searchable.
    """
    raise NotImplementedError("Lab 02 Step 2 exercise: populate chunks_fts from chunks")


def search_fulltext(conn: sqlite3.Connection, query: str, k: int = 5) -> list[SearchResult]:
    """Return the top-k chunks matching query, ranked by BM25 relevance.

    Lab 02 Step 2 exercise: query chunks_fts with MATCH, rank with bm25(),
    and return results best-match-first. Remember: SQLite's bm25() returns
    more negative values for better matches, so order ascending.
    """
    raise NotImplementedError("Lab 02 Step 2 exercise: implement the MATCH + bm25 query")
