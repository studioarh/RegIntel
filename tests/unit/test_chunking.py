from apps.api.app.services.chunking import draft_chunk_records


def test_chunks_have_embeddings_and_correct_order(
    fake_embed_documents,
) -> None:
    text = (
        "First FCA sentence. "
        "Second FCA sentence. "
        "Third FCA sentence. "
    ) * 100

    chunks = draft_chunk_records(text, [])

    assert len(chunks) >= 2

    assert chunks[0].text
    assert chunks[0].embedding is not None
    assert len(chunks[0].embedding) == 1024

    assert chunks[0].embedding != chunks[1].embedding


def test_adjacent_chunks_overlap(fake_embed_documents) -> None:
    text = " ".join(f"token-{index}" for index in range(500))
    chunks = draft_chunk_records(text, [])

    assert chunks[0].text
    assert chunks[1].text

    trailing_words = chunks[0].text.split()[-25:]
    leading_words = chunks[1].text.split()[:25]
    

    assert any(word in leading_words for word in trailing_words)