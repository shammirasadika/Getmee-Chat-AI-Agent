import tempfile
import shutil
from fastapi import UploadFile
from utils.logger import get_logger

logger = get_logger()

def save_temp_file(file: UploadFile) -> str:
    try:
        suffix = '.' + file.filename.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name
        logger.info(f"Saved temp file: {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"Failed to save temp file: {e}")
        raise