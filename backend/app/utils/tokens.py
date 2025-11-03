import jwt
from datetime import datetime, timezone
from flask import current_app
from app import db
from app.models import PasswordResetToken
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

def generate_reset_token(user):
    """
    Generate a JWT token for password reset and store it in database
    Returns: token string
    """
    # Create JWT payload
    expiry = datetime.now(timezone.utc) + current_app.config['PASSWORD_RESET_TOKEN_EXPIRY']
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': expiry,
        'iat': datetime.n0w(timezone.utc),
        'type': 'password_reset'
    }
    
    # Generate JWT token
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )
    
    # Store token in database
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expiry
    )
    db.session.add(reset_token)
    db.session.commit()
    
    return token

def verify_reset_token(token):
    """
    Verify JWT token and check if it exists in database and is valid
    Returns: user object if valid, None otherwise
    """
    try:
        # Decode JWT
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config['JWT_ALGORITHM']]
        )
        
        # Check if token type is correct
        if payload.get('type') != 'password_reset':
            return None
        
        # Check if token exists in database and is valid
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if not reset_token or not reset_token.is_valid():
            return None
        
        # Get user
        from app.models import Users
        user = Users.query.get(payload['user_id'])
        
        return user, reset_token
        
    except ExpiredSignatureError:
        current_app.logger.warning("Password reset token has expired")
        return None
    except InvalidTokenError as e:
        current_app.logger.warning(f"Invalid password reset token: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"Error verifying reset token: {str(e)}")
        return None


def invalidate_token(reset_token):
    """Mark token as used and delete it"""
    try:
        reset_token.used = True
        db.session.delete(reset_token)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error invalidating token: {str(e)}")


def cleanup_expired_tokens():
    """Delete all expired tokens from database"""
    try:
        expired = PasswordResetToken.query.filter(
            PasswordResetToken.expires_at < datetime.n0w(timezone.utc)
        ).all()
        
        for token in expired:
            db.session.delete(token)
        
        db.session.commit()
        current_app.logger.info(f"Cleaned up {len(expired)} expired tokens")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cleaning up expired tokens: {str(e)}")


