from pathlib import Path

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

