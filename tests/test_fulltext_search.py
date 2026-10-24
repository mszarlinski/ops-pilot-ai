import sqlite3

import pytest

from app.documents import init_db
from app.search import create_fts_index, index_chunks, search_fulltext


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    init_db(connection)
    connection.executemany(
        "INSERT INTO chunks (id, document_id, chunk_index, text) VALUES (?, ?, ?, ?)",
        [
            ("db-0", "db", 0, "The database connection pool is exhausted, causing timeouts."),
            ("s3-0", "s3", 0, "The S3 bucket is returning 503 errors on every upload."),
            ("ui-0", "ui", 0, "The dashboard logo is misaligned on the homepage."),
        ],
    )
    connection.commit()
    create_fts_index(connection)
    index_chunks(connection)
    return connection


def test_search_fulltext_returns_best_keyword_match_first(conn):
    results = search_fulltext(conn, "database connection", k=5)

    assert results[0].chunk_id == "db-0"


def test_search_fulltext_matches_distinct_topics(conn):
    results = search_fulltext(conn, "logo misaligned", k=5)

    assert results[0].chunk_id == "ui-0"


def test_search_fulltext_returns_empty_for_no_match(conn):
    results = search_fulltext(conn, "quantum entanglement", k=5)

    assert results == []


def test_search_fulltext_respects_k_limit(conn):
    results = search_fulltext(conn, "bucket OR database OR logo", k=1)

    assert len(results) == 1
