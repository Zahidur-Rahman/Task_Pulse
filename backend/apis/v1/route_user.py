import logging
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from db.models.task import Task
from db.models.user import User
from apis.v1.route_login import get_current_user, get_current_active_user
from db.session import get_db
from schemas.user import UserCreate, ShowUser, UserResponse
from db.repository.user import create_new_user
from core.hashing import Hasher

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=ShowUser,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Register a new user account"
)
async def create_user(
    request: Request,
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account.
    
    Args:
        request: FastAPI request object
        user: User creation data
        db: Async database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If user creation fails
    """
    try:
        # Log user creation attempt
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"User creation attempt from IP: {client_ip} for email: {user.email}")
        
        # Validate password strength
        if len(user.password) < 6:
            logger.warning(f"Password too short for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Check if user already exists
        result = await db.execute(select(User).filter(User.email == user.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.warning(f"User creation failed - email already exists: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = await create_new_user(user=user, db=db)
        
        logger.info(f"User created successfully: {new_user.email}")
        
        return new_user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except IntegrityError as e:
        logger.error(f"Database integrity error during user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed due to database constraints"
        )
    except Exception as e:
        logger.error(f"Unexpected error during user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user creation"
        )


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Get list of all active users"
)
async def get_all_users(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all active users.
    
    Args:
        request: FastAPI request object
        db: Async database session
        current_user: Currently authenticated user
        
    Returns:
        List of all active users
    """
    try:
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Get all users request from IP: {client_ip}")
        
        # Get all active users
        result = await db.execute(
            select(User).filter(User.is_active == True)
        )
        users = result.scalars().all()
        
        logger.info(f"Retrieved {len(users)} active users")
        
        return users
        
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving users"
        )


@router.get(
    "/available-assignees/{task_id}",
    response_model=List[UserResponse],
    summary="Get available assignees",
    description="Get list of users who can be assigned to a specific task"
)
async def get_available_assignees(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available assignees for a specific task.
    
    Args:
        request: FastAPI request object
        task_id: ID of the task
        db: Async database session
        current_user: Currently authenticated user
        
    Returns:
        List of available assignees
        
    Raises:
        HTTPException: If task not found or user not authorized
    """
    try:
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Available assignees request from IP: {client_ip} for task: {task_id}")
        
        # Validate task_id
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid task ID"
            )
        
        # Fetch the task by ID
        result = await db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check if task is active
        if not task.is_active:
            logger.warning(f"Access attempt to inactive task: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is not active"
            )
        
        # Check authorization - only task author or current assignee can view assignees
        if task.author_id != current_user.id and task.assignee_id != current_user.id:
            logger.warning(
                f"Unauthorized access attempt to task {task_id} by user {current_user.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view available assignees for this task"
            )
        
        # Get available assignees (excluding current assignee)
        result = await db.execute(
            select(User).filter(
                User.id != task.assignee_id,
                User.is_active == True
            )
        )
        available_assignees = result.scalars().all()
        
        logger.info(f"Retrieved {len(available_assignees)} available assignees for task {task_id}")
        
        return available_assignees
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting available assignees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving assignees"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user"
)
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Args:
        request: FastAPI request object
        current_user: Currently authenticated user
        
    Returns:
        Current user information
    """
    try:
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"User info request from IP: {client_ip} for user: {current_user.email}")
        
        return current_user
        
    except Exception as e:
        logger.error(f"Error getting current user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving user information"
        )


@router.put(
    "/me/password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change the current user's password"
)
async def change_password(
    request: Request,
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password.
    
    Args:
        request: FastAPI request object
        current_password: Current password for verification
        new_password: New password to set
        current_user: Currently authenticated user
        db: Async database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If password change fails
    """
    try:
        # Log password change attempt
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Password change attempt from IP: {client_ip} for user: {current_user.email}")
        
        # Validate new password
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 6 characters long"
            )
        
        # Verify current password
        if not Hasher.verify_password(current_password, current_user.password):
            logger.warning(f"Password change failed - incorrect current password for user: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed_password = Hasher.hash_password(new_password)
        
        # Update password in database
        current_user.password = new_hashed_password
        await db.commit()
        
        logger.info(f"Password changed successfully for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while changing password"
        )



