# ChromaDB Integration Guide

## 1. Start the ChromaDB Server

You must run the ChromaDB server from the correct directory so both ingestion and backend services use the same database.

**From the project root:**

```
chroma run --path ./ingestion_pipeline/chroma-data
```

**Or from inside the ingestion_pipeline folder:**

```
chroma run --path chroma-data
```

Keep this terminal open while using the backend or ingestion scripts.

---

## 2. Backend Environment Variables

Copy the ChromaDB-related variables from `ingestion_pipeline/.env.example` to your `backend/.env` file. Example:

```
CHROMA_DB_IMPL=chromadb.db.impl.sqlite
CHROMA_DB_PATH=../ingestion_pipeline/chroma-data
CHROMA_COLLECTION_NAME=your_collection_name
```

Adjust the path if your backend runs from a different working directory.

---

## 3. Install ChromaDB Python Client in Backend

In your backend virtual environment, run:

```
pip install chromadb
```

---

## 4. Connect to ChromaDB in Backend Code

Use the ChromaDB Python client to connect to the same database as the ingestion pipeline:

```python
import chromadb

# New ChromaDB HTTP client initialization (post-migration)
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_collection("getmee_docs_dev")
# Now you can query the collection
```

---

## 5. Create API Endpoints for Retrieval

Example using FastAPI:

```python
from fastapi import FastAPI, Query
app = FastAPI()

@app.get("/search")
def search(query: str):
        results = collection.query(query_texts=[query], n_results=5)
        return results
```

---

## 6. Run the Backend

Start your backend server (e.g., with Uvicorn for FastAPI):

```
uvicorn main:app --reload
```

---

## 7. Test Retrieval

Use curl, Postman, or your frontend to hit the `/search` endpoint and verify results.

---

## Troubleshooting

- If you get an error like "command not found" for `chroma`, try:
    ```
    python -m chromadb.run --path ./ingestion_pipeline/chroma-data
    ```
- If you see "port already in use," stop any other process using port 8000 or specify a different port:
    ```
    chroma run --path ./ingestion_pipeline/chroma-data --host 127.0.0.1 --port 8001
    ```

---

**Summary:**
- Always run the ChromaDB server from the correct folder so ingestion and backend share the same data.
- Configure backend environment variables to point to the same ChromaDB instance.
- Install the chromadb Python package in your backend environment.
- Connect and query ChromaDB as shown above.
# ChromaDB Integration Guide

This document explains how to access and use ChromaDB from the backend (FastAPI or any Python backend).

---

## 1. Prerequisites
- Ensure ChromaDB server is running and accessible.
- Environment variables (`.env`) must be set:
  - `CHROMA_HOST` (default: localhost)
  - `CHROMA_PORT` (default: 8000)
  - `CHROMA_COLLECTION` (default: getmee_docs_dev)
- The `chroma_client.py` helper is available in the ingestion_pipeline folder.

---

## 2. Accessing ChromaDB in Backend Code

Import the helper and get the collection:
```python
from chroma_client import get_collection

collection = get_collection()
```

---

## 3. Adding Data
```python
collection.add(
    ids=["unique_id_1"],
    documents=["This is a paragraph to store."],
    metadatas=[{"source": "example"}]
)
```

---

## 4. Querying Data (Semantic Search)
```python
results = collection.query(
    query_texts=["search phrase here"],
    n_results=5
)
print(results)
```

---

## 5. Getting All Data
```python
all_data = collection.get()
print(all_data)
```

---

## 6. Deleting Data
```python
ids = collection.get()["ids"]
if ids:
    collection.delete(ids=ids)
```

---

## 7. Chunking Strategy
- Text is chunked by paragraph (split on double newlines) before storing in ChromaDB.
- Each paragraph is stored as a separate document for better search and retrieval.

---

## 8. Management Scripts
- To delete all records: `python delete_chromadb.py`
- To check all records: `python check_chromadb.py`

---

## 9. Example Integration in FastAPI Endpoint
```python
from fastapi import APIRouter
from chroma_client import get_collection

router = APIRouter()

@router.get("/search")
def search_endpoint(q: str):
    collection = get_collection()
    results = collection.query(query_texts=[q], n_results=5)
    return results
```
