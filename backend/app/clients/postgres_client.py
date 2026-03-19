# PostgreSQL integration (Neon/cloud-ready)
import asyncpg

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
