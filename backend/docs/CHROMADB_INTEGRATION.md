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

Copy the ChromaDB-related variables to your `backend/.env` file. Example:

```
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION=getmee_docs_dev
```

> **Note:** The backend connects to ChromaDB via HTTP (host/port), not by direct file path. Do not use CHROMA_DB_PATH or CHROMA_DB_IMPL in backend .env for server mode.

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
uvicorn main:app --reload   or python main.py
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
