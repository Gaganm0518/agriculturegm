"""
Validators utility module.
Provides input validation functions for API endpoints.
"""

import re


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password strength.
    Must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 digit.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Valid"


def validate_required_fields(data, required_fields):
    """
    Check that all required fields are present and non-empty in the data dict.
    
    Args:
        data: Dictionary of input data
        required_fields: List of required field names
    
    Returns:
        Tuple (is_valid, missing_fields)
    """
    missing = []
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            missing.append(field)
    
    if missing:
        return False, missing
    return True, []


def validate_numeric_range(value, min_val=None, max_val=None, field_name="Value"):
    """Validate that a numeric value is within the expected range."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return False, f"{field_name} must be a number"
    
    if min_val is not None and num < min_val:
        return False, f"{field_name} must be at least {min_val}"
    if max_val is not None and num > max_val:
        return False, f"{field_name} must be at most {max_val}"
    
    return True, "Valid"
