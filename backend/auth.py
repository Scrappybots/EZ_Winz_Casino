"""
Authentication and authorization logic
"""
import bcrypt
from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from .models import db, User, APIKey
from datetime import datetime


def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def register_user(character_name, password, faction=None):
    """Register a new user"""
    from .models import generate_account_number
    
    # Check if user already exists
    if User.query.filter_by(character_name=character_name).first():
        return None, "Character name already exists"
    
    # Create new user
    user = User(
        character_name=character_name,
        password_hash=hash_password(password),
        account_number=generate_account_number(),
        faction=faction,
        balance=0.0
    )
    
    db.session.add(user)
    db.session.commit()
    
    return user, None


def login_user(character_name, password):
    """Authenticate a user and return JWT token"""
    user = User.query.filter_by(character_name=character_name).first()
    
    if not user or not verify_password(password, user.password_hash):
        return None, "Invalid credentials"
    
    # Create JWT token (identity must be a string)
    access_token = create_access_token(identity=str(user.id))
    
    return {
        'access_token': access_token,
        'user': user.to_dict()
    }, None


def get_current_user():
    """Get the current authenticated user from JWT"""
    user_id = get_jwt_identity()
    # Convert string identity back to integer
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def api_key_required(f):
    """Decorator to require valid API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in header or body
        api_key = request.headers.get('X-API-Key')
        if not api_key and request.is_json:
            api_key = request.json.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key
        key_obj = APIKey.query.filter_by(key_value=api_key, is_active=True).first()
        if not key_obj:
            return jsonify({'error': 'Invalid or inactive API key'}), 401
        
        # Update last used timestamp
        key_obj.last_used = datetime.utcnow()
        db.session.commit()
        
        # Store API key object in request context
        request.api_key = key_obj
        
        return f(*args, **kwargs)
    return decorated_function
