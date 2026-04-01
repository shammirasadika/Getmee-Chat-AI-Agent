"""
Redis Session Service — temporary session & UI state management.

Keys managed (all prefixed with session:{session_key}:):
  :context           — current session metadata and runtime state
  :messages           — recent message history for chatbot context (list)
  :feedback_state     — response-level feedback tracking for latest bot answer
  :support_state      — escalation flow state after negative feedback
  :endchat_state      — end-of-chat / session-feedback tracking

All keys use TTL so stale sessions auto-expire.
"""

import json
from typing import Optional, List, Dict, Any

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Session TTL for chatbot sessions (default: 30 minutes / 1800 seconds)
# NOTE: This value may be adjusted later based on client confirmation.
import os
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1800"))  # 30 minutes
DEFAULT_TTL = SESSION_TTL_SECONDS
# Max recent messages kept in the messages list
MAX_RECENT_MESSAGES = 20


class RedisSessionService:
    """Structured Redis helpers for live chat session state."""

    def __init__(self, url: str, ttl: int = DEFAULT_TTL):
        self.url = url
        # Always use centralized TTL config
        self.ttl = SESSION_TTL_SECONDS
        self.memory: Dict[str, Any] = {}  # in-memory fallback
        if REDIS_AVAILABLE:
            self.client = aioredis.from_url(url, decode_responses=True)
        else:
            self.client = None

    # Helper: refresh TTL for all session keys (context, messages, feedback, etc.)
    async def refresh_session_ttl(self, session_key: str):
        """Refresh TTL for all session keys for this session (called on user activity)."""
        suffixes = ["context", "messages", "feedback_state", "support_state", "endchat_state"]
        for suffix in suffixes:
            key = self._key(session_key, suffix)
            if self.client:
                await self.client.expire(key, self.ttl)
            # in-memory fallback: no TTL support

    # ── internal helpers ──────────────────────────

    def _key(self, session_key: str, suffix: str) -> str:
        return f"session:{session_key}:{suffix}"

    async def _set_json(self, key: str, data: dict):
        """Store a JSON blob in Redis (or in-memory fallback)."""
        payload = json.dumps(data)
        if self.client:
            await self.client.set(key, payload, ex=self.ttl)
        else:
            self.memory[key] = payload

    async def _get_json(self, key: str) -> Optional[dict]:
        """Retrieve a JSON blob from Redis (or in-memory fallback)."""
        if self.client:
            raw = await self.client.get(key)
        else:
            raw = self.memory.get(key)
        if raw:
            return json.loads(raw)
        return None

    async def _delete(self, key: str):
        if self.client:
            await self.client.delete(key)
        else:
            self.memory.pop(key, None)

    # ──────────────────────────────────────────────
    # 1. session:{session_key}:context
    #    Current session metadata & runtime state
    # ──────────────────────────────────────────────

    def _default_context(self, session_id: str) -> dict:
        return {
            "session_id": session_id,
            "user_email": None,
            "preferred_language": "en",
            "active": True,
            "last_intent": None,
            "waiting_for_feedback": False,
            "waiting_for_support_confirmation": False,
            "session_feedback_pending": False,
            "chat_status": "active",
        }

    async def get_context(self, session_key: str) -> Optional[dict]:
        """Get current session context."""
        return await self._get_json(self._key(session_key, "context"))

    async def set_context(self, session_key: str, data: dict):
        """Overwrite session context."""
        await self._set_json(self._key(session_key, "context"), data)

    async def init_context(self, session_key: str, session_id: str, language: str = "en"):
        """Initialize context for a brand-new session."""
        ctx = self._default_context(session_id)
        ctx["preferred_language"] = language
        await self.set_context(session_key, ctx)
        return ctx

    async def update_context(self, session_key: str, **fields):
        """Merge partial updates into existing context."""
        ctx = await self.get_context(session_key)
        if ctx is None:
            return None
        ctx.update(fields)
        await self.set_context(session_key, ctx)
        return ctx

    # ──────────────────────────────────────────────
    # 2. session:{session_key}:messages
    #    Recent message history for chatbot context
    # ──────────────────────────────────────────────

    async def push_message(self, session_key: str, message: dict):
        """Append a message to the recent-messages list and trim to max. Refresh session TTL on activity."""
        key = self._key(session_key, "messages")
        payload = json.dumps(message)
        if self.client:
            await self.client.rpush(key, payload)
            await self.client.ltrim(key, -MAX_RECENT_MESSAGES, -1)
            # Refresh TTL for all session keys on user activity
            await self.refresh_session_ttl(session_key)
        else:
            lst = self.memory.setdefault(key, [])
            lst.append(payload)
            self.memory[key] = lst

    async def get_messages(self, session_key: str) -> List[dict]:
        """Return recent messages for context window."""
        key = self._key(session_key, "messages")
        if self.client:
            raw = await self.client.lrange(key, 0, -1)
            return [json.loads(r) for r in raw]
        else:
            return [json.loads(r) for r in self.memory.get(key, [])]

    # ──────────────────────────────────────────────
    # 3. session:{session_key}:feedback_state
    #    Response-level feedback tracking
    # ──────────────────────────────────────────────

    async def set_feedback_state(self, session_key: str, last_bot_message_id: str,
                                  feedback_required: bool = True,
                                  feedback_submitted: bool = False):
        """Set feedback state after a bot answer is generated."""
        await self._set_json(self._key(session_key, "feedback_state"), {
            "last_bot_message_id": last_bot_message_id,
            "feedback_required": feedback_required,
            "feedback_submitted": feedback_submitted,
        })

    async def get_feedback_state(self, session_key: str) -> Optional[dict]:
        return await self._get_json(self._key(session_key, "feedback_state"))

    async def mark_feedback_submitted(self, session_key: str):
        """Mark response-level feedback as submitted."""
        state = await self.get_feedback_state(session_key)
        if state:
            state["feedback_submitted"] = True
            state["feedback_required"] = False
            await self._set_json(self._key(session_key, "feedback_state"), state)

    # ──────────────────────────────────────────────
    # 4. session:{session_key}:support_state
    #    Escalation flow tracking after negative feedback
    # ──────────────────────────────────────────────

    async def set_support_state(self, session_key: str,
                                 not_satisfied_selected: bool = False,
                                 support_confirmation_pending: bool = False,
                                 selected_message_id: Optional[str] = None):
        await self._set_json(self._key(session_key, "support_state"), {
            "not_satisfied_selected": not_satisfied_selected,
            "support_confirmation_pending": support_confirmation_pending,
            "selected_message_id": selected_message_id,
        })

    async def get_support_state(self, session_key: str) -> Optional[dict]:
        return await self._get_json(self._key(session_key, "support_state"))

    async def clear_support_state(self, session_key: str):
        await self._delete(self._key(session_key, "support_state"))

    # ──────────────────────────────────────────────
    # 5. session:{session_key}:endchat_state
    #    End-of-chat / session-feedback tracking
    # ──────────────────────────────────────────────

    async def set_endchat_state(self, session_key: str,
                                 chat_ended: bool = False,
                                 session_feedback_pending: bool = False):
        await self._set_json(self._key(session_key, "endchat_state"), {
            "chat_ended": chat_ended,
            "session_feedback_pending": session_feedback_pending,
        })

    async def get_endchat_state(self, session_key: str) -> Optional[dict]:
        return await self._get_json(self._key(session_key, "endchat_state"))

    # ──────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────

    async def expire_session(self, session_key: str, ttl: int = 300):
        """Set a short TTL on all session keys so they auto-expire after chat ends."""
        suffixes = ["context", "messages", "feedback_state", "support_state", "endchat_state"]
        for suffix in suffixes:
            key = self._key(session_key, suffix)
            if self.client:
                await self.client.expire(key, ttl)
            # in-memory fallback simply deletes (no TTL support)

    async def clear_session(self, session_key: str):
        """Immediately remove all Redis keys for a session."""
        suffixes = ["context", "messages", "feedback_state", "support_state", "endchat_state"]
        for suffix in suffixes:
            await self._delete(self._key(session_key, suffix))
