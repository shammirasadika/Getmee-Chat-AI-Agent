# PostgreSQL integration (Neon/cloud-ready)
import asyncpg
from datetime import datetime, timezone

class PostgresClient:
    """
    PostgreSQL client supporting Neon/cloud connection strings.
    """
    def __init__(self, url: str):
        self.url = url
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.url)

    async def ensure_tables(self):
        """Create tables if they don't exist."""
        await self.connect()
        async with self.pool.acquire() as conn:
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

    async def save_feedback(self, feedback_data: dict):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO feedback (session_id, message_id, feedback, comment)
                VALUES ($1, $2, $3, $4)
                """,
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
                """
                INSERT INTO support_requests
                    (session_id, user_message, user_email, fallback_message, language, status, email_sent, chat_summary)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                data.get("session_id"),
                data.get("user_message"),
                data.get("user_email"),
                data.get("fallback_message"),
                data.get("language", "en"),
                data.get("status", "pending"),
                data.get("email_sent", False),
                data.get("chat_summary"),
            )
            return row["id"]

    async def update_support_request_email(self, request_id: int, email_sent: bool):
        """Update the email_sent flag on a support request."""
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE support_requests SET email_sent = $1 WHERE id = $2",
                email_sent,
                request_id,
            )

    async def get_support_requests(self, status: str = None, limit: int = 50):
        """Retrieve support requests, optionally filtered by status."""
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
