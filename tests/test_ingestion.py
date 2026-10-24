import sqlite3
from pathlib import Path

from app.documents import ingest_documents


def test_ingest_documents_chunks_and_persists(tmp_path: Path):
    doc_path = tmp_path / "sample.md"
    doc_path.write_text("word " * 300)  # long enough to require multiple chunks

    conn = sqlite3.connect(":memory:")

    count = ingest_documents(tmp_path, conn, chunk_size=500, overlap=50)

    rows = conn.execute(
        "SELECT document_id, chunk_index, text FROM chunks ORDER BY chunk_index"
    ).fetchall()

    assert count == len(rows)
    assert count > 1
    assert all(document_id == "sample" for document_id, _, _ in rows)
    assert [chunk_index for _, chunk_index, _ in rows] == list(range(count))
