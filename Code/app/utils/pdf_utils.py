"""PDF and document text extraction."""
from io import BytesIO
from pathlib import Path


def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {e}") from e


def extract_docx_text(file_bytes: bytes) -> str:
    try:
        from docx import Document
        doc = Document(BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        raise ValueError(f"Failed to read DOCX: {e}") from e


def extract_document_text(filename: str, file_bytes: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_pdf_text(file_bytes)
    if ext in (".docx", ".doc"):
        return extract_docx_text(file_bytes)
    if ext == ".txt":
        return file_bytes.decode("utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {ext}")
