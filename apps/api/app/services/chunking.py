from langchain_text_splitters import RecursiveCharacterTextSplitter
from dataclasses import dataclass
from uuid import UUID
from langchain_core.documents import Document



@dataclass(frozen=True)
class ChunkingConfig:
    version: str = "v1"
    chunk_size_chars: int = 4000
    chunk_overlap_chars: int = 400

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


def create_chunk_records(
        document_id: UUID,
        source_url: str,
        document_title: str,
        published_on: str,
        page_no: int,
        chunk_order: int,
        sector: str,
        document_type: str,
        text: str
        ):

    chunks = chunk_text(text)

    for chunk_index, chunk in enumerate(chunks):
        pass
    


