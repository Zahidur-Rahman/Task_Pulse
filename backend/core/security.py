import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import jwt, JWTError
from fastapi import HTTPException, status
from core.config import settings

logger = logging.getLogger(__name__)


class TokenError(Exception):
    """Custom exception for token-related errors"""
    pass


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
        
    Raises:
        TokenError: If token creation fails
    """
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        logger.debug(f"Access token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise TokenError(f"Token creation failed: {str(e)}")


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Decoded token payload
        
    Raises:
        TokenError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Check if token has expired
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise TokenError("Token has expired")
        
        logger.debug("Token verified successfully")
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise TokenError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise TokenError(f"Token verification failed: {str(e)}")


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a token without verifying it.
    
    Args:
        token: JWT token string
        
    Returns:
        Expiration datetime or None if not found
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_signature": False}
        )
        
        if "exp" in payload:
            return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        return None
        
    except Exception as e:
        logger.warning(f"Failed to get token expiration: {e}")
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired.
    
    Args:
        token: JWT token string
        
    Returns:
        True if expired, False otherwise
    """
    exp_time = get_token_expiration(token)
    if exp_time is None:
        return True
    
    return exp_time < datetime.now(timezone.utc)


 