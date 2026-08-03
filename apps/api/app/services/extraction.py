from __future__ import annotations

import httpx
from dataclasses import dataclass
from datetime import date
import re
import hashlib

from bs4 import BeautifulSoup


MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024
MIN_EXTRACTED_CHARACTERS = 100


class ExtractionError(ValueError):
    """The downloaded content cannot be accepted as a usable document."""

def download_document(url: str) -> tuple[bytes, str, str]:
    with httpx.Client(
        follow_redirects=True,
        timeout=httpx.Timeout(20.0),
    ) as client:

         with client.stream("GET", url) as response:
             response.raise_for_status()
             content_length = response.headers.get("content-length")
             if content_length and int(content_length) > MAX_DOWNLOAD_BYTES:
                 raise ExtractionError(
                      f"Header reports file size ({content_length} bytes) exceeds the limit."
                             )
             buffer = bytearray()
             for chunk in response.iter_bytes():
                             buffer.extend(chunk)
                             if len(buffer) > MAX_DOWNLOAD_BYTES:
                                 raise ExtractionError(
                                     "The downloaded document exceeds the size limit."
                                 )
             
             final_url = str(response.url)
             content_type = response.headers.get("content-type", "")
             return (
                     bytes(buffer),
                     final_url,
                     content_type,
                 )


@dataclass(frozen=True)
class ExtractedDocument:
    title: str | None
    text: str
    published_at: date | None
    source_url: str
    content_type: str
    pages: list[str] | None


def normalize_text(text: str) -> str:
    """
    Preserve paragraph breaks while normalising line endings,
    repeated spaces, and excessive blank lines.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def content_hash(text: str) -> str:
     normalized_text = normalize_text(text)
     encoded_text = normalized_text.encode("utf-8")
     return hashlib.sha256(
          encoded_text
          ).hexdigest()


def require_meaningful_text(text: str) -> str:
     cleaned_text = normalize_text(text)

     if len(cleaned_text) < MIN_EXTRACTED_CHARACTERS:
          raise ExtractionError(
               "The downloaded document contained very little meaningful text."
          )

     if len(re.sub(r"\W+", "", cleaned_text)) < 50:
          raise ExtractionError(
               "The downloaded document didn't contain any meaningful text."
          )

     return cleaned_text


def parse_published_at(value: str | None) -> date | None:
    """
    Accept ISO-formatted HTML metadata dates.
    Unknown formats become None rather than causing ingestion failure
    """

    if not value:
         return None

    value = value.strip()

    try:
         return date.fromisoformat(value[:10])
    except ValueError:
         return None
         

def extract_html(raw_content: bytes,
                 source_url: str,
                 content_type: str
                 ) -> ExtractedDocument:
     
     html = raw_content.decode("utf-8", errors="replace")
     soup = BeautifulSoup(html, "html.parser")
     
    

    


        

            
            

            
            
            