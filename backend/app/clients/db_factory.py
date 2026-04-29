from app.clients.postgres_client import PostgresClient
from app.clients.mongo_client import MongoClientAdapter
from app.core.config import settings

def get_db_client():
    if getattr(settings, "PRIMARY_DB", "postgresql") == "postgresql":
        return PostgresClient(settings.POSTGRES_URL)
    elif getattr(settings, "PRIMARY_DB", "postgresql") == "mongodb":
        return MongoClientAdapter(settings.MONGODB_URI, settings.MONGODB_DATABASE)
    else:
        raise ValueError(f"Unsupported PRIMARY_DB: {getattr(settings, 'PRIMARY_DB', None)}")
