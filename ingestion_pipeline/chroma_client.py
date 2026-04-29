import os
import chromadb

from config.config import Config


def get_chroma_client():
    """
    Create and return a ChromaDB client based on CHROMA_MODE.

    Modes:
        - "local" → PersistentClient (local folder via CHROMA_PATH)
        - "http"  → HttpClient (self-hosted server via CHROMA_HOST:CHROMA_PORT)
        - "cloud" → Chroma Cloud (placeholder, not yet implemented)
    """
    mode = Config.CHROMA_MODE.lower()

    if mode == "local":
        print(f"[ChromaDB] Mode: local | Path: {Config.CHROMA_PATH}")
        return chromadb.PersistentClient(path=Config.CHROMA_PATH)

    elif mode == "http":
        print(f"[ChromaDB] Mode: http | Host: {Config.CHROMA_HOST}:{Config.CHROMA_PORT}")
        return chromadb.HttpClient(
            host=Config.CHROMA_HOST,
            port=Config.CHROMA_PORT,
        )

    elif mode == "cloud":
        print("[ChromaDB] Mode: cloud")
        return chromadb.CloudClient(
            api_key=Config.CHROMA_API_KEY,
            tenant=Config.CHROMA_TENANT,
            database=Config.CHROMA_DATABASE,
        )

    else:
        raise ValueError(
            f"[ChromaDB] Invalid CHROMA_MODE='{mode}'. "
            "Supported modes: local, http, cloud"
        )


def get_collection():
    client = get_chroma_client()
    collection_name = os.environ["CHROMA_COLLECTION"]
    return client.get_or_create_collection(name=collection_name)
