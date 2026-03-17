from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.file_handler import save_temp_file
from services.text_extractor import extract_text
from services.text_cleaner import clean_text
from services.chunker import chunk_text
from utils.logger import get_logger
import os

router = APIRouter()
logger = get_logger()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save file temporarily
        temp_path = save_temp_file(file)
        # Extract text
        text = extract_text(temp_path, file.filename)
        # Clean text
        cleaned = clean_text(text)
        # Chunk text
        chunks = chunk_text(cleaned)
        # Remove temp file
        os.remove(temp_path)
        return JSONResponse({"text": cleaned, "chunks": chunks})
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
