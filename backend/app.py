from flask import Flask, jsonify
from flask_cors import CORS
from database.db import Database
from routes.posts import posts_bp
from config import Config

# Create Flask application
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows your Streamlit frontend to communicate with this backend
CORS(app)

# Load configuration
app.config.from_object(Config)


# ============================================================
# Initialize Database Connection
# ============================================================
try:
    Database.initialize()
except Exception as e:
    print(f"Failed to initialize database: {e}")
    exit(1)


# ============================================================
# Register Blueprints (Route Modules)
# ============================================================
app.register_blueprint(posts_bp)


# ============================================================
# Root Endpoint - Health Check
# ============================================================
@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Confirms the API is running
    
    Returns:
        200: API status information
    """
    return jsonify({
        "status": "success",
        "message": "Blog API is running!",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /",
            "create_post": "POST /posts",
            "get_all_posts": "GET /posts",
            "search_posts": "GET /posts?term=search_term",
            "get_post": "GET /posts/:id",
            "update_post": "PUT /posts/:id",
            "delete_post": "DELETE /posts/:id"
        }
    }), 200


# ============================================================
# Error Handlers
# ============================================================
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested URL was not found on this server"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors (wrong HTTP method)"""
    return jsonify({
        "error": "Method not allowed",
        "message": "The method is not allowed for the requested URL"
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


# ============================================================
# Run the Application
# ============================================================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Starting Blog API Server")
    print("=" * 60)
    print(f"📍 Running on: http://{Config.HOST}:{Config.PORT}")
    print(f"🔧 Debug mode: {Config.DEBUG}")
    print(f"📁 Database: {Config.DATABASE_NAME}")
    print(f"📄 Collection: {Config.COLLECTION_NAME}")
    print("=" * 60)
    print("\n💡 Press CTRL+C to stop the server\n")
    
    # Run Flask app
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )