import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TEMP_DIR = os.getenv("TEMP_DIR", "./tmp")
