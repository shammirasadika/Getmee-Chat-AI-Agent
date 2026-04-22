
import os
from dotenv import load_dotenv


# Load .env values directly (bypasses any system env vars)
# To use production settings, change '.env' to '.env.production' below:
from pathlib import Path
env_file = '.env'
# env_file = '.env.production'
load_dotenv(env_file)

class Config:
    TEMP_DIR = os.environ["TEMP_DIR"]
    CHROMA_MODE = os.environ["CHROMA_MODE"]
    CHROMA_HOST = os.environ["CHROMA_HOST"]
    CHROMA_PORT = int(os.environ["CHROMA_PORT"])
    CHROMA_PATH = os.environ.get("CHROMA_PATH", "")
    # Chroma Cloud variables
    CHROMA_URL = os.environ.get("CHROMA_URL", "")
    CHROMA_API_KEY = os.environ.get("CHROMA_API_KEY", "")
    CHROMA_TENANT = os.environ.get("CHROMA_TENANT", "")
    CHROMA_DATABASE = os.environ.get("CHROMA_DATABASE", "")
    CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "")
