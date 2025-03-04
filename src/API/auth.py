import logging
from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def generate_token(user_id):
    """Generate a JWT token."""
    try:
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key:
            logger.error("SECRET_KEY not found in environment variables")
            raise ValueError("SECRET_KEY not configured")
            
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Authentication required'}), 401

            # Remove 'Bearer ' prefix if present
            token = token.replace('Bearer ', '')
            secret_key = os.getenv('SECRET_KEY')
            
            if not secret_key:
                logger.error("SECRET_KEY not found in environment variables")
                return jsonify({'message': 'Server configuration error'}), 500

            jwt.decode(token, secret_key, algorithms=['HS256'])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token received")
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token received: {str(e)}")
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            logger.error(f"Unexpected error in authentication: {str(e)}")
            return jsonify({'message': 'Server error during authentication'}), 500
    return decorated 