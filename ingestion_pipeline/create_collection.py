import os

from chroma_client import get_chroma_client

# Get collection name from environment variable or use default
collection_name = os.getenv("CHROMA_COLLECTION", "getmee_docs_dev")

# Use HTTP client for server mode (recommended in your codebase)
client = get_chroma_client()

# Create or get collection (dimension will be set by first upsert)
collection = client.get_or_create_collection(
    name=collection_name
)
