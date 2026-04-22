from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger("embedding")

logger.info("Before loading embedding model")
model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("After loading embedding model")

def generate_embedding(text):
    logger.info("Before single encode")
    embedding = model.encode(text, convert_to_numpy=True)
    logger.info("After single encode")
    return embedding.tolist()

def generate_embeddings_in_batches(chunks, batch_size=2):
    logger.info(f"Before batch encode: {len(chunks)} chunks")
    embeddings = model.encode(
        chunks,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    logger.info("After batch encode")
    return embeddings.tolist()