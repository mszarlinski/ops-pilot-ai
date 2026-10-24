"""Acceptance criteria for Lab 02 Step 3 (semantic search).

The first run downloads Chroma's default embedding model (~80MB), so expect
it to be slow once and fast afterwards.
"""

import sqlite3

import chromadb
import pytest

from app.documents import init_db
from app.search import create_fts_index, search_fulltext
from app.search import index_chunks as index_chunks_fts
from app.semantic_search import create_collection, index_chunks, search_semantic

# Deliberately worded so that "disk filling up" shares no vocabulary with the
# storage chunk it should retrieve — the paraphrase case FTS cannot handle.
CHUNKS = [
    (
        "storage-0",
        "storage",
        0,
        "The archive storage array is nearing capacity at 92% utilisation.",
    ),
    ("vpn-0", "vpn", 0, "Remote engineers cannot reach the EU data center over the VPN."),
    ("ui-0", "ui", 0, "The dashboard logo is misaligned on the homepage."),
]


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    init_db(connection)
    connection.executemany(
        "INSERT INTO chunks (id, document_id, chunk_index, text) VALUES (?, ?, ?, ?)",
        CHUNKS,
    )
    connection.commit()
    return connection


@pytest.fixture
def collection(conn):
    created = create_collection(chromadb.EphemeralClient())
    index_chunks(conn, created)
    return created


def test_search_semantic_returns_best_match_first(collection):
    results = search_semantic(collection, "VPN access for remote engineers", k=3)

    assert results[0].chunk_id == "vpn-0"


def test_search_semantic_reports_document_id(collection):
    results = search_semantic(collection, "VPN access for remote engineers", k=3)

    assert results[0].document_id == "vpn"


def test_search_semantic_respects_k_limit(collection):
    results = search_semantic(collection, "storage", k=1)

    assert len(results) == 1


def test_search_semantic_scores_are_higher_is_better(collection):
    results = search_semantic(collection, "VPN access for remote engineers", k=3)

    assert [result.score for result in results] == sorted(
        (result.score for result in results), reverse=True
    )


def test_semantic_search_finds_paraphrase_that_fulltext_misses(conn, collection):
    """The whole point of Step 3: recall on a query with no shared vocabulary."""
    query = "disk filling up"

    create_fts_index(conn)
    index_chunks_fts(conn)
    keyword_results = search_fulltext(conn, query, k=3)
    semantic_results = search_semantic(collection, query, k=3)

    assert keyword_results == []
    assert semantic_results[0].chunk_id == "storage-0"
