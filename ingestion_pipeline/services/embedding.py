from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger("embedding")

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings_in_batches(chunks, batch_size=4):
    """
    Generate embeddings for all chunks using batch processing.
    This ensures efficient memory usage and stable performance.
    """
    try:
        logger.info(f"Generating embeddings for {len(chunks)} chunks")

        embeddings = model.encode(
            chunks,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        logger.info("Embedding generation completed")

        return embeddings.tolist()

    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise