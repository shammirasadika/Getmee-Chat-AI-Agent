# Ingestion Pipeline

## Folder Structure

- main.py: FastAPI app entry point
- routes/upload.py: File upload API route
- services/file_handler.py: Handles file saving
- services/text_extractor.py: Extracts text from files
- services/text_cleaner.py: Cleans/preprocesses text
- services/chunker.py: Splits text into chunks
- utils/logger.py: Logger setup
- utils/helpers.py: Helper utilities
- config/config.py: Configuration
- .env.example: Example environment variables
- requirements.txt: Python dependencies

## How to Run Locally

1. Copy .env.example to .env and adjust if needed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Start the server:
   ```
   uvicorn main:app --reload
   ```
4. Open Swagger UI at http://localhost:8000/docs

## Sample Request (Swagger/Postman)
- POST /api/upload
- Form-data: file (PDF, DOCX, or TXT)

## Sample Response
```
{
  "text": "...cleaned text...",
  "chunks": ["chunk1", "chunk2", ...]
}
```

## ChromaDB Management

To delete all records from the ChromaDB collection:
```
python delete_chromadb.py
```

To check the current records in the collection:
```
python check_chromadb.py
```

## Chunking Strategy

Text is now chunked by paragraph (split on double newlines) before storing in ChromaDB. This improves search relevance and retrieval quality.

- Each paragraph is stored as a separate chunk/document.
- For best results, ensure your input text uses paragraphs separated by blank lines.
