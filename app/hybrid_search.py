"""Hybrid search: fuse the FTS and vector rankings into one result list.

BM25 scores (unbounded, corpus-dependent) and cosine similarities (roughly
0..1) live on different scales, so adding or averaging them lets whichever
retriever has the bigger numbers dominate. Reciprocal Rank Fusion sidesteps
that by ignoring scores entirely and fusing on *rank* alone.
"""

import sqlite3

import chromadb

from app.search import SearchResult, search_fulltext
from app.semantic_search import search_semantic

RRF_K = 60


def reciprocal_rank_fusion(
    result_lists: list[list[SearchResult]], k: int, rrf_k: int = RRF_K
) -> list[SearchResult]:
    """Fuse several best-first result lists into one, best first, top k.

    Each chunk scores the sum, over every list it appears in, of
    `1 / (rrf_k + rank)`, where rank is 1-based; a list a chunk is absent
    from contributes nothing. Each chunk is returned once, with `score` set
    to its fused RRF score.

    The input scores are deliberately ignored: only positions matter.
    """
    fused_scores: dict[str, float] = {}
    first_seen: dict[str, SearchResult] = {}
    for results in result_lists:
        for rank, hit in enumerate(results, start=1):
            fused_scores[hit.chunk_id] = fused_scores.get(hit.chunk_id, 0.0) + 1 / (rrf_k + rank)
            first_seen.setdefault(hit.chunk_id, hit)

    ranked = sorted(fused_scores, key=fused_scores.get, reverse=True)[:k]
    return [
        first_seen[chunk_id].model_copy(update={"score": fused_scores[chunk_id]})
        for chunk_id in ranked
    ]


def search_hybrid(
    conn: sqlite3.Connection, collection: chromadb.Collection, query: str, k: int = 5
) -> list[SearchResult]:
    """Return the top-k chunks for query by fusing FTS and vector results.

    Each retriever is asked for a deeper candidate list (4 * k) than is
    returned, so a chunk ranked just below the cut-off by one retriever can
    still be lifted into the top k by the other.
    """
    candidates = 4 * k
    return reciprocal_rank_fusion(
        [
            search_fulltext(conn, query, k=candidates),
            search_semantic(collection, query, k=candidates),
        ],
        k=k,
    )
