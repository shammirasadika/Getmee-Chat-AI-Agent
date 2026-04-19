import os
import chromadb

from config.config import Config


def get_chroma_client() -> chromadb.HttpClient:
    """Create and return a ChromaDB HttpClient using environment-based settings."""
    return chromadb.HttpClient(
        host=Config.CHROMA_HOST,
        port=Config.CHROMA_PORT,
    )


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=os.getenv("CHROMA_COLLECTION", "getmee_docs_dev")
    )
