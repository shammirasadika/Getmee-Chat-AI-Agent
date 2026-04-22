from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger("embedding")

# Load model once
logger.info("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("Embedding model loaded successfully.")

def generate_embedding(text):
    """
    Generate a 384-dim embedding for a single text.
    """
    try:
        logger.info("Generating embedding for single text...")
        embedding = model.encode(text, convert_to_numpy=True)
        logger.info("Single embedding generated.")
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error in generate_embedding: {e}")
        raise


def generate_embeddings_in_batches(chunks, batch_size=2):
    """
    Generate embeddings for all chunks in small batches to reduce memory usage.
    Returns a list of embeddings.
    """
    logger.info(f"Starting batch embedding generation: {len(chunks)} chunks, batch_size={batch_size}")

    all_embeddings = []

    try:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            logger.info(f"Encoding batch {i//batch_size + 1}: {len(batch)} chunks")

            embeddings = model.encode(
                batch,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )

            logger.info(f"Batch {i//batch_size + 1} encoded")

            all_embeddings.extend(embeddings.tolist())

        logger.info(f"Completed embedding generation for {len(chunks)} chunks.")

        return all_embeddings

    except Exception as e:
        logger.error(f"Error in batch embedding: {e}")
        raise
