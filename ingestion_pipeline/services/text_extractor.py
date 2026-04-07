
import os
import re
from utils.logger import get_logger
from docx import Document
import PyPDF2
import pandas as pd
import json
from .chunker import chunk_text

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
        elif ext == 'xlsx':
            return extract_excel(file_path)
        elif ext == 'csv':
            return extract_csv(file_path)
        elif ext == 'json':
            return extract_json(file_path)
        else:
            raise ValueError('Unsupported file type')
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise

def clean_text_light(text: str) -> str:
    """
    Lightweight cleaning: remove non-printable chars, normalize line endings, preserve paragraphs/line breaks.
    """
    # Remove non-printable characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Normalize multiple spaces (but preserve line breaks)
    text = re.sub(r'[ ]{2,}', ' ', text)
    # Reduce excessive newlines to max two
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove trailing spaces on each line
    text = '\n'.join([line.rstrip() for line in text.split('\n')])
    return text

def detect_faq_format(text: str) -> bool:
    """
    Detect if text is FAQ/Q&A style (e.g., Q: ... A: ... or numbered Q&A pairs).
    Returns True if FAQ-like, else False.
    """
    # Flexible Q/A patterns (case-insensitive)
    q_patterns = [r'\bq\d{0,2}[:.)\-]', r'\bquestion\b', r'\bq[:.)\-]']
    a_patterns = [r'\ba\d{0,2}[:.)\-]', r'\banswer\b', r'\ba[:.)\-]']
    q_count = 0
    a_count = 0
    for line in text.split('\n'):
        l = line.strip().lower()
        if any(re.match(p, l) for p in q_patterns):
            q_count += 1
        if any(re.match(p, l) for p in a_patterns):
            a_count += 1
    # At least 3 Qs and 3 As, or multiple repeating Q/A patterns
    if q_count >= 3 and a_count >= 3:
        logger.info("Detected FAQ/Q&A style document")
        return True
    logger.info("General document format detected")
    return False

def chunk_faq(text: str) -> list:
    """
    Chunk FAQ/Q&A text by question-answer pairs.
    Each chunk = one Q + one A. Handles multi-line answers, ignores category headers.
    """
    # Pattern for Q: (Q1:, Q:, Question: etc.)
    q_pattern = re.compile(r'^(q\d{0,2}[:.)\-]|question[:.)\-]?)', re.IGNORECASE)
    a_pattern = re.compile(r'^(a\d{0,2}[:.)\-]|answer[:.)\-]?)', re.IGNORECASE)
    lines = text.split('\n')
    chunks = []
    current_q = None
    current_a = []
    mode = None
    for line in lines:
        l = line.strip()
        if q_pattern.match(l):
            # Save previous Q&A
            if current_q and current_a:
                chunk = f"Question: {current_q}\nAnswer: {' '.join(current_a).strip()}"
                chunks.append(chunk)
            current_q = l
            current_a = []
            mode = 'q'
        elif a_pattern.match(l):
            mode = 'a'
        elif mode == 'a':
            current_a.append(l)
        elif mode == 'q' and not q_pattern.match(l) and not a_pattern.match(l):
            # Allow multi-line questions
            current_q += ' ' + l
    # Save last Q&A
    if current_q and current_a:
        chunk = f"Question: {current_q}\nAnswer: {' '.join(current_a).strip()}"
        chunks.append(chunk)
    # Failsafe: fallback if parsing fails or 0 chunks
    if len(chunks) == 0:
        logger.warning("FAQ detected but Q&A chunking failed, falling back to general chunking.")
        return None
    return chunks

def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    General chunking for normal documents, with overlap. Preserves paragraphs.
    """
    # Fallback chunking: ignore paragraph structure, chunk by words
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

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

def extract_excel(file_path: str) -> str:
    df = pd.read_excel(file_path)
    df = preprocess_tabular(df)
    return df.to_csv(index=False)

def extract_csv(file_path: str) -> str:
    df = pd.read_csv(file_path)
    df = preprocess_tabular(df)
    return df.to_csv(index=False)

def extract_json(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # If JSON is a list of dicts or dict of lists, convert to DataFrame
    if isinstance(data, list):
        df = pd.DataFrame(data)
        df = preprocess_tabular(df)
        return df.to_csv(index=False)
    elif isinstance(data, dict):
        try:
            df = pd.DataFrame(data)
            df = preprocess_tabular(df)
            return df.to_csv(index=False)
        except Exception:
            return json.dumps(data)
    else:
        return json.dumps(data)

def preprocess_tabular(df: pd.DataFrame) -> pd.DataFrame:
    """
    Modular preprocessing for tabular data:
    - Drop or fill NaN
    - Remove duplicates
    - Normalize/standardize columns
    - Filter irrelevant columns (customize as needed)
    - Convert data types
    - Clean text columns
    """
    # Drop rows with all NaN
    df = df.dropna(how='all')
    # Fill remaining NaN with empty string or 0 (customize as needed)
    df = df.fillna("")
    # Remove duplicates
    df = df.drop_duplicates()
    # Example: Normalize column names
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
    # Example: Clean text columns
    for col in df.select_dtypes(include=['object']):
        df[col] = df[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
    # (Add more steps as needed)
    return df


def chunk_text_by_paragraph(text):
    """
    Splits text into chunks by paragraph (separated by two newlines).
    Returns a list of paragraphs (non-empty, stripped).
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs

def extract_and_chunk(file_path: str, filename: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Main entry: extract text, clean, detect structure, chunk, and log.
    Returns list of chunks.
    """
    text = extract_text(file_path, filename)
    text = clean_text_light(text)
    is_faq = detect_faq_format(text)
    if is_faq:
        chunks = chunk_faq(text)
        if chunks is None:
            # Failsafe fallback
            chunks = chunk_document(text, chunk_size=chunk_size, overlap=overlap)
            mode = "General (fallback)"
        else:
            mode = "Q&A"
    else:
        chunks = chunk_document(text, chunk_size=chunk_size, overlap=overlap)
        mode = "General"
    logger.info(f"Chunking mode: {mode}")
    logger.info(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):
        logger.info(f"Chunk {i+1} preview: {chunk[:200]}")
    return chunks