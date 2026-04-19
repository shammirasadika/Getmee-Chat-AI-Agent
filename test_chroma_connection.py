"""
Quick connectivity test for self-hosted ChromaDB.

Usage:
    python test_chroma_connection.py

Requires CHROMA_HOST and CHROMA_PORT env vars (defaults: localhost:8000).
"""
import os
import sys

# Allow running from both backend/ and ingestion_pipeline/
# by using chromadb directly with env vars.
import chromadb


def get_chroma_client() -> chromadb.HttpClient:
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8000"))
    return chromadb.HttpClient(host=host, port=port)


def main():
    host = os.getenv("CHROMA_HOST", "localhost")
    port = os.getenv("CHROMA_PORT", "8000")
    print(f"Connecting to ChromaDB at {host}:{port} ...")

    try:
        client = get_chroma_client()
        heartbeat = client.heartbeat()
        print(f"Heartbeat: {heartbeat}")
        print("ChromaDB connection OK")
    except Exception as e:
        print(f"ChromaDB connection FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    # List collections
    try:
        collections = client.list_collections()
        print(f"Collections ({len(collections)}):")
        for c in collections:
            print(f"  - {c.name}")
    except Exception as e:
        print(f"Could not list collections: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
