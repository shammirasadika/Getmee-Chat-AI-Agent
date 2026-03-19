import re
from utils.logger import get_logger

logger = get_logger()

def clean_text(text: str) -> str:
    try:
        # Remove extra whitespace, non-printable chars, etc.
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = cleaned.strip()
        logger.info("Text cleaned")
        return cleaned
    except Exception as e:
        logger.error(f"Text cleaning failed: {e}")
        raise