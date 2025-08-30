import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from schemas.user import UserCreate
from db.models.user import User, UserRole
from core.hashing import Hasher
from db.repository.base import AsyncRepository

logger = logging.getLogger(__name__)


class UserRepository(AsyncRepository[User]):
    """Async repository for User operations."""
    
    def __init__(self):
        super().__init__(User)
    
    async def create_new_user(
        self, 
        user: UserCreate, 
        db: AsyncSession
    ) -> User:
        """Create a new user."""
        try:
            # Hash the password
            hashed_password = Hasher.hash_password(user.password)
            
            # Create new user
            new_user = User(
                email=user.email,
                password=hashed_password,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                organization_id=user.organization_id,
                is_active=True
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(f"User created successfully: {new_user.email}")
            return new_user
            
        except IntegrityError as e:
            logger.error(f"Integrity error creating user {user.email}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error creating user {user.email}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user due to database error"
            )
        except Exception as e:
            logger.error(f"Unexpected error creating user {user.email}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def get_user_by_email(
        self, 
        email: str, 
        db: AsyncSession
    ) -> Optional[User]:
        """Get user by email address."""
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
    
    async def get_user_by_id(
        self, 
        user_id: int, 
        db: AsyncSession
    ) -> Optional[User]:
        """Get user by ID."""
        try:
            result = await db.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                logger.debug(f"User found by ID: {user_id}")
            else:
                logger.debug(f"No user found with ID: {user_id}")
            
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while retrieving user"
            )
    
    async def update_user(
        self, 
        user_id: int, 
        update_data: dict, 
        db: AsyncSession
    ) -> Optional[User]:
        """Update user information."""
        try:
            result = await db.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User {user_id} not found for update")
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"User {user_id} updated successfully")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error updating user {user_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while updating user"
            )
    
    async def deactivate_user(
        self, 
        user_id: int, 
        db: AsyncSession
    ) -> bool:
        """Deactivate a user."""
        try:
            result = await db.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User {user_id} not found for deactivation")
                return False
            
            user.is_active = False
            await db.commit()
            
            logger.info(f"User {user_id} deactivated successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error deactivating user {user_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while deactivating user"
            )
    
    async def get_all_active_users(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Get all active users with pagination."""
        try:
            result = await db.execute(
                select(User)
                .filter(User.is_active == True)
                .offset(skip)
                .limit(limit)
            )
            users = result.scalars().all()
            
            logger.info(f"Retrieved {len(users)} active users")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting active users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while retrieving users"
            )
    
    async def get_all_users_with_filters(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Get all users with advanced filtering."""
        try:
            query = select(User)
            
            # Apply filters
            if role is not None:
                query = query.filter(User.role == role)
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            
            # Apply pagination and ordering
            query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
            
            result = await db.execute(query)
            users = result.scalars().all()
            
            logger.info(f"Retrieved {len(users)} users with filters")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting users with filters: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while retrieving users"
            )
    
    async def get_users_by_organization(
        self,
        organization_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users by organization."""
        try:
            result = await db.execute(
                select(User)
                .filter(User.organization_id == organization_id)
                .filter(User.is_active == True)
                .order_by(User.first_name, User.last_name)
                .offset(skip)
                .limit(limit)
            )
            users = result.scalars().all()
            
            logger.info(f"Retrieved {len(users)} users from organization {organization_id}")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting users by organization {organization_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while retrieving users by organization"
            )
    
    async def get_users_by_role(
        self,
        role: UserRole,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users by role."""
        try:
            result = await db.execute(
                select(User)
                .filter(User.role == role)
                .filter(User.is_active == True)
                .order_by(User.first_name, User.last_name)
                .offset(skip)
                .limit(limit)
            )
            users = result.scalars().all()
            
            logger.info(f"Retrieved {len(users)} users with role {role}")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting users by role {role}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while retrieving users by role"
            )
    
    async def search_users(
        self,
        search_term: str,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """Search users by name or email."""
        try:
            search_pattern = f"%{search_term}%"
            
            result = await db.execute(
                select(User)
                .filter(
                    or_(
                        User.first_name.ilike(search_pattern),
                        User.last_name.ilike(search_pattern),
                        User.email.ilike(search_pattern)
                    )
                )
                .filter(User.is_active == True)
                .order_by(User.first_name, User.last_name)
                .offset(skip)
                .limit(limit)
            )
            users = result.scalars().all()
            
            logger.info(f"Found {len(users)} users matching '{search_term}'")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Database error searching users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while searching users"
            )


# Global instance
user_repository = UserRepository()

# Convenience functions for backward compatibility
async def create_new_user(user: UserCreate, db: AsyncSession) -> User:
    return await user_repository.create_new_user(user, db)

async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    return await user_repository.get_user_by_email(email, db)

async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    return await user_repository.get_user_by_id(user_id, db)

    