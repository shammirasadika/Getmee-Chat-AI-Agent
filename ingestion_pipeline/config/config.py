import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TEMP_DIR = os.getenv("TEMP_DIR", "./tmp")
    CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
