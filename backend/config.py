import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # MongoDB connection string
    MONGO_URI = os.getenv('MONGO_URI')
    
    # Database name
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'blog_db')
    
    # Collection name - using blog_db as you created
    COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'blog_db')
    
    # Flask settings
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    # For production, set DEBUG = False