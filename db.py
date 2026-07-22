# db.py
import os
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Get MongoDB URI from environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "estora")

# Global client connection
client = None
db = None

def get_db():
    """Get MongoDB database connection"""
    global client, db
    if client is None:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
    return db

def init_database():
    """Initialize MongoDB collections and indexes"""
    try:
        db = get_db()
        
        # Create collection if it doesn't exist (MongoDB creates on first write)
        # But we can create indexes for better performance
        
        # Create index on user_id and created_at for faster queries
        db.chat_history.create_index([("user_id", 1), ("created_at", -1)])
        db.chat_history.create_index("user_id")
        
        print("✅ MongoDB initialized successfully")
        return True
    except Exception as e:
        print(f"❌ MongoDB initialization error: {e}")
        return False

def save_chat_message(user_id: str, user_message: str, bot_response: str) -> bool:
    """Save a chat message to MongoDB"""
    try:
        db = get_db()
        chat_doc = {
            "user_id": user_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "created_at": datetime.utcnow()
        }
        db.chat_history.insert_one(chat_doc)
        return True
    except Exception as e:
        print(f"❌ Error saving chat: {e}")
        return False

def fetch_chat_history(user_id: str, limit: int = 10) -> List[Dict]:
    """Fetch recent chat history for a user"""
    try:
        db = get_db()
        
        # Find messages for this user, sort by newest first
        cursor = db.chat_history.find(
            {"user_id": user_id},
            {"_id": 0, "user_message": 1, "bot_response": 1, "created_at": 1}
        ).sort("created_at", -1).limit(limit)
        
        # Convert cursor to list
        history = []
        for doc in cursor:
            history.append({
                "user_message": doc["user_message"],
                "bot_response": doc["bot_response"],
                "created_at": doc["created_at"].isoformat() if doc.get("created_at") else None
            })
        
        return history
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        return []