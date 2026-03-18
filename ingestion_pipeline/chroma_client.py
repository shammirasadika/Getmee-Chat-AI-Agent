
import os
from dotenv import load_dotenv
load_dotenv()
import chromadb

def get_collection():
    collection_name = os.getenv("CHROMA_COLLECTION", "getmee_docs_dev")
    api_key = os.getenv("CHROMA_API_KEY", "")
    tenant = os.getenv("CHROMA_TENANT", "")
    database = os.getenv("CHROMA_DATABASE", "")
    if not api_key:
        raise RuntimeError("CHROMA_API_KEY is missing or empty in your environment. Please set it in your .env file.")
    if not tenant:
        raise RuntimeError("CHROMA_TENANT is missing or empty in your environment. Please set it in your .env file.")
    if not database:
        raise RuntimeError("CHROMA_DATABASE is missing or empty in your environment. Please set it in your .env file.")
    client = chromadb.CloudClient(
        api_key=api_key,
        tenant=tenant,
        database=database
    )
    return client.get_or_create_collection(name=collection_name)
