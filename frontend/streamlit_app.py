import streamlit as st
import requests
import json
from datetime import datetime

# ============================================================
# Configuration
# ============================================================
API_BASE_URL = "http://localhost:5000"

# Page configuration
st.set_page_config(
    page_title="Personal Blog Platform",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Custom CSS for better styling
# ============================================================
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .post-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    .post-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .post-meta {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    .tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        background-color: #3498db;
        color: white;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================
# API Helper Functions
# ============================================================

def get_all_posts(search_term=""):
    """Get all posts from API with optional search"""
    try:
        url = f"{API_BASE_URL}/posts"
        if search_term:
            url += f"?term={search_term}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching posts: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []


def get_post_by_id(post_id):
    """Get a single post by ID"""
    try:
        response = requests.get(f"{API_BASE_URL}/posts/{post_id}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error("Post not found")
            return None
        else:
            st.error(f"Error fetching post: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None


def create_post(title, content, category, tags):
    """Create a new post"""
    try:
        data = {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags
        }
        response = requests.post(f"{API_BASE_URL}/posts", json=data)
        if response.status_code == 201:
            return True, response.json()
        elif response.status_code == 400:
            errors = response.json().get('errors', ['Validation error'])
            return False, errors
        else:
            return False, [f"Error: {response.status_code}"]
    except Exception as e:
        return False, [f"Error connecting to API: {str(e)}"]


def update_post(post_id, title, content, category, tags):
    """Update an existing post"""
    try:
        data = {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags
        }
        response = requests.put(f"{API_BASE_URL}/posts/{post_id}", json=data)
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 400:
            errors = response.json().get('errors', ['Validation error'])
            return False, errors
        elif response.status_code == 404:
            return False, ["Post not found"]
        else:
            return False, [f"Error: {response.status_code}"]
    except Exception as e:
        return False, [f"Error connecting to API: {str(e)}"]


def delete_post(post_id):
    """Delete a post"""
    try:
        response = requests.delete(f"{API_BASE_URL}/posts/{post_id}")
        if response.status_code == 204:
            return True, "Post deleted successfully"
        elif response.status_code == 404:
            return False, "Post not found"
        else:
            return False, f"Error: {response.status_code}"
    except Exception as e:
        return False, f"Error connecting to API: {str(e)}"


# ============================================================
# UI Helper Functions
# ============================================================

def format_datetime(iso_string):
    """Format ISO datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return iso_string


def display_post_card(post, show_full_content=False):
    """Display a post in a card format"""
    with st.container():
        st.markdown(f"""
            <div class="post-card">
                <div class="post-title">{post['title']}</div>
                <div class="post-meta">
                    📁 {post['category']} | 
                    📅 {format_datetime(post['createdAt'])}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Tags
        st.markdown("**Tags:** " + " ".join([f"`{tag}`" for tag in post['tags']]))
        
        # Content
        if show_full_content:
            st.markdown("**Content:**")
            st.write(post['content'])
        else:
            # Show preview (first 200 characters)
            preview = post['content'][:200] + "..." if len(post['content']) > 200 else post['content']
            st.write(preview)
        
        st.markdown("---")


# ============================================================
# Page: Home / View All Posts
# ============================================================

def page_home():
    """Home page showing all posts"""
    st.markdown('<h1 class="main-header">📝 Personal Blog Platform</h1>', unsafe_allow_html=True)
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search posts", placeholder="Search by title, content, or category...")
    with col2:
        search_button = st.button("Search", use_container_width=True)
    
    # Get posts
    if search_term or search_button:
        posts = get_all_posts(search_term)
        if search_term:
            st.info(f"Showing results for: **{search_term}**")
    else:
        posts = get_all_posts()
    
    # Display posts
    if not posts:
        st.info("📭 No posts found. Create your first post using the sidebar!")
    else:
        st.success(f"📚 Found {len(posts)} post(s)")
        
        for post in posts:
            col1, col2, col3 = st.columns([6, 1, 1])
            
            with col1:
                display_post_card(post, show_full_content=False)
            
            with col2:
                if st.button("👁️ View", key=f"view_{post['id']}"):
                    st.session_state.page = "view_post"
                    st.session_state.selected_post_id = post['id']
                    st.rerun()
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_{post['id']}"):
                    st.session_state.page = "edit_post"
                    st.session_state.selected_post_id = post['id']
                    st.rerun()


# ============================================================
# Page: Create New Post
# ============================================================

def page_create_post():
    """Create new post page"""
    st.markdown('<h1 class="main-header">✍️ Create New Post</h1>', unsafe_allow_html=True)
    
    with st.form("create_post_form"):
        title = st.text_input("Title *", placeholder="Enter post title...")
        
        category = st.selectbox(
            "Category *",
            ["Technology", "Travel", "Food", "Lifestyle", "Education", "Health", "Business", "Other"]
        )
        
        content = st.text_area(
            "Content *",
            placeholder="Write your post content here...",
            height=300
        )
        
        tags_input = st.text_input(
            "Tags * (comma-separated)",
            placeholder="e.g., python, coding, tutorial"
        )
        
        submitted = st.form_submit_button("📤 Publish Post", use_container_width=True)
    
    # IMPORTANT: These buttons are OUTSIDE the form
    if submitted:
        # Parse tags
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        # Create post
        success, result = create_post(title, content, category, tags)
        
        if success:
            st.success("✅ Post created successfully!")
            st.balloons()
            st.json(result)
            
            # These buttons are now outside the form
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Create Another Post", use_container_width=True):
                    st.rerun()
            
            with col2:
                if st.button("🏠 Go to Home", use_container_width=True):
                    st.session_state.page = "home"
                    st.rerun()
        else:
            st.error("❌ Error creating post:")
            for error in result:
                st.error(f"• {error}")

# ============================================================
# Page: View Single Post
# ============================================================

def page_view_post():
    """View single post page"""
    post_id = st.session_state.get('selected_post_id')
    
    if not post_id:
        st.error("No post selected")
        if st.button("🏠 Go to Home"):
            st.session_state.page = "home"
            st.rerun()
        return
    
    post = get_post_by_id(post_id)
    
    if post:
        st.markdown(f'<h1 class="main-header">{post["title"]}</h1>', unsafe_allow_html=True)
        
        # Metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Category", post['category'])
        with col2:
            st.metric("Created", format_datetime(post['createdAt']))
        with col3:
            st.metric("Updated", format_datetime(post['updatedAt']))
        
        st.markdown("---")
        
        # Tags
        st.markdown("**Tags:**")
        for tag in post['tags']:
            st.markdown(f'<span class="tag">{tag}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Content
        st.markdown("### Content")
        st.write(post['content'])
        
        st.markdown("---")
        
        # Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
        
        with col2:
            if st.button("✏️ Edit Post", use_container_width=True):
                st.session_state.page = "edit_post"
                st.rerun()
        
        with col3:
            if st.button("🗑️ Delete Post", type="primary", use_container_width=True):
                st.session_state.show_delete_confirm = True
                st.rerun()
        
        # Delete confirmation
        if st.session_state.get('show_delete_confirm', False):
            st.warning("⚠️ Are you sure you want to delete this post? This action cannot be undone!")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                    success, message = delete_post(post_id)
                    if success:
                        st.success(message)
                        st.session_state.page = "home"
                        st.session_state.show_delete_confirm = False
                        st.rerun()
                    else:
                        st.error(message)
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_delete_confirm = False
                    st.rerun()


# ============================================================
# Page: Edit Post
# ============================================================

def page_edit_post():
    """Edit post page"""
    post_id = st.session_state.get('selected_post_id')
    
    if not post_id:
        st.error("No post selected")
        if st.button("🏠 Go to Home"):
            st.session_state.page = "home"
            st.rerun()
        return
    
    post = get_post_by_id(post_id)
    
    if not post:
        return
    
    st.markdown(f'<h1 class="main-header">✏️ Edit Post</h1>', unsafe_allow_html=True)
    
    with st.form("edit_post_form"):
        title = st.text_input("Title *", value=post['title'])
        
        categories = ["Technology", "Travel", "Food", "Lifestyle", "Education", "Health", "Business", "Other"]
        category_index = categories.index(post['category']) if post['category'] in categories else 0
        category = st.selectbox("Category *", categories, index=category_index)
        
        content = st.text_area("Content *", value=post['content'], height=300)
        
        tags_string = ", ".join(post['tags'])
        tags_input = st.text_input("Tags * (comma-separated)", value=tags_string)
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Update Post", use_container_width=True)
        
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted:
            # Parse tags
            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            
            # Update post
            success, result = update_post(post_id, title, content, category, tags)
            
            if success:
                st.success("✅ Post updated successfully!")
                st.session_state.page = "view_post"
                st.rerun()
            else:
                st.error("❌ Error updating post:")
                for error in result:
                    st.error(f"• {error}")
        
        if cancel:
            st.session_state.page = "view_post"
            st.rerun()


# ============================================================
# Sidebar Navigation
# ============================================================

def sidebar():
    """Sidebar with navigation and info"""
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        
        if st.button("✍️ Create New Post", use_container_width=True):
            st.session_state.page = "create_post"
            st.rerun()
        
        st.markdown("---")
        
        # API Status
        st.markdown("## 📡 API Status")
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=2)
            if response.status_code == 200:
                st.success("✅ Connected")
                data = response.json()
                st.caption(f"Version: {data.get('version', 'N/A')}")
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ Disconnected")
            st.caption("Make sure Flask server is running on port 5000")
        
        st.markdown("---")
        
        # Stats
        st.markdown("## 📊 Statistics")
        posts = get_all_posts()
        st.metric("Total Posts", len(posts))
        
        if posts:
            categories = {}
            for post in posts:
                cat = post.get('category', 'Other')
                categories[cat] = categories.get(cat, 0) + 1
            
            st.markdown("**Posts by Category:**")
            for cat, count in categories.items():
                st.caption(f"{cat}: {count}")
        
        st.markdown("---")
        st.caption("Made with ❤️ using Streamlit")


# ============================================================
# Main Application
# ============================================================

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    # Render sidebar
    sidebar()
    
    # Route to appropriate page
    if st.session_state.page == "home":
        page_home()
    elif st.session_state.page == "create_post":
        page_create_post()
    elif st.session_state.page == "view_post":
        page_view_post()
    elif st.session_state.page == "edit_post":
        page_edit_post()
    else:
        page_home()


if __name__ == "__main__":
    main()