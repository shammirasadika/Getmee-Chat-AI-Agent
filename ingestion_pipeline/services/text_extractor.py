import os
from utils.logger import get_logger
from docx import Document
import PyPDF2
import pandas as pd
import json

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