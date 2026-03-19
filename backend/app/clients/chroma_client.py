
import chromadb
from app.core.config import settings
import os

class ChromaClient:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        # Use collection name from environment or default
        self.collection_name = os.getenv("CHROMA_COLLECTION", "getmee_docs_dev")

    def query(self, query_text: str, top_k: int = 5):
        collection = self.client.get_collection(self.collection_name)
        # Use query_texts for text search
        results = collection.query(query_texts=[query_text], n_results=top_k)
        return results
