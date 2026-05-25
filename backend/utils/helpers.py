"""
Helper utility functions.
Shared utility functions used across the application.
"""

import os
from datetime import datetime
from flask import jsonify


def api_response(data=None, message="Success", status_code=200):
    """
    Create a standardized API success response.
    
    Returns:
        Tuple of (response_json, status_code)
    """
    return jsonify({
        "success": True,
        "data": data or {},
        "message": message
    }), status_code


def api_error(error_message, status_code=400):
    """
    Create a standardized API error response.
    
    Returns:
        Tuple of (response_json, status_code)
    """
    return jsonify({
        "success": False,
        "error": error_message,
        "code": status_code
    }), status_code


def allowed_file(filename, allowed_extensions=None):
    """Check if a file has an allowed extension."""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


import html

def sanitize_input(data):
    """Recursively strip HTML and sanitize string inputs in a dictionary/list."""
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(i) for i in data]
    elif isinstance(data, str):
        # Escape HTML characters to prevent XSS
        return html.escape(data.strip())
    return data


def validate_image_bytes(file_stream):
    """Validate uploaded image files using magic bytes."""
    # Read first 32 bytes
    header = file_stream.read(32)
    file_stream.seek(0) # Reset stream position
    
    # Check magic bytes for common image formats
    if header.startswith(b'\xff\xd8\xff'): # JPEG
        return True
    if header.startswith(b'\x89PNG\r\n\x1a\n'): # PNG
        return True
    if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'): # GIF
        return True
    if header.startswith(b'RIFF') and header[8:12] == b'WEBP': # WEBP
        return True
    return False

def generate_unique_filename(original_filename):
    """Generate a unique filename using timestamp."""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'file'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    return f"{timestamp}.{ext}"


def ensure_dir_exists(dir_path):
    """Create directory if it doesn't exist."""
    os.makedirs(dir_path, exist_ok=True)
    return dir_path
