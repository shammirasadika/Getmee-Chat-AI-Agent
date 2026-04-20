import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TEMP_DIR = os.environ["TEMP_DIR"]
    CHROMA_MODE = os.environ["CHROMA_MODE"]
    CHROMA_HOST = os.environ["CHROMA_HOST"]
    CHROMA_PORT = int(os.environ["CHROMA_PORT"])
    CHROMA_PATH = os.environ["CHROMA_PATH"]
