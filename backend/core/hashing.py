import logging
from typing import Optional
from passlib.context import CryptContext
from passlib.exc import PasswordSizeError

logger = logging.getLogger(__name__)

# Configure password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],  # Use bcrypt as it's more widely available
    deprecated="auto",
    bcrypt__rounds=12              # 12 rounds for bcrypt
)


class Hasher:
    """Password hashing and verification utilities."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        
        Args:
            plain_password: The plain text password to verify
            hashed_password: The hashed password to check against
            
        Returns:
            True if password matches, False otherwise
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not plain_password or not hashed_password:
            logger.warning("Empty password or hash provided for verification")
            return False
            
        try:
            is_valid = pwd_context.verify(plain_password, hashed_password)
            logger.debug("Password verification completed")
            return is_valid
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash a plain password using the configured hashing scheme.
        
        Args:
            plain_password: The plain text password to hash
            
        Returns:
            The hashed password string
            
        Raises:
            ValueError: If password is empty or too short
            PasswordSizeError: If password is too long
        """
        if not plain_password:
            raise ValueError("Password cannot be empty")
        
        if len(plain_password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        if len(plain_password) > 128:
            raise ValueError("Password cannot exceed 128 characters")
        
        try:
            hashed_password = pwd_context.hash(plain_password)
            logger.debug("Password hashed successfully")
            return hashed_password
            
        except PasswordSizeError as e:
            logger.error(f"Password hashing failed due to size constraints: {e}")
            raise ValueError(f"Password size issue: {str(e)}")
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise ValueError(f"Password hashing failed: {str(e)}")
    
    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        Check if a password hash needs to be rehashed.
        
        Args:
            hashed_password: The hashed password to check
            
        Returns:
            True if rehashing is needed, False otherwise
        """
        try:
            return pwd_context.needs_update(hashed_password)
        except Exception as e:
            logger.warning(f"Failed to check if password needs rehash: {e}")
            return False
    
    @staticmethod
    def get_hash_info(hashed_password: str) -> Optional[dict]:
        """
        Get information about a password hash.
        
        Args:
            hashed_password: The hashed password to analyze
            
        Returns:
            Dictionary with hash information or None if failed
        """
        try:
            return pwd_context.hash_info(hashed_password)
        except Exception as e:
            logger.warning(f"Failed to get hash info: {e}")
            return None
