import pytest

from apps.api.app.services.retrieval import retrieve_chunks


@pytest.mark.integration
def test_known_question_returns_expected_chunk_in_top_k(
    db_session,
    monkeypatch,
    motor_finance_chunk,
) -> None:
    monkeypatch.setattr(
        "apps.api.app.services.retrieval.embed_question",
        lambda question: [1.0, 0.0, 0.0],
    )

    candidates = retrieve_chunks(
        db=db_session,
        question="How many motor finance promotions changed?",
    )

    returned_ids = {
        candidate["chunk_id"]
        for candidate in candidates
    }

    assert motor_finance_chunk.id in returned_ids