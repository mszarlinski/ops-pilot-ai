"""Semantic (vector) search over the chunk corpus using ChromaDB.

Where full-text search in `app.search` matches tokens, this matches *meaning*:
chunks and queries are embedded into vectors, and retrieval is a
nearest-neighbour lookup in that vector space. The payoff is recall on
paraphrases — a query sharing no vocabulary with the chunk it should find.

Step 4 fuses this with the FTS baseline and measures which one earns its cost
on which query shape.
"""

import sqlite3

import chromadb

from app.search import SearchResult

COLLECTION_NAME = "chunks"


def create_collection(client: chromadb.ClientAPI) -> chromadb.Collection:
    """Create (or get) the chunks collection, configured for cosine distance.

    Chroma defaults to squared L2; cosine is the conventional choice for text
    embeddings, because it compares direction rather than magnitude.
    """
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def index_chunks(conn: sqlite3.Connection, collection: chromadb.Collection) -> None:
    """Embed every chunk in the SQLite `chunks` table into the collection.

    Chroma's default embedding function does the embedding. `document_id` is
    stored as metadata so a search result can report its source document.
    Upserting by chunk id keeps repeated calls idempotent, as
    `app.search.index_chunks` is.
    """
    rows = conn.execute("SELECT id, document_id, text FROM chunks").fetchall()
    collection.upsert(
        ids=[row[0] for row in rows],
        metadatas=[{"document_id": row[1]} for row in rows],
        documents=[row[2] for row in rows],
    )


def search_semantic(collection: chromadb.Collection, query: str, k: int = 5) -> list[SearchResult]:
    """Return the top-k chunks most similar to query, best match first.

    Chroma returns cosine *distance* (0.0 means identical, so lower is
    better), but SearchResult.score is higher-is-better, so it is converted
    with `1.0 - distance` to match the FTS baseline's convention.
    """
    hits = collection.query(query_texts=[query], n_results=k)
    return [
        SearchResult(
            chunk_id=chunk_id,
            document_id=metadata["document_id"],
            text=text,
            score=1.0 - distance,
        )
        for chunk_id, metadata, text, distance in zip(
            hits["ids"][0], hits["metadatas"][0], hits["documents"][0], hits["distances"][0]
        )
    ]
