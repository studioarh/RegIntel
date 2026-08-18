from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date

import fitz
import httpx
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
    pdf_headings: list[tuple[str, int]] | None = None


def normalize_text(text: str) -> str:
    """
    Preserve paragraph breaks while normalising line endings,
    repeated spaces, and excessive blank lines.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
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

     for tag in soup(["script", "style", "noscript", "template", "svg", "iframe"]):
          tag.decompose()

     title_tag = soup.find("meta", property="og:title")

     title = title_tag.get("content", "").strip() if title_tag else None

     if not title:
          page_title = soup.find("title")
          title = page_title.get_text(" ", strip=True) if page_title else None

     published_meta = (
          soup.find("meta", property="article:published_time")
          or soup.find("meta", attrs={"name" : "date"})
          or soup.find("meta", attrs={"name" : "DC.date"}) 
     )

     published_value = (
          published_meta.get("content") if published_meta else None
     )

     parts: list[str] = []

     for element in soup(
          ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "pre"]
          ):

          value = element.get_text(" ", strip=True)

          if not value:
               continue

          if element.name.startswith("h"):
               level = int(element.name[1])
               parts.append(f"{'#' * level} {value}")
          else:
               parts.append(value)

     text = require_meaningful_text("\n\n".join(parts))


     return ExtractedDocument(
        title=title or None,
        text=text,
        published_at=parse_published_at(published_value),
        source_url=source_url,
        content_type=content_type,
        pages=None,
    )

def extract_pdf(
          raw_content: bytes, 
          source_url: str,
          content_type: str,
          ) -> ExtractedDocument:

          try:
               pdf = fitz.open(stream=raw_content, filetype="pdf")
          except Exception as exc:
               raise ExtractionError("The PDF could not be opened.") from exc

          try:
               pages = [
                    normalize_text(page.get_text("text", sort=True)) for page in pdf
                    ]

               pages = [page for page in pages if page]
               headings = [(heading, page) for _, heading, page in pdf.get_toc() if heading]

          finally:
               pdf.close()


          text = require_meaningful_text(
               "\n\n".join(
                    f"--- Page {index} ---\n{page_text}" for index, page_text in enumerate(pages, start=1)
               )
               )

          
          
          return ExtractedDocument(
               title=headings[0][0] if headings else None,
               text=text,
               published_at=None,
               source_url=source_url,
               content_type=content_type,
               pages=pages,
               pdf_headings=headings or None
               )

def extract_plain_text(
          raw_content: bytes,
          source_url: str,
          content_type: str
          ) -> ExtractedDocument:

     text = require_meaningful_text(
          raw_content.decode("utf-8", errors="replace")
          )

     return ExtractedDocument(
        title=None,
        text=text,
        published_at=None,
        source_url=source_url,
        content_type=content_type,
        pages=None,
    )


def extract_document(
          raw_content: bytes,
          source_url: str,
          content_type: str
) -> ExtractedDocument:

     """
    Dispatch based on the HTTP Content-Type header.
    Removes header parameters such as '; charset=utf-8'.
    """  
     media_type = content_type.split(";", 1)[0].strip().lower()

     if media_type in {"text/html", "application/xhtml+xml"}:
        return extract_html(raw_content, source_url, media_type)

     if media_type == "application/pdf":
        return extract_pdf(raw_content, source_url, media_type)

     if media_type == "text/plain":
        return extract_plain_text(raw_content, source_url, media_type)

     raise ExtractionError(
        f"Unsupported content type: {media_type or 'missing Content-Type'}."
    )

    


        

            
            

            
            
            