from database.db_connection import Database

def test_mongodb():
    print("Testing MongoDB connection...")
    db = Database.connect()
    
    # Check if we're connected to real MongoDB
    if hasattr(db, 'users'):
        print("✅ Connected to real MongoDB")
        print(f"Database: {db.name}")
        print(f"Collections: {db.list_collection_names()}")
        
        # Test inserting a document
        test_doc = {
            "test": "MongoDB connection test",
            "timestamp": "just now"
        }
        result = db.test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up
        db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
    else:
        print("⚠️ Using in-memory fallback database")
        print("Make sure MongoDB is running on localhost:27017")
    
    Database.disconnect()

if __name__ == "__main__":
    test_mongodb()