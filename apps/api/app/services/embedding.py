import voyageai
from config.config import settings

client = voyageai.Client(api_key=settings.embedding_model_api_key)

'''
def prepare_question_embedding_text(question: str) -> str:
    return f"task: question answering | query: {question}"


def prepare_document_embedding_text(
    chunk_text: str,
    document_title: str | None,
    section_heading: str | None, 
    ) -> str:

    title = document_title or "none"
    heading = section_heading or "none"

    return (
        f"title: {title} | "
        f"section: {heading} | "
        f"text: {chunk_text}"
    )
 '''

def embed_documents(texts: list[str]) -> list[list[float]]:
    result = client.embed(
        texts=texts,
        model=settings.embedding_model,
        input_type="document"
        )

    embeddings = result.embeddings

    for embedding in embeddings:
        if len(embedding) != settings.embedding_dimensions:
            raise ValueError(
                "Embedding dimension does not match EMBEDDING_DIMENSIONS."
                
            ) 

    return embeddings

def embed_question(question: str) -> list[float]:
    result = client.embed(
        texts=[question],
        model=settings.embedding_model,
        input_type="query"

    )

    embedding = result.embeddings[0]

    if len(embedding) != settings.embedding_dimensions:
        raise ValueError(
                "Embedding dimension does not match EMBEDDING_DIMENSIONS."
                )

    return embedding

    
