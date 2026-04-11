import os
import redis
import json

# Set your Upstash Redis URL and token here or via environment variables
REDIS_URL = os.getenv("REDIS_URL", "<YOUR_UPSTASH_REDIS_REST_URL>")
REDIS_TOKEN = os.getenv("REDIS_TOKEN", "<YOUR_UPSTASH_REDIS_REST_TOKEN>")

# For Upstash REST API, use redis-py with from_url
r = redis.from_url(REDIS_URL, password=REDIS_TOKEN)

# List all session keys
pattern = "session:*"
keys = r.keys(pattern)

# Debug print statements removed
