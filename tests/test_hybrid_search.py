"""Acceptance criteria for Lab 02 Step 4a (hybrid search via RRF)."""

import sqlite3

import chromadb
import pytest

from app.documents import init_db
from app.hybrid_search import reciprocal_rank_fusion, search_hybrid
from app.search import SearchResult, create_fts_index
from app.search import index_chunks as index_chunks_fts
from app.semantic_search import create_collection
from app.semantic_search import index_chunks as index_chunks_vector


def result(chunk_id: str, score: float = 0.0) -> SearchResult:
    return SearchResult(chunk_id=chunk_id, document_id="doc", text=chunk_id, score=score)


def ids(results: list[SearchResult]) -> list[str]:
    return [r.chunk_id for r in results]


def test_rrf_scores_by_reciprocal_rank():
    fused = reciprocal_rank_fusion([[result("a"), result("b")]], k=2)

    assert [r.score for r in fused] == pytest.approx([1 / 61, 1 / 62])


def test_rrf_chunk_found_by_both_retrievers_outranks_single_list_winners():
    keyword = [result("x"), result("shared")]
    vector = [result("y"), result("shared")]

    fused = reciprocal_rank_fusion([keyword, vector], k=3)

    assert ids(fused)[0] == "shared"
    assert fused[0].score == pytest.approx(2 / 62)


def test_rrf_ignores_input_score_scale():
    """BM25's large scores must not let the keyword list dominate the vector list."""
    keyword = [result("kw-top", score=25.0), result("both", score=24.0)]
    vector = [result("both", score=0.9), result("vec-only", score=0.8)]

    fused = reciprocal_rank_fusion([keyword, vector], k=3)

    assert ids(fused) == ["both", "kw-top", "vec-only"]


def test_rrf_returns_each_chunk_once():
    fused = reciprocal_rank_fusion([[result("a"), result("b")], [result("b"), result("a")]], k=5)

    assert sorted(ids(fused)) == ["a", "b"]


def test_rrf_respects_k_limit():
    fused = reciprocal_rank_fusion([[result("a"), result("b"), result("c")]], k=2)

    assert ids(fused) == ["a", "b"]


CHUNKS = [
    (
        "storage-0",
        "storage",
        0,
        "The archive storage array is nearing capacity at 92% utilisation.",
    ),
    ("vpn-0", "vpn", 0, "Remote engineers cannot reach the EU data center over the VPN."),
    ("vpn-1", "vpn", 1, "VPN is not required to reach publicly accessible resources."),
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
    create_fts_index(connection)
    index_chunks_fts(connection)
    return connection


@pytest.fixture
def collection(conn):
    created = create_collection(chromadb.EphemeralClient())
    index_chunks_vector(conn, created)
    return created


def test_search_hybrid_recovers_paraphrase_that_fulltext_misses(conn, collection):
    results = search_hybrid(conn, collection, "disk filling up", k=3)

    assert results[0].chunk_id == "storage-0"


def test_search_hybrid_finds_exact_keyword_match(conn, collection):
    results = search_hybrid(conn, collection, "dashboard logo", k=3)

    assert results[0].chunk_id == "ui-0"
    assert results[0].document_id == "ui"
