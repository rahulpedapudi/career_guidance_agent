"""
MongoDB Database Connection.

Uses Motor (async driver) to manage database connections.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "career_guidance"

class Database:
    client: AsyncIOMotorClient = None
    db = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB."""
        if not MONGO_URI:
            print("⚠️ Database: MONGO_URI not found. Persistence disabled.")
            return

        try:
            cls.client = AsyncIOMotorClient(MONGO_URI)
            cls.db = cls.client[DB_NAME]
            # Verify connection
            await cls.client.admin.command('ping')
            print("✨ Database: Connected to MongoDB")
        except Exception as e:
            print(f"❌ Database: Connection failed: {e}")
            cls.client = None
            cls.db = None

    @classmethod
    async def close(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            print("✨ Database: Connection closed")
            
    @classmethod
    def get_collection(cls, name: str):
        """Get a collection if connected."""
        if cls.db is not None:
            return cls.db[name]
        return None

# Singleton instance access
db = Database
