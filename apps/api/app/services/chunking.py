from langchain_text_splitters import RecursiveCharacterTextSplitter
from dataclasses import dataclass

from langchain_core.documents import Document
import re


from apps.api.app.services.embedding import embed_documents




@dataclass(frozen=True)
class ChunkingConfig:
    version: str = "v1"
    chunk_size_chars: int = 4000
    chunk_overlap_chars: int = 400

@dataclass
class ChunkDraft:
    chunk_index: int
    char_start: int
    char_end: int
    text: str | None
    heading: str | None
    page_no: int | None = None
    embedding: list[float] | None = None



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


def get_pdf_heading(
        page_no: int | None,
        headings: list[tuple[str, int]] | None
) -> str | None:

    if page_no is None or not headings:
        return None

    matching_headings = [heading for heading, page in headings if page <= page_no]

    if not matching_headings:
        return None


    return matching_headings[-1]



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


def draft_chunk_records(
        text: str, 
        headings: list[tuple[str, int]]
        ) -> list[ChunkDraft]:

    chunks = chunk_text(text)
    chunk_drafts: list[ChunkDraft] = []
    chunk_texts: list[str] = []

    for chunk_index, chunk in enumerate(chunks):
        char_start = chunk.metadata["start_index"]

        char_end = char_start + len(chunk.page_content)

        page_number = get_pdf_page_number(text, char_start)

        pdf_heading = get_pdf_heading(page_number, headings)


        chunk_draft = ChunkDraft(
            chunk_index=chunk_index,
            char_start=char_start,
            char_end=char_end,
            page_no=page_number,
            text=chunk.page_content,
            heading=pdf_heading
           
            )

        chunk_drafts.append(chunk_draft)
        chunk_texts.append(chunk.page_content)

    embeddings = embed_documents(chunk_texts)

    for draft, embedding in zip(chunk_drafts, embeddings, strict=True):
        draft.embedding = embedding




    return chunk_drafts
    


