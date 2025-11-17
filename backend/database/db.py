from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config

class Database:
    client = None
    db=None
    @staticmethod
    def initialize():
        """Initialize the MongoDB connection"""
        try:
            print("🔍 Initializing MongoDB connection...")
            Database.client = MongoClient(Config.MONGO_URI)
            Database.client.admin.command('ping')  # Test connection
            Database.db = Database.client[Config.DATABASE_NAME]
            print("   ✅ MongoDB connection established!")
            print(f"   📊 Using database: {Config.DATABASE_NAME}")
            print(f"   📄 Using collection: {Config.COLLECTION_NAME}")
        except ConnectionFailure as e:
            print("   ❌ Could not connect to MongoDB:", e)
            raise e
        except Exception as e:
            print("   ❌ An error occurred while connecting to MongoDB:", e)
            raise e    
    @staticmethod
    def get_collection(collection_name):
        """Get a specific collection from the database"""
        if Database.db is None:
            raise Exception("Database not initialized. Call Database.initialize() first!")
        
        return Database.db[collection_name]
    
    @staticmethod
    def close():
        """close the datbase connection"""
        if Database.client:
            Database.client.close()
            print("🔌 MongoDB connection closed")