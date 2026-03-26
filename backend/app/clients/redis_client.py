# Redis integration (Upstash/cloud-ready)

import os
from typing import List, Dict, Any

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class RedisClient:
    """
    Simple Redis client for storing/retrieving recent conversation history by session_id.
    Falls back to in-memory storage if Redis is unavailable.
    """
    def __init__(self, url: str, max_turns: int = 10):
        self.url = url
        self.max_turns = max_turns
        self.memory: Dict[str, List[Dict[str, Any]]] = {}  # fallback in-memory
        if REDIS_AVAILABLE:
            self.client = redis.from_url(url, decode_responses=True)
        else:
            self.client = None

    async def save_session(self, session_id: str, turn: dict):
        """Append a conversation turn to the session history."""
        if self.client:
            # Use Redis list to store recent turns
            await self.client.rpush(session_id, str(turn))
            await self.client.ltrim(session_id, -self.max_turns, -1)
        else:
            # In-memory fallback
            if session_id not in self.memory:
                self.memory[session_id] = []
            self.memory[session_id].append(turn)
            self.memory[session_id] = self.memory[session_id][-self.max_turns:]

    async def get_session(self, session_id: str) -> List[dict]:
        """Retrieve recent conversation turns for a session."""
        if self.client:
            turns = await self.client.lrange(session_id, 0, -1)
            # Optionally: parse from str to dict if needed
            import ast
            return [ast.literal_eval(t) for t in turns]
        else:
            return self.memory.get(session_id, [])

    async def is_cooldown_active(self, key: str) -> bool:
        """Check if a cooldown key exists in Redis."""
        if self.client:
            return await self.client.exists(key) > 0
        return key in self.memory

    async def set_cooldown(self, key: str, ttl_seconds: int = 300):
        """Set a cooldown key with TTL in Redis."""
        if self.client:
            await self.client.set(key, "1", ex=ttl_seconds)
        else:
            self.memory[key] = True
