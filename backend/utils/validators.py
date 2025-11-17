def validate_post_data(data):
    """valodation blog post data"""
    errors = []

    if not data:
        return["required body is required"]
    
    # Validate title
    if "title" not in data:
        errors.append("Title is required")
    elif not data["title"] or not data["title"].strip():
        errors.append("Title cannot be empty")
    elif len(data["title"].strip()) < 3:
        errors.append("Title must be at least 3 characters long")
    elif len(data["title"]) > 200:
        errors.append("Title must be less than 200 characters")
    
    # Validate content
    if "content" not in data:
        errors.append("Content is required")
    elif not data["content"] or not data["content"].strip():
        errors.append("Content cannot be empty")
    elif len(data["content"].strip()) < 10:
        errors.append("Content must be at least 10 characters long")
    
    # Validate category
    if "category" not in data:
        errors.append("Category is required")
    elif not data["category"] or not data["category"].strip():
        errors.append("Category cannot be empty")
    
    # Validate tags
    if "tags" not in data:
        errors.append("Tags field is required")
    elif not isinstance(data["tags"], list):
        errors.append("Tags must be an array")
    elif len(data["tags"]) == 0:
        errors.append("At least one tag is required")
    else:
        # Check each tag is a string
        for i, tag in enumerate(data["tags"]):
            if not isinstance(tag, str):
                errors.append(f"Tag at index {i} must be a string")
            elif not tag.strip():
                errors.append(f"Tag at index {i} cannot be empty")
    
    return errors