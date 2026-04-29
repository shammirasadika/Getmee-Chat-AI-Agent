import os

from chroma_client import get_chroma_client

# Get collection name from environment variable (required)
collection_name = os.environ["CHROMA_COLLECTION"]

# Use HTTP client for server mode (recommended in your codebase)
client = get_chroma_client()

# Create or get collection (dimension will be set by first upsert)
collection = client.get_or_create_collection(
    name=collection_name
)
