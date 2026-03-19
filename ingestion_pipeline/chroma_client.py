import os
import chromadb

def get_collection():
    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8000"))
    )
    return client.get_or_create_collection(
        name=os.getenv("CHROMA_COLLECTION", "getmee_docs_dev")
    )
