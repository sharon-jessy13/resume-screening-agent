"""
parser.py
Extracts raw text from resumes in PDF, DOCX, or TXT format.
"""

import os
import pdfplumber
import docx


def extract_text(file_path: str) -> str:
    """Route to the right extractor based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return _extract_docx(file_path)
    elif ext == ".txt":
        return _extract_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext} ({file_path})")


def _extract_pdf(file_path: str) -> str:
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_docx(file_path: str) -> str:
    document = docx.Document(file_path)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def _extract_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_resumes(folder_path: str) -> dict:
    """Load and extract text for every resume in a folder.

    Returns: { filename: raw_text }
    """
    resumes = {}
    supported = (".pdf", ".docx", ".txt")
    for fname in sorted(os.listdir(folder_path)):
        if fname.lower().endswith(supported):
            full_path = os.path.join(folder_path, fname)
            try:
                resumes[fname] = extract_text(full_path)
            except Exception as e:
                print(f"[warn] Failed to parse {fname}: {e}")
    return resumes
