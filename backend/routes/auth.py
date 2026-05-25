"""
Authentication Routes.
Handles user registration, login, profile retrieval, and logout.
"""

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from backend.extensions import db, jwt, limiter
from backend.models.user import User
from backend.models.token_blocklist import TokenBlocklist
from backend.utils.helpers import api_response, api_error
from backend.utils.validators import validate_email, validate_password, validate_required_fields

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return api_error("Invalid JSON data", 400)
        
    # Validate required fields
    is_valid, missing = validate_required_fields(data, ['name', 'email', 'password'])
    if not is_valid:
        return api_error(f"Missing required fields: {', '.join(missing)}", 400)
        
    name = data['name'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    # Validate format
    if not validate_email(email):
        return api_error("Invalid email format", 400)
        
    pwd_valid, pwd_msg = validate_password(password)
    if not pwd_valid:
        return api_error(pwd_msg, 400)
        
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return api_error("Email already registered", 409)
        
    # Create new user
    new_user = User(
        name=name,
        email=email,
        role=data.get('role', 'farmer')  # Default to farmer, can specify admin during setup
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))
    
    return api_response(
        data={
            "user": new_user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        message="Registration successful",
        status_code=201
    )

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate a user and return tokens."""
    data = request.get_json()
    if not data:
        return api_error("Invalid JSON data", 400)
        
    is_valid, missing = validate_required_fields(data, ['email', 'password'])
    if not is_valid:
        return api_error(f"Missing required fields: {', '.join(missing)}", 400)
        
    email = data['email'].strip().lower()
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return api_error("Invalid email or password", 401)
        
    if not user.is_active:
        return api_error("Account is disabled", 403)
        
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return api_response(
        data={
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        message="Login successful"
    )

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the currently logged-in user's profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return api_error("User not found", 404)
        
    return api_response(
        data={"user": user.to_dict()},
        message="User profile retrieved successfully"
    )

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user by adding JWT to blocklist."""
    jti = get_jwt()["jti"]
    
    blocked_token = TokenBlocklist(jti=jti)
    db.session.add(blocked_token)
    db.session.commit()
    
    return api_response(message="Successfully logged out")
