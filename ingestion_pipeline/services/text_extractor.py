import os
from utils.logger import get_logger
from docx import Document
import PyPDF2

logger = get_logger()

def extract_text(file_path: str, filename: str) -> str:
    ext = filename.split('.')[-1].lower()
    try:
        if ext == 'pdf':
            return extract_pdf(file_path)
        elif ext == 'docx':
            return extract_docx(file_path)
        elif ext == 'txt':
            return extract_txt(file_path)
        else:
            raise ValueError('Unsupported file type')
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise

def extract_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def extract_docx(file_path: str) -> str:
    doc = Document(file_path)
    return '\n'.join([p.text for p in doc.paragraphs])

def extract_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()