"""Input validation and sanitization utilities"""
from email_validator import validate_email, EmailNotValidError
import bleach
import re
from urllib.parse import urlparse

# Allowed HTML tags and attributes for sanitization
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'code', 'pre']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {
    'documents': {'.pdf', '.doc', '.docx', '.txt', '.md', '.tex', '.bib'},
    'images': {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'},
    'data': {'.csv', '.xlsx', '.xls', '.json', '.xml'},
    'code': {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h'},
    'archives': {'.zip', '.tar', '.gz', '.7z'},
    'presentations': {'.ppt', '.pptx', '.odp'},
}

def validate_email_address(email):
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        tuple: (is_valid, normalized_email, error_message)
    """
    if not email or not isinstance(email, str):
        return False, None, "Email is required"
    
    try:
        # Validate and normalize
        validated = validate_email(email, check_deliverability=False)
        return True, validated.normalized, None
    except EmailNotValidError as e:
        return False, None, str(e)

def validate_url(url, require_https=False):
    """
    Validate URL format
    
    Args:
        url: URL to validate
        require_https: If True, only allow HTTPS URLs
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not url:
        return True, None  # Empty URLs are allowed
    
    if not isinstance(url, str):
        return False, "URL must be a string"
    
    try:
        result = urlparse(url)
        
        # Check if scheme and netloc are present
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"
        
        # Check if scheme is http or https
        if result.scheme not in ['http', 'https']:
            return False, "URL must use HTTP or HTTPS protocol"
        
        # Check HTTPS requirement
        if require_https and result.scheme != 'https':
            return False, "URL must use HTTPS protocol"
        
        return True, None
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"

def validate_filename(filename):
    """
    Validate and sanitize filename
    
    Args:
        filename: Original filename
        
    Returns:
        tuple: (is_valid, sanitized_filename, error_message)
    """
    if not filename or not isinstance(filename, str):
        return False, None, "Filename is required"
    
    # Remove path components to prevent directory traversal
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove or replace dangerous characters
    # Allow alphanumeric, dots, hyphens, underscores, and spaces
    sanitized = re.sub(r'[^a-zA-Z0-9._\- ]', '', filename)
    
    # Ensure filename is not empty after sanitization
    if not sanitized or sanitized.strip() == '':
        return False, None, "Invalid filename"
    
    # Ensure filename has an extension
    if '.' not in sanitized:
        return False, None, "Filename must have an extension"
    
    # Limit filename length
    if len(sanitized) > 255:
        return False, None, "Filename too long (max 255 characters)"
    
    return True, sanitized, None

def validate_file_extension(filename, allowed_categories=None):
    """
    Validate file extension against allowed list
    
    Args:
        filename: Filename to check
        allowed_categories: List of allowed categories (e.g., ['documents', 'images'])
                          If None, all categories are allowed
        
    Returns:
        tuple: (is_valid, extension, error_message)
    """
    if not filename or '.' not in filename:
        return False, None, "File must have an extension"
    
    extension = '.' + filename.rsplit('.', 1)[1].lower()
    
    # Build allowed extensions set
    if allowed_categories is None:
        allowed = set()
        for exts in ALLOWED_EXTENSIONS.values():
            allowed.update(exts)
    else:
        allowed = set()
        for category in allowed_categories:
            if category in ALLOWED_EXTENSIONS:
                allowed.update(ALLOWED_EXTENSIONS[category])
    
    if extension not in allowed:
        return False, extension, f"File type '{extension}' not allowed"
    
    return True, extension, None

def sanitize_html(text, allowed_tags=None, allowed_attributes=None):
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        text: HTML text to sanitize
        allowed_tags: List of allowed HTML tags (uses default if None)
        allowed_attributes: Dict of allowed attributes per tag (uses default if None)
        
    Returns:
        str: Sanitized HTML
    """
    if not text:
        return text
    
    if allowed_tags is None:
        allowed_tags = ALLOWED_TAGS
    if allowed_attributes is None:
        allowed_attributes = ALLOWED_ATTRIBUTES
    
    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

def sanitize_text(text, max_length=None):
    """
    Sanitize plain text input
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length (None for no limit)
        
    Returns:
        tuple: (is_valid, sanitized_text, error_message)
    """
    if text is None:
        return True, '', None
    
    if not isinstance(text, str):
        return False, None, "Text must be a string"
    
    # Strip leading/trailing whitespace
    sanitized = text.strip()
    
    # Check length
    if max_length and len(sanitized) > max_length:
        return False, None, f"Text too long (max {max_length} characters)"
    
    return True, sanitized, None

def validate_password_strength(password, min_length=8):
    """
    Validate password strength
    
    Args:
        password: Password to validate
        min_length: Minimum password length
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    # Check for at least one letter and one number
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_number = bool(re.search(r'\d', password))
    
    if not (has_letter and has_number):
        return False, "Password must contain both letters and numbers"
    
    return True, None

def validate_integer(value, min_value=None, max_value=None):
    """
    Validate integer input
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value (None for no limit)
        max_value: Maximum allowed value (None for no limit)
        
    Returns:
        tuple: (is_valid, int_value, error_message)
    """
    try:
        int_value = int(value)
        
        if min_value is not None and int_value < min_value:
            return False, None, f"Value must be at least {min_value}"
        
        if max_value is not None and int_value > max_value:
            return False, None, f"Value must be at most {max_value}"
        
        return True, int_value, None
    except (ValueError, TypeError):
        return False, None, "Invalid integer value"
