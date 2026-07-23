import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "Estora")


print(f"Connecting to: {MONGODB_URI}")
print(f"Database: {DB_NAME}")
print(f"Collection: properties")

# Check if database exists
client = MongoClient(MONGODB_URI)
print("Available databases:", client.list_database_names())
print("Available collections:", client[DB_NAME].list_collection_names())

def load_properties_to_db(json_file="properties.json"):
    """Load properties from JSON file into MongoDB"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db["properties"]
        
        # Read JSON file
        with open(json_file, 'r') as f:
            properties = json.load(f)
        
        # Clear existing properties
        collection.delete_many({})
        
        # Insert new properties
        if properties:
            collection.insert_many(properties)
            print(f"✅ Loaded {len(properties)} properties to MongoDB")
        
        return True
    except Exception as e:
        print(f"❌ Error loading properties: {e}")
        return False

# def get_properties_from_db():
#     """Fetch all properties from MongoDB"""
#     try:
#         client = MongoClient(MONGODB_URI)
#         db = client[DB_NAME]
        
#         properties = list(db.properties.find({}, {"_id": 0}))
#         return properties
#     except Exception as e:
#         print(f"❌ Error fetching properties: {e}")
#         return []

if __name__ == "__main__":
    load_properties_to_db()