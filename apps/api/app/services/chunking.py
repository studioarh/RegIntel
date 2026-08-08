from langchain_text_splitters import RecursiveCharacterTextSplitter
from dataclasses import dataclass
from uuid import UUID
from langchain_core.documents import Document
import re

from apps.db.models import DocumentChunk



@dataclass(frozen=True)
class ChunkingConfig:
    version: str = "v1"
    chunk_size_chars: int = 4000
    chunk_overlap_chars: int = 400


class ChunkDraft:
    page_no: int | None
    chunk_index: int
    text: str | None



def get_pdf_page_number( 
        document_text: str, 
        char_start: int,
        ) -> int | None:
    
    preceding_text = document_text[:char_start]

    page_numbers = re.findall(
        r"^--- Page (\d+) ---$",
        preceding_text,
        flags=re.MULTILINE,
    )

    return int(page_numbers[-1]) if page_numbers else None


def get_pdf_heading():



def chunk_text(text: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=400,
        separators=[
        "\n\n",  # Paragraph boundary
        "\n",    # Line boundary
        ". ",    # Sentence boundary
        " ",     # Word boundary
        "",      # Hard character split fallback
    ],
    keep_separator=True,
    add_start_index=True
    )

    return splitter.create_documents([text])


def draft_chunk_records(text: str) -> list[ChunkDraft]:

    chunks = chunk_text(text)
    chunk_drafts: list[ChunkDraft] = []

    for chunk_index, chunk in enumerate(chunks):
        char_start = chunk.metadata["start_index"]

        chunk_draft = ChunkDraft(
            page_no=get_pdf_page_number(text, char_start),
            chunk_index=chunk_index,
            text=chunk.page_content
            )

        chunk_drafts.append(chunk_draft)

    return chunk_drafts
    


