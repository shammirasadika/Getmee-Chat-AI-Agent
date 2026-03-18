from utils.logger import get_logger

logger = get_logger()

def chunk_text(text: str, chunk_size: int = 500) -> list:
    try:
        words = text.split()
        chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Chunking failed: {e}")
        raise