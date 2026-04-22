from sentence_transformers import SentenceTransformer
import logging

# Load the model once at module level for efficiency
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim

def generate_embedding(text):
    """
    Generate a 384-dim embedding for the given text using sentence-transformers.
    """
    embedding = model.encode(text)
    return embedding.tolist()

def generate_embeddings_in_batches(chunks, batch_size=4):
    """
    Generate embeddings for all chunks in small batches to reduce memory usage.
    Returns a list of embeddings (as lists).
    """
    logger = logging.getLogger("embedding")
    logger.info(f"Starting batch embedding generation: {len(chunks)} chunks, batch_size={batch_size}")
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        logger.info(f"Encoding batch {i//batch_size+1}: {len(batch)} chunks")
        embeddings = model.encode(batch, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False)
        logger.info(f"Batch {i//batch_size+1} encoded")
        all_embeddings.extend(embeddings.tolist())
    logger.info(f"Completed embedding generation for {len(chunks)} chunks.")
    return all_embeddings
