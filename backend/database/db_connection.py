from pymongo import MongoClient
from config import settings
from typing import Optional

class Database:
    client: Optional[MongoClient] = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            try:
                cls.client = MongoClient(settings.MONGO_URI)
                cls.db = cls.client[settings.DATABASE_NAME]
                
                # Test connection
                cls.client.admin.command('ping')
                print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
                
                # Create indexes if they don't exist
                cls.db.users.create_index("email", unique=True)
                cls.db.users.create_index("created_at")
                
            except Exception as e:
                print(f"❌ MongoDB connection failed: {e}")
                print("⚠️  Falling back to in-memory database for testing")
                cls.db = {"users": []}  # Fallback
        return cls.db

    @classmethod
    def disconnect(cls):
        if cls.client:
            cls.client.close()
            cls.client = None
            print("✅ MongoDB disconnected")
        else:
            print("✅ In-memory database disconnected")

def get_db():
    return Database.connect()