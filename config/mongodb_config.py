import os
from pymongo import MongoClient
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables if not already loaded
load_dotenv()

# MongoDB connection string
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# MongoDB client instance
try:
    client = MongoClient(MONGODB_URI)
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    client = None

def get_database():
    """Get MongoDB database instance"""
    return client[DATABASE_NAME]

# Database collections
def media_collection():
    """Get media collection"""
    db = get_database()
    return db["media"]