"""
Authentication routes for WorkLifeOS
Handles user registration, login, token refresh, and logout
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import logging

from app import db
from app.models import User
from app.utils import success_response, error_response, validate_email, validate_password, validate_timezone

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Expected JSON:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "first_name": "string (optional)",
        "last_name": "string (optional)",
        "timezone": "string (optional, default: UTC)"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return error_response('Missing required fields: username, email, password', 400)
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        timezone = data.get('timezone', 'UTC').strip()
        
        # Validate email format
        if not validate_email(email):
            return error_response('Invalid email format', 400)
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return error_response(message, 400)
        
        # Validate timezone
        if not validate_timezone(timezone):
            return error_response('Invalid timezone', 400)
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return error_response('Username already exists', 409)
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return error_response('Email already exists', 409)
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            timezone=timezone
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {username}")
        
        return success_response(
            data={'user_id': user.id, 'username': user.username, 'email': user.email},
            message='User registered successfully',
            status_code=201
        )
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return error_response('Registration failed', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT tokens
    
    Expected JSON:
    {
        "username_or_email": "string",
        "password": "string"
    }
    
    Returns:
    {
        "access_token": "string",
        "refresh_token": "string",
        "user": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['username_or_email', 'password']):
            return error_response('Missing username_or_email or password', 400)
        
        username_or_email = data['username_or_email'].strip().lower()
        password = data['password']
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            logger.warning(f"Failed login attempt for: {username_or_email}")
            return error_response('Invalid username/email or password', 401)
        
        if not user.is_active:
            return error_response('User account is inactive', 401)
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        logger.info(f"User logged in: {user.username}")
        
        return success_response(
            data={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            },
            message='Login successful'
        )
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return error_response('Login failed', 500)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh access token using refresh token
    
    Returns:
    {
        "access_token": "string"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        if not user.is_active:
            return error_response('User account is inactive', 401)
        
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        
        logger.info(f"Token refreshed for user: {user.username}")
        
        return success_response(
            data={'access_token': access_token},
            message='Token refreshed successfully'
        )
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return error_response('Token refresh failed', 500)


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (token invalidation on client side)
    Note: JWT tokens are stateless, logout is handled on the client by removing tokens
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user:
            logger.info(f"User logged out: {user.username}")
        
        return success_response(message='Logout successful')
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return error_response('Logout failed', 500)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's profile
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        return success_response(
            data=user.to_dict(),
            message='User retrieved successfully'
        )
    
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return error_response('Failed to retrieve user', 500)


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """
    Change user password
    
    Expected JSON:
    {
        "old_password": "string",
        "new_password": "string"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['old_password', 'new_password']):
            return error_response('Missing old_password or new_password', 400)
        
        # Verify old password
        if not check_password_hash(user.password_hash, data['old_password']):
            return error_response('Invalid old password', 401)
        
        # Validate new password
        is_valid, message = validate_password(data['new_password'])
        if not is_valid:
            return error_response(message, 400)
        
        # Update password
        user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        
        return success_response(message='Password changed successfully')
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Change password error: {str(e)}")
        return error_response('Password change failed', 500)
