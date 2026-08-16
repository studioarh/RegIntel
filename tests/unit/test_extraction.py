from apps.api.app.services.extraction import extract_html,extract_pdf, ExtractionError, extract_document
import pytest
from pathlib import Path

def test_html_extraction_returns_meaningful_text() -> None:

    html = Path("C:/courses/AI Engineer/RegIntel/tests/fixtures/fca_fixture.html").read_bytes()

    extracted_html = extract_html(html,"https://www.fca.org.uk/publications/consultation-papers/cp26-15-reviewing-financial-promotions-rules-consumer-credit","text/html")

    assert "Give firms greater discretion when applying our requirements to" in extracted_html.text


def test_pdf_extraction_returns_meaningful_text() -> None:

    pdf = Path("C:/courses/AI Engineer/RegIntel/tests/fixtures/source.pdf").read_bytes()

    extracted_pdf = extract_pdf(pdf,"https://www.fca.org.uk/publication/regulatory-priorities/consumer-finance-report.pdf","application/pdf")

    assert "We are committed to supporting smaller firms in applying outcomes-based regulation" in extracted_pdf.text


def test_empty_document_extraction_fails_safely() -> None:
    with pytest.raises(ExtractionError):
        extract_document(b"","empty_file.txt","text/plain")


    
