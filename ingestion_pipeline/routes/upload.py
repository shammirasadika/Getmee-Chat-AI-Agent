from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
 
from services.text_extractor import extract_and_chunk
from utils.logger import get_logger
import os

router = APIRouter()
logger = get_logger()

def embed_and_store_in_chromadb(chunks, metadata):
    from chroma_client import get_collection
    from services.embedding import generate_embedding
    collection = get_collection()
    file_name = metadata.get("filename", "unknown")

    # Replace old chunks for this file to prevent stale mixed-size chunks.
    try:
        collection.delete(where={"file_name": file_name})
        logger.info(f"Deleted previous chunks for file: {file_name}")
    except Exception as e:
        logger.warning(f"Could not delete existing chunks for {file_name}: {e}")

    ids = [f"{metadata.get('filename', 'doc')}_chunk_{i+1}" for i in range(len(chunks))]
    embeddings = [generate_embedding(chunk) for chunk in chunks]
    metadatas = [{
        "document_id": metadata.get("document_id", "doc1"),
        "file_name": file_name,
        "chunk_index": i+1,
        "chunk_type": "qa_pair"
    } for i in range(len(chunks))]
    try:
        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"Stored {len(chunks)} chunks in ChromaDB with metadata: {metadata}")
        return True
    except Exception as e:
        logger.error(f"ChromaDB upsert failed: {e}")
        return False

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    import tempfile
    import os
    import time
    try:
        start_total = time.time()
        logger.info("Upload started")
        step_start = time.time()
        file_content = await file.read()
        logger.info(f"File read: {time.time() - step_start:.3f}s")
        step_start = time.time()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + file.filename.split('.')[-1]) as tmp:
            tmp.write(file_content)
            tmp.flush()
            temp_path = tmp.name
        logger.info(f"Temp file written: {time.time() - step_start:.3f}s")
        step_start = time.time()
        try:
            chunks = extract_and_chunk(temp_path, file.filename)
        finally:
            os.remove(temp_path)
        logger.info(f"Text extracted and chunked: {time.time() - step_start:.3f}s")
        step_start = time.time()
        metadata = {"filename": file.filename}
        embedding_success = embed_and_store_in_chromadb(chunks, metadata)
        logger.info(f"ChromaDB upsert: {time.time() - step_start:.3f}s")
        logger.info(f"Total upload time: {time.time() - start_total:.3f}s")
        if not embedding_success:
            raise Exception("Failed to store document in ChromaDB")
        return JSONResponse({"chunks": chunks, "chromadb_status": "success"})
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
