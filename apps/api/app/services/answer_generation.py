from apps.api.app.services.retrieval import retrieve_chunks

from sqlalchemy.orm import Session
from datetime import date
from config.config import settings


def generate_answer(
    db: Session,
    question: str,
    published_after: date | None = None,
    published_before: date | None = None,
) -> list[dict]:

    answer_candidates = retrieve_chunks(
     db=db,
     question=question,
     published_before=published_before,
     published_after=published_after
     )

    if len(answer_candidates) < settings.min_credible_chunks:
        raise ValueError(
        "Insufficient supporting material was retrieved."
        )

    answer_context = answer_candidates[:settings.answer_context_count]

    return answer_context

