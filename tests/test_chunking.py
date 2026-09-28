import pytest

from app.chunking import build_chunks_with_metadata, chunk_text


def test_short_text_returns_single_chunk():
    assert chunk_text("hello world", chunk_size=50, overlap=10) == ["hello world"]


def test_empty_text_returns_no_chunks():
    assert chunk_text("", chunk_size=50, overlap=10) == []
    assert chunk_text("   ", chunk_size=50, overlap=10) == []


def test_long_text_is_split_into_multiple_chunks():
    text = "a" * 250
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_chunks_overlap():
    text = "".join(str(i % 10) for i in range(300))
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    # the last 20 chars of one chunk should be the first 20 chars of the next
    assert chunks[0][-20:] == chunks[1][:20]


def test_all_text_is_covered():
    text = "".join(chr(97 + i % 26) for i in range(1000))
    chunks = chunk_text(text, chunk_size=120, overlap=30)
    assert chunks[0].startswith(text[:10])
    assert chunks[-1].endswith(text[-10:])


@pytest.mark.parametrize("size,overlap", [(0, 0), (-5, 0), (100, 100), (100, 150), (100, -1)])
def test_invalid_settings_raise(size, overlap):
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=size, overlap=overlap)


def test_metadata_is_attached_to_every_chunk():
    pages = [(1, "a" * 600), (2, "b" * 100)]
    records = build_chunks_with_metadata(pages, pillar="Security")
    assert records
    assert all(r["pillar"] == "Security" for r in records)
    assert {r["page"] for r in records} == {1, 2}
    assert len({r["id"] for r in records}) == len(records)  # ids are unique
