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

print(f"Found {len(keys)} session keys:")
for key in keys:
    print(f"\nKey: {key.decode() if isinstance(key, bytes) else key}")
    value = r.get(key)
    try:
        # Try to pretty-print JSON values
        print(json.dumps(json.loads(value), indent=2))
    except Exception:
        print(value)
