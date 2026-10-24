from app.chunking import chunk_text


def test_chunk_text_splits_into_overlapping_chunks():
    text = "abcdefghij"  # 10 chars

    chunks = chunk_text(text, chunk_size=4, overlap=1)

    assert chunks == ["abcd", "defg", "ghij"]


def test_chunk_text_last_chunk_may_be_shorter():
    text = "abcdefghijk"  # 11 chars

    chunks = chunk_text(text, chunk_size=4, overlap=1)

    assert chunks == ["abcd", "defg", "ghij", "jk"]


def test_chunk_text_returns_single_chunk_when_shorter_than_chunk_size():
    text = "short text"

    chunks = chunk_text(text, chunk_size=500, overlap=50)

    assert chunks == [text]


def test_chunk_text_consecutive_chunks_overlap():
    text = "0123456789" * 10  # 100 chars

    chunks = chunk_text(text, chunk_size=20, overlap=5)

    assert len(chunks) > 1
    for current_chunk, next_chunk in zip(chunks, chunks[1:]):
        assert current_chunk[-5:] == next_chunk[:5]

def test_chunk_empty_text():
    text = ""

    chunks = chunk_text(text, chunk_size=10, overlap=2)

    assert chunks == []