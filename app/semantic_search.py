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
    """Create (or get) the chunks collection for vector search.

    Lab 02 Step 3 exercise: create a collection named COLLECTION_NAME on the
    given client, configured for cosine distance. Chroma defaults to squared
    L2; cosine is the conventional choice for text embeddings, because it
    compares direction rather than magnitude.

    Hint: pass `metadata={"hnsw:space": "cosine"}`.
    """
    raise NotImplementedError("Lab 02 Step 3 exercise: create the chunks collection")


def index_chunks(conn: sqlite3.Connection, collection: chromadb.Collection) -> None:
    """Embed every chunk in the SQLite `chunks` table into the collection.

    Lab 02 Step 3 exercise: read (id, document_id, text) from `chunks` and
    add them with `collection.add`, letting Chroma's default embedding
    function do the embedding. Store `document_id` as metadata so a search
    result can report which document it came from.

    Keep this idempotent, as `app.search.index_chunks` is — `collection.upsert`
    is the easy way.
    """
    raise NotImplementedError("Lab 02 Step 3 exercise: embed chunks into the collection")


def search_semantic(
    collection: chromadb.Collection, query: str, k: int = 5
) -> list[SearchResult]:
    """Return the top-k chunks most similar to query, best match first.

    Lab 02 Step 3 exercise: query the collection and map each hit onto the
    same SearchResult shape the FTS baseline returns, so Step 4 can compare
    them directly.

    Note the score convention: Chroma returns cosine *distance* (0.0 means
    identical, so lower is better), but SearchResult.score is higher-is-better.
    Convert with `1.0 - distance`.
    """
    raise NotImplementedError("Lab 02 Step 3 exercise: implement the vector query")
