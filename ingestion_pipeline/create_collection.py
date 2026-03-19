import chromadb
import os

# Get collection name from environment variable or use default
collection_name = os.getenv("CHROMA_COLLECTION_NAME", "default_collection")

# Use HTTP client for server mode (recommended in your codebase)
client = chromadb.HttpClient(
    host=os.getenv("CHROMA_HOST", "localhost"),
    port=int(os.getenv("CHROMA_PORT", "8000"))
)

# Create or get collection (dimension will be set by first upsert)
collection = client.get_or_create_collection(
    name=collection_name
)

print(f"Collection '{collection_name}' created or retrieved.")
