from datetime import datetime
from bson import ObjectId

class Post:
    """
    Blog Post Model
    Defines the structure and operations for blog posts
    """
    
    @staticmethod
    def create_post(title, content, category, tags):
        """
        Create a new post document
        
        Args:
            title (str): Post title
            content (str): Post content
            category (str): Post category
            tags (list): List of tags
            
        Returns:
            dict: Post document ready for MongoDB
        """
        return {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    
    @staticmethod
    def update_post(title, content, category, tags):
        """
        Create an update document for existing post
        
        Args:
            title (str): Updated title
            content (str): Updated content
            category (str): Updated category
            tags (list): Updated tags
            
        Returns:
            dict: Update document
        """
        return {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "updatedAt": datetime.utcnow()
        }
    
    @staticmethod
    def serialize_post(post):
        """
        Convert MongoDB document to JSON-friendly format
        MongoDB uses ObjectId and datetime which aren't JSON serializable
        
        Args:
            post (dict): MongoDB document
            
        Returns:
            dict: JSON-serializable post object
        """
        if post is None:
            return None
        
        return {
            "id": str(post["_id"]),  # Convert ObjectId to string
            "title": post["title"],
            "content": post["content"],
            "category": post["category"],
            "tags": post["tags"],
            "createdAt": post["createdAt"].isoformat() + "Z",  # ISO 8601 format
            "updatedAt": post["updatedAt"].isoformat() + "Z"
        }