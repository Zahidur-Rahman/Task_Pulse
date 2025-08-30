import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from db.models.user import User

logger = logging.getLogger(__name__)


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """
    Get user by email address for authentication.
    
    Args:
        email: User's email address
        db: Async database session
        
    Returns:
        User object if found, None otherwise
        
    Raises:
        HTTPException: If database error occurs
    """
    try:
        result = await db.execute(
            select(User).filter(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            logger.debug(f"User found by email: {email}")
        else:
            logger.debug(f"No user found with email: {email}")
        
        return user
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting user by email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving user"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting user by email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving user"
        )