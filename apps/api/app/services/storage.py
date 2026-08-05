from pathlib import Path
from uuid import UUID

ROOT_STORAGE_PATH = Path("data/raw")

def extenshion_for_content_type(content_type: str) -> str:
    media_type = content_type.split(";", 1)[0].strip().lower()

    extensions = {
        "text/html": ".html",
        "application/xhtml+xml": ".html",
        "application/pdf": ".pdf",
        "text/plain": ".txt",
    }

    return extensions.get(media_type, ".bin")


def save_raw_content(
        run_id: UUID,
        raw_content: bytes,
        content_type: str
) -> str:
    """
    Save original downloaded bytes and return a relative storage path.
    """

    extension = extenshion_for_content_type(content_type)

    absolute_path = ROOT_STORAGE_PATH / str(run_id) / f"source{extension}"

    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(raw_content)

    return str(absolute_path.relative_to(ROOT_STORAGE_PATH.parent))





