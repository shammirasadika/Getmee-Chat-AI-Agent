
import chromadb

from app.core.config import settings


def get_chroma_client():
    """
    Create and return a ChromaDB client based on CHROMA_MODE.

    Modes:
        - "local" → PersistentClient
        - "http"  → HttpClient
        - "cloud" → CloudClient
    """
    mode = settings.CHROMA_MODE.lower()

    if mode == "local":
        # ...existing code...
        return chromadb.PersistentClient(path=settings.CHROMA_PATH)

    elif mode == "http":
        # ...existing code...
        return chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )


    elif mode == "cloud":
        # ...existing code...
        return chromadb.CloudClient(
            api_key=settings.CHROMA_API_KEY,
            tenant=settings.CHROMA_TENANT,
            database=settings.CHROMA_DATABASE,
        )

    else:
        raise ValueError(
            f"[ChromaDB] Invalid CHROMA_MODE='{mode}'. "
            "Supported modes: local, http, cloud"
        )


class ChromaClient:
    def __init__(self):
        self.client = get_chroma_client()
        self.collection_name = settings.CHROMA_COLLECTION

    def query(self, query_text: str, top_k: int = 5):
        try:
            collection = self.client.get_collection(self.collection_name)
            results = collection.query(query_texts=[query_text], n_results=top_k)
            docs = results.get("documents", [])
            distances = results.get("distances", [])
            return {
                "documents": docs,
                "ids": results.get("ids", []),
                "metadatas": results.get("metadatas", []),
                "embeddings": results.get("embeddings", []),
                "distances": distances
            }
        except Exception as e:
            # ...existing code...
            return {"documents": [], "ids": [], "metadatas": [], "embeddings": [], "distances": []}
