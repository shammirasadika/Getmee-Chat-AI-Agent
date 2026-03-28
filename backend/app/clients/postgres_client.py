# PostgreSQL integration (Neon/cloud-ready)
import asyncpg
import uuid
from datetime import datetime, timezone
from typing import Optional


class PostgresClient:
    """
    PostgreSQL client supporting Neon/cloud connection strings.
    Handles both legacy tables AND the new chat data layer.
    """

    def __init__(self, url: str):
        self.url = url
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.url)

    # ──────────────────────────────────────────────
    # Table creation  (startup)
    # ──────────────────────────────────────────────

    async def ensure_tables(self):
        """Create all tables if they don't exist (legacy + new schema)."""
        await self.connect()
        async with self.pool.acquire() as conn:
            # --- Legacy tables (kept for backwards-compat) ---
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS support_requests (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    user_message TEXT NOT NULL,
                    user_email VARCHAR(255),
                    fallback_message TEXT,
                    language VARCHAR(10) NOT NULL DEFAULT 'en',
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    email_sent BOOLEAN NOT NULL DEFAULT FALSE,
                    chat_summary TEXT,
                    source VARCHAR(32), -- 'rag_fallback' or 'user_unsatisfied'
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255),
                    message_id VARCHAR(255),
                    feedback VARCHAR(50),
                    comment TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)

            # --- New schema tables ---
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_key     VARCHAR     UNIQUE NOT NULL,
                    user_email      VARCHAR     NULL,
                    preferred_language VARCHAR  NULL,
                    status          VARCHAR     NOT NULL DEFAULT 'active',
                    started_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ended_at        TIMESTAMP   NULL,
                    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id      UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    message_type    VARCHAR     NOT NULL,
                    message_text    TEXT        NOT NULL,
                    language        VARCHAR     NULL,
                    fallback_used   BOOLEAN     NOT NULL DEFAULT FALSE,
                    source_type     VARCHAR     NULL,
                    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS message_feedback (
                    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
                    message_id      UUID        NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
                    session_id      UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    feedback        VARCHAR     NOT NULL,
                    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id      UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    message_id      UUID        NULL REFERENCES chat_messages(id) ON DELETE SET NULL,
                    user_email      VARCHAR     NULL,
                    issue_summary   TEXT        NOT NULL,
                    status          VARCHAR     NOT NULL DEFAULT 'open',
                    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS session_feedback (
                    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id      UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    rating          INT         NOT NULL CHECK (rating BETWEEN 1 AND 5),
                    comment         TEXT        NULL,
                    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    # ──────────────────────────────────────────────
    # chat_sessions
    # ──────────────────────────────────────────────

    async def get_or_create_session(self, session_key: str, language: Optional[str] = None) -> dict:
        """Return existing session row or create a new one. Returns dict with 'id', 'session_key', etc."""
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM chat_sessions WHERE session_key = $1", session_key
            )
            if row:
                return dict(row)
            row = await conn.fetchrow(
                """INSERT INTO chat_sessions (session_key, preferred_language)
                   VALUES ($1, $2) RETURNING *""",
                session_key, language,
            )
            return dict(row)

    async def update_session_status(self, session_id, status: str, ended_at=None):
        """Update status (and optionally ended_at) on a chat session."""
        await self.connect()
        async with self.pool.acquire() as conn:
            if ended_at:
                await conn.execute(
                    "UPDATE chat_sessions SET status=$1, ended_at=$2 WHERE id=$3",
                    status, ended_at, session_id,
                )
            else:
                await conn.execute(
                    "UPDATE chat_sessions SET status=$1 WHERE id=$2",
                    status, session_id,
                )

    async def update_session_email(self, session_id, email: str):
        """Set user_email on a chat session."""
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE chat_sessions SET user_email=$1 WHERE id=$2",
                email, session_id,
            )

    # ──────────────────────────────────────────────
    # chat_messages
    # ──────────────────────────────────────────────

    async def insert_message(self, session_id, message_type: str, message_text: str,
                             language: Optional[str] = None, fallback_used: bool = False,
                             source_type: Optional[str] = None) -> dict:
        """Insert a chat message and return the full row (including generated UUID)."""
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO chat_messages (session_id, message_type, message_text, language, fallback_used, source_type)
                   VALUES ($1, $2, $3, $4, $5, $6) RETURNING *""",
                session_id, message_type, message_text, language, fallback_used, source_type,
            )
            return dict(row)

    async def get_message_by_id(self, message_id) -> Optional[dict]:
        """Fetch a single message row by UUID."""
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM chat_messages WHERE id = $1", message_id)
            return dict(row) if row else None

    # ──────────────────────────────────────────────
    # message_feedback
    # ──────────────────────────────────────────────

    async def insert_message_feedback(self, message_id, session_id, feedback: str) -> dict:
        """Insert response-level feedback (satisfied / not_satisfied)."""
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO message_feedback (message_id, session_id, feedback)
                   VALUES ($1, $2, $3) RETURNING *""",
                message_id, session_id, feedback,
            )
            return dict(row)

    # ──────────────────────────────────────────────
    # support_tickets
    # ──────────────────────────────────────────────

    async def insert_support_ticket(self, session_id, issue_summary: str,
                                    message_id=None, user_email: Optional[str] = None) -> dict:
        """Create a support ticket and return the row."""
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO support_tickets (session_id, message_id, user_email, issue_summary)
                   VALUES ($1, $2, $3, $4) RETURNING *""",
                session_id, message_id, user_email, issue_summary,
            )
            return dict(row)

    async def update_ticket_status(self, ticket_id, status: str):
        """Update a support ticket status."""
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE support_tickets SET status=$1 WHERE id=$2", status, ticket_id,
            )

    async def get_support_tickets(self, status: Optional[str] = None, limit: int = 50) -> list:
        """Retrieve support tickets, optionally filtered by status."""
        await self.connect()
        async with self.pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    "SELECT * FROM support_tickets WHERE status=$1 ORDER BY created_at DESC LIMIT $2",
                    status, limit,
                )
            else:
                rows = await conn.fetch(
                    "SELECT * FROM support_tickets ORDER BY created_at DESC LIMIT $1", limit,
                )
            return [dict(r) for r in rows]

    # ──────────────────────────────────────────────
    # session_feedback  (end-of-chat rating)
    # ──────────────────────────────────────────────

    async def insert_session_feedback(self, session_id, rating: int, comment: Optional[str] = None) -> dict:
        """Insert a final session rating (1–5) with optional comment."""
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO session_feedback (session_id, rating, comment)
                   VALUES ($1, $2, $3) RETURNING *""",
                session_id, rating, comment,
            )
            return dict(row)

    # ──────────────────────────────────────────────
    # Legacy helpers  (kept for backwards-compat)
    # ──────────────────────────────────────────────

    async def save_feedback(self, feedback_data: dict):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO feedback (session_id, message_id, feedback, comment)
                   VALUES ($1, $2, $3, $4)""",
                feedback_data.get("session_id"),
                feedback_data.get("message_id"),
                feedback_data.get("feedback"),
                feedback_data.get("comment"),
            )

    async def save_support_request(self, data: dict) -> int:
        """Save a fallback/support request and return its ID."""
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO support_requests
                    (session_id, user_message, user_email, fallback_message, language, status, email_sent, chat_summary, source)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                   RETURNING id""",
                data.get("session_id"),
                data.get("user_message"),
                data.get("user_email"),
                data.get("fallback_message"),
                data.get("language", "en"),
                data.get("status", "pending"),
                data.get("email_sent", False),
                data.get("chat_summary"),
                data.get("source"),
            )
            return row["id"]

    async def update_support_request_email(self, request_id: int, email_sent: bool):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE support_requests SET email_sent = $1 WHERE id = $2",
                email_sent, request_id,
            )

    async def get_support_requests(self, status: str = None, limit: int = 50):
        await self.connect()
        async with self.pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    "SELECT * FROM support_requests WHERE status = $1 ORDER BY created_at DESC LIMIT $2",
                    status, limit,
                )
            else:
                rows = await conn.fetch(
                    "SELECT * FROM support_requests ORDER BY created_at DESC LIMIT $1",
                    limit,
                )
            return [dict(r) for r in rows]
