import logging
from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from db.session import get_db
from core.hashing import Hasher
from db.repository.login import get_user_by_email
from core.security import create_access_token, verify_token, TokenError
from core.config import settings
from schemas.user import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/token",
    scheme_name="JWT"
)


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[UserResponse]:
    """
    Authenticate a user with email and password.
    
    Args:
        email: User's email address
        password: User's plain text password
        db: Async database session
        
    Returns:
        UserResponse object if authentication successful, None otherwise
    """
    try:
        # Input validation
        if not email or not password:
            logger.warning("Empty email or password provided")
            return None
        
        # Get user from database
        user = await get_user_by_email(email=email, db=db)
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt with inactive user: {email}")
            return None
        
        # Verify password
        if not Hasher.verify_password(password, user.password):
            logger.warning(f"Failed login attempt for user: {email}")
            return None
        
        logger.info(f"Successful authentication for user: {email}")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error for user {email}: {e}")
        return None


@router.post("/token", response_model=dict)
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.
    
    Args:
        request: FastAPI request object
        form_data: OAuth2 form data containing username (email) and password
        db: Async database session
        
    Returns:
        Dictionary containing access token and token type
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Log login attempt (without sensitive data)
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Login attempt from IP: {client_ip} for email: {form_data.username}")
        
        # Authenticate user
        user = await authenticate_user(
            email=form_data.username,
            password=form_data.password,
            db=db
        )
        
        if not user:
            logger.warning(f"Failed login attempt for email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        # Set HttpOnly cookie
        response.set_cookie(
            key=settings.COOKIE_NAME,
            value=access_token,
            max_age=settings.COOKIE_MAX_AGE,
            expires=settings.COOKIE_MAX_AGE,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/"
        )
        
        logger.info(f"Access token created and set as HttpOnly cookie for user: {user.email}")
        
        return {
            "access_token": access_token,  # Include token for header-based auth
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value  # Include user role for frontend routing
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Get current authenticated user from JWT token (cookie or header).
    
    Args:
        request: FastAPI request object
        db: Async database session
        
    Returns:
        UserResponse object for authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        # Try to get token from cookie first
        token = request.cookies.get(settings.COOKIE_NAME)
        
        # If no cookie token, try Authorization header
        if not token:
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
        
        if not token:
            logger.warning("No access token found in cookies or Authorization header")
            raise credentials_exception
        
        # Verify token
        payload = verify_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
        
        # Get user from database
        user = await get_user_by_email(email=email, db=db)
        if user is None:
            logger.warning(f"Token valid but user not found: {email}")
            raise credentials_exception
        
        # Check if user is still active
        if not user.is_active:
            logger.warning(f"Token valid but user inactive: {email}")
            raise credentials_exception
        
        logger.debug(f"Current user authenticated: {email}")
        return user
        
    except TokenError as e:
        logger.warning(f"Token validation failed: {e}")
        raise credentials_exception
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get current active user (additional validation).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse object for active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        logger.warning(f"Access attempt by inactive user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing the JWT cookie.
    
    Args:
        response: FastAPI response object
        
    Returns:
        Success message
    """
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        domain=settings.COOKIE_DOMAIN,
        path="/"
    )
    
    logger.info("User logged out - JWT cookie cleared")
    return {"detail": "Logged out successfully"}
