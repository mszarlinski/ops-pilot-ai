"""Hybrid search: fuse the FTS and vector rankings into one result list.

BM25 scores (unbounded, corpus-dependent) and cosine similarities (roughly
0..1) live on different scales, so adding or averaging them lets whichever
retriever has the bigger numbers dominate. Reciprocal Rank Fusion sidesteps
that by ignoring scores entirely and fusing on *rank* alone.
"""

import sqlite3

import chromadb

from app.search import SearchResult

RRF_K = 60


def reciprocal_rank_fusion(
    result_lists: list[list[SearchResult]], k: int, rrf_k: int = RRF_K
) -> list[SearchResult]:
    """Fuse several best-first result lists into one, best first, top k.

    Lab 02 Step 4a exercise: each chunk scores the sum, over every list it
    appears in, of `1 / (rrf_k + rank)`, where rank is 1-based. A chunk that
    is absent from a list contributes nothing for that list. Return each
    chunk once, with `score` set to its fused RRF score.

    The input scores are deliberately ignored: only positions matter.
    """
    raise NotImplementedError("Lab 02 Step 4a exercise: implement reciprocal rank fusion")


def search_hybrid(
    conn: sqlite3.Connection, collection: chromadb.Collection, query: str, k: int = 5
) -> list[SearchResult]:
    """Return the top-k chunks for query by fusing FTS and vector results.

    Lab 02 Step 4a exercise: run `search_fulltext` and `search_semantic`,
    then fuse their result lists with `reciprocal_rank_fusion`. Fetch a
    deeper candidate list than k from each retriever, so a chunk ranked just
    below the cut-off by one retriever can still be lifted by the other.
    """
    raise NotImplementedError("Lab 02 Step 4a exercise: wire both retrievers into RRF")
