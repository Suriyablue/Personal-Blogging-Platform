from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from database.db import Database
from models.post import Post
from utils.validators import validate_post_data
from config import Config

# Create Blueprint
# Blueprint is like a module for organizing routes
posts_bp = Blueprint('posts', __name__)


def get_posts_collection():
    """
    Helper function to get the posts collection
    
    Returns:
        Collection: MongoDB posts collection
    """
    return Database.get_collection(Config.COLLECTION_NAME)


# ============================================================
# CREATE - POST /posts
# ============================================================
@posts_bp.route('/posts', methods=['POST'])
def create_post():
    """
    Create a new blog post
    
    Request Body:
        {
            "title": "My Post",
            "content": "Post content",
            "category": "Technology",
            "tags": ["tech", "coding"]
        }
    
    Returns:
        201: Post created successfully
        400: Validation error
        500: Server error
    """
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        # Validate the data
        errors = validate_post_data(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        # Create post document using the Post model
        post_data = Post.create_post(
            title=data['title'],
            content=data['content'],
            category=data['category'],
            tags=data['tags']
        )
        
        # Insert into MongoDB
        collection = get_posts_collection()
        result = collection.insert_one(post_data)
        
        # Get the created post with the generated _id
        created_post = collection.find_one({"_id": result.inserted_id})
        
        # Serialize and return
        return jsonify(Post.serialize_post(created_post)), 201
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ============================================================
# READ - GET /posts/:id
# ============================================================
@posts_bp.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """
    Get a single blog post by ID
    
    Args:
        post_id (str): MongoDB ObjectId as string
    
    Returns:
        200: Post found
        400: Invalid ID format
        404: Post not found
        500: Server error
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(post_id):
            return jsonify({"error": "Invalid post ID format"}), 400
        
        # Find post in database
        collection = get_posts_collection()
        post = collection.find_one({"_id": ObjectId(post_id)})
        
        # Check if post exists
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Return serialized post
        return jsonify(Post.serialize_post(post)), 200
        
    except InvalidId:
        return jsonify({"error": "Invalid post ID format"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ============================================================
# READ - GET /posts (with optional search)
# ============================================================
@posts_bp.route('/posts', methods=['GET'])
def get_all_posts():
    """
    Get all blog posts with optional search
    
    Query Parameters:
        term (optional): Search term for filtering posts
        
    Example:
        GET /posts
        GET /posts?term=technology
    
    Returns:
        200: List of posts (can be empty array)
        500: Server error
    """
    try:
        collection = get_posts_collection()
        
        # Get search term from query parameters
        search_term = request.args.get('term', '').strip()
        
        # Build MongoDB query
        if search_term:
            # Case-insensitive regex search in title, content, and category
            # $regex is like SQL LIKE '%term%'
            # $options: "i" means case-insensitive
            query = {
                "$or": [
                    {"title": {"$regex": search_term, "$options": "i"}},
                    {"content": {"$regex": search_term, "$options": "i"}},
                    {"category": {"$regex": search_term, "$options": "i"}}
                ]
            }
        else:
            # No search term, get all posts
            query = {}
        
        # Find posts and sort by creation date (newest first)
        # -1 means descending order
        posts_cursor = collection.find(query).sort("createdAt", -1)
        
        # Convert cursor to list and serialize each post
        posts = [Post.serialize_post(post) for post in posts_cursor]
        
        return jsonify(posts), 200
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ============================================================
# UPDATE - PUT /posts/:id
# ============================================================
@posts_bp.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update an existing blog post
    
    Args:
        post_id (str): MongoDB ObjectId as string
    
    Request Body:
        {
            "title": "Updated Title",
            "content": "Updated content",
            "category": "Updated category",
            "tags": ["tag1", "tag2"]
        }
    
    Returns:
        200: Post updated successfully
        400: Validation error or invalid ID
        404: Post not found
        500: Server error
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(post_id):
            return jsonify({"error": "Invalid post ID format"}), 400
        
        # Get JSON data from request
        data = request.get_json()
        
        # Validate data
        errors = validate_post_data(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        # Create update document
        update_data = Post.update_post(
            title=data['title'],
            content=data['content'],
            category=data['category'],
            tags=data['tags']
        )
        
        # Update in database
        collection = get_posts_collection()
        result = collection.update_one(
            {"_id": ObjectId(post_id)},  # Filter: find post by ID
            {"$set": update_data}         # Update: set new values
        )
        
        # Check if post was found
        if result.matched_count == 0:
            return jsonify({"error": "Post not found"}), 404
        
        # Get the updated post
        updated_post = collection.find_one({"_id": ObjectId(post_id)})
        
        return jsonify(Post.serialize_post(updated_post)), 200
        
    except InvalidId:
        return jsonify({"error": "Invalid post ID format"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ============================================================
# DELETE - DELETE /posts/:id
# ============================================================
@posts_bp.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a blog post
    
    Args:
        post_id (str): MongoDB ObjectId as string
    
    Returns:
        204: Post deleted successfully (no content)
        400: Invalid ID format
        404: Post not found
        500: Server error
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(post_id):
            return jsonify({"error": "Invalid post ID format"}), 400
        
        # Delete from database
        collection = get_posts_collection()
        result = collection.delete_one({"_id": ObjectId(post_id)})
        
        # Check if post was found and deleted
        if result.deleted_count == 0:
            return jsonify({"error": "Post not found"}), 404
        
        # Return 204 No Content (successful deletion)
        return '', 204
        
    except InvalidId:
        return jsonify({"error": "Invalid post ID format"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500