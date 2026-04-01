import re
from utils.logger import get_logger

logger = get_logger()

def clean_text(text: str) -> str:
    try:
        # Preserve line boundaries so downstream Q&A parsing can detect pair markers.
        cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n")
        # Trim trailing spaces per line.
        cleaned = "\n".join(line.strip() for line in cleaned.split("\n"))
        # Collapse repeated spaces/tabs within lines.
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        # Collapse excessive blank lines.
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = cleaned.strip()
        logger.info("Text cleaned")
        return cleaned
    except Exception as e:
        logger.error(f"Text cleaning failed: {e}")
        raise