from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os
from pprint import pprint

load_dotenv()

def test_mongo_connection():
    try:
        username = quote_plus(os.getenv("MONGO_USERNAME"))
        password = quote_plus(os.getenv("MONGO_PASSWORD"))
        
        print(f"Testing connection with username: {username}")
        print(f"Password length: {len(password) if password else 0}")
        
        uri = f"mongodb+srv://{username}:{password}@cluster0.frxzbp7.mongodb.net/?retryWrites=true&w=majority"
        
        print("Attempting to connect...")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Access database and collection
        db = client["sample_weatherdata"]
        collection = db["data"]
        
        # Count documents
        count = collection.count_documents({})
        print(f"✅ Found {count} documents in the collection")
        
        # Find and display first 3 documents (with _id removed for readability)
        print("\n📄 Sample documents from the collection:")
        for i, doc in enumerate(collection.find().limit(3)):
            print(f"\nDocument {i+1}:")
            doc.pop('_id', None)  # Remove _id for cleaner output
            pprint(doc, indent=2)
            
        # Show some statistics about the data
        print("\n📊 Collection statistics:")
        if count > 0:
            # Get sample field names
            sample_doc = collection.find_one()
            print(f"Sample fields: {list(sample_doc.keys())[:5]}...")  # Show first 5 fields
            
            # Count documents with position data
            with_position = collection.count_documents({"position": {"$exists": True}})
            print(f"Documents with position data: {with_position} ({with_position/count:.1%})")
            
            # Show date range if available
            if "ts" in sample_doc:
                first = collection.find_one(sort=[("ts", 1)])["ts"]
                last = collection.find_one(sort=[("ts", -1)])["ts"]
                print(f"Date range: {first} to {last}")
            
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Check if credentials are loaded
        if not os.getenv("MONGO_USERNAME"):
            print("⚠️  MONGO_USERNAME not found in environment")
        if not os.getenv("MONGO_PASSWORD"):
            print("⚠️  MONGO_PASSWORD not found in environment")

if __name__ == "__main__":
    test_mongo_connection()