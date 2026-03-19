import chromadb
import os

# Get collection name from environment variable or use default
collection_name = os.getenv("CHROMA_COLLECTION_NAME", "default_collection")

client = chromadb.Client()

# Create collection with 384-dim embeddings
collection = client.create_collection(
    name=collection_name,
    embedding_function=None,
    metadata={"hnsw:space": "cosine"},
    dimension=384
)

print(f"Collection '{collection_name}' created with 384 dimensions.")
