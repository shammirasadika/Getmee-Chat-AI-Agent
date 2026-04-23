from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class MongoClientAdapter:
    def __init__(self, uri: str, database: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database]

    async def update_support_request_email(self, request_id: str, email_sent: bool):
        """
        Update the email_sent field for a support request document by its _id.
        """
        from bson import ObjectId
        collection = self.db["support_requests"]
        await collection.update_one({"_id": ObjectId(request_id)}, {"$set": {"email_sent": email_sent}})
        # ...existing code...

    async def save_support_request(self, data: dict) -> str:
        """
        Save a fallback/support request and return its inserted ID (as string).
        """
        collection = self.db["support_requests"]
        result = await collection.insert_one(data)
        # ...existing code...
        return str(result.inserted_id)

    async def get_or_create_session(self, session_key: str, language: str = None) -> dict:
        """
        Get a chat session by session_key, or create it if it doesn't exist.
        Returns the session document as a dict (with 'id' as string).
        """
        collection = self.db["chat_sessions"]
        session = await collection.find_one({"session_key": session_key})
        if session:
            session["id"] = str(session["_id"])
            return session
        doc = {
            "session_key": session_key,
            "preferred_language": language,
            "status": "active",
        }
        result = await collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        # ...existing code...
        return doc
    def __init__(self, uri: str, database: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database]

    async def insert_message(self, session_id, message_type: str, message_text: str,
                             language: Optional[str] = None, fallback_used: bool = False,
                             source_type: Optional[str] = None) -> dict:
        collection = self.db["chat_messages"]
        doc = {
            "session_id": session_id,
            "message_type": message_type,
            "message_text": message_text,
            "language": language,
            "fallback_used": fallback_used,
            "source_type": source_type,
        }
        result = await collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        # ...existing code...
        return doc

    async def get_message_by_id(self, message_id) -> Optional[dict]:
        collection = self.db["chat_messages"]
        from bson import ObjectId
        doc = await collection.find_one({"_id": ObjectId(message_id)})
        if doc:
            doc["id"] = str(doc["_id"])
            return doc
        return None

    async def insert_message_feedback(self, message_id, session_id, feedback: str) -> dict:
        collection = self.db["message_feedback"]
        doc = {
            "message_id": message_id,
            "session_id": session_id,
            "feedback": feedback,
        }
        result = await collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        # ...existing code...
        return doc

    async def insert_session_feedback(self, session_id, rating: int, comment: Optional[str] = None) -> dict:
        collection = self.db["session_feedback"]
        doc = {
            "session_id": session_id,
            "rating": rating,
            "comment": comment,
        }
        result = await collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        # ...existing code...
        return doc

    async def update_ticket_status(self, ticket_id, status: str):
        collection = self.db["support_tickets"]
        from bson import ObjectId
        await collection.update_one({"_id": ObjectId(ticket_id)}, {"$set": {"status": status}})
        # Only update ticket status; removed undefined session_key/language logic
        return None

    async def update_session_status(self, session_id, status: str, ended_at=None):
        collection = self.db["chat_sessions"]
        update = {"status": status}
        if ended_at:
            update["ended_at"] = ended_at
        await collection.update_one({"_id": session_id}, {"$set": update})

    async def update_session_email(self, session_id, email: str):
        collection = self.db["chat_sessions"]
        await collection.update_one({"_id": session_id}, {"$set": {"user_email": email}})

    async def insert_support_ticket(self, session_id, issue_summary: str, message_id=None, user_email: Optional[str] = None) -> dict:
        collection = self.db["support_tickets"]
        doc = {
            "session_id": session_id,
            "issue_summary": issue_summary,
            "message_id": message_id,
            "user_email": user_email,
            "status": "open",
        }
        result = await collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        # ...existing code...
        return doc

    async def get_support_tickets(self, status: Optional[str] = None, limit: int = 50) -> list:
        collection = self.db["support_tickets"]
        query = {"status": status} if status else {}
        cursor = collection.find(query).sort("_id", -1).limit(limit)
        tickets = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            tickets.append(doc)
        return tickets
