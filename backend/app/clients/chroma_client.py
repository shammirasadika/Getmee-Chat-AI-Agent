
import chromadb
import os

from app.core.config import settings


def get_chroma_client() -> chromadb.HttpClient:
    """Create and return a ChromaDB HttpClient using environment-based settings."""
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )


class ChromaClient:
    def __init__(self):
        self.client = get_chroma_client()
        self.collection_name = os.getenv("CHROMA_COLLECTION", "getmee_docs_dev")

    def query(self, query_text: str, top_k: int = 5):
        try:
            collection = self.client.get_collection(self.collection_name)
            results = collection.query(query_texts=[query_text], n_results=top_k)
            docs = results.get("documents", [])
            distances = results.get("distances", [])
            # Debug print removed
            return {
                "documents": docs,
                "ids": results.get("ids", []),
                "metadatas": results.get("metadatas", []),
                "embeddings": results.get("embeddings", []),
                "distances": distances
            }
        except Exception as e:
            # Debug print removed
            return {"documents": [], "ids": [], "metadatas": [], "embeddings": [], "distances": []}
