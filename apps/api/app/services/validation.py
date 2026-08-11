from config.config import settings

def validate_retrieval_quality(
        candidates: list[dict]
) -> tuple[bool, str | None]:

    if not candidates:
        return False, "no retrieval candidates found"

    threshold = settings.similarity_threshold

    strong = [ c for c in candidates if c["similarity"] >= threshold ]

    if len(strong) < settings.min_credible_chunks:
        return (
            False,
            "Too few high-similarity chunks to support a reliable answer.",
        )

    return True, None
    