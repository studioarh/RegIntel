from apps.api.app.services.embedding import embed_question
from apps.db.models import DocumentChunk


def retrieve_chunks(
        question: str
) -> list[dict]:
    query = embed_question(question)

    distance = DocumentChunk.embedding.cosine_distance(query)

    similarity = (1 - distance).label("similarity")

    


