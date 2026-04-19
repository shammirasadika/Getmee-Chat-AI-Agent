import os
import redis
from dotenv import load_dotenv

load_dotenv()

# Get Redis connection details from environment variables or set defaults
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Connect to Redis
r = redis.from_url(REDIS_URL)

# Delete all keys
r.flushdb()
