from utils.logger import get_logger
import re

logger = get_logger()

QA_PATTERN = re.compile(
    r"(?is)(?:^|\n|\r|\b)(?:q(?:uestion)?|প্রশ্ন)\s*\d*\s*[:\-]\s*"
    r"(?P<question>.*?)\s*"
    r"(?:a(?:nswer)?|উত্তর)\s*[:\-]\s*"
    r"(?P<answer>.*?)\s*"
    r"(?=(?:\b(?:q(?:uestion)?|প্রশ্ন)\s*\d*\s*[:\-])|$)"
)


def _normalize_qa_text(value: str) -> str:
    value = re.sub(r"\s+", " ", (value or "")).strip()
    return value


def extract_qa_chunks(text: str) -> list:
    """Return one chunk per Q&A pair when text contains structured QA patterns."""
    chunks = []
    for match in QA_PATTERN.finditer(text or ""):
        question = _normalize_qa_text(match.group("question"))
        answer = _normalize_qa_text(match.group("answer"))
        if not question or not answer:
            continue
        # Store one document per QA for precise retrieval.
        chunks.append(f"Q: {question}\nA: {answer}")
    return chunks


def chunk_text(text: str, chunk_size: int = 500) -> list:
    try:
        qa_chunks = extract_qa_chunks(text)
        if qa_chunks:
            logger.info(f"Detected {len(qa_chunks)} Q&A pairs; using one-QA-per-chunk mode")
            return qa_chunks

        words = text.split()
        chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Chunking failed: {e}")
        raise