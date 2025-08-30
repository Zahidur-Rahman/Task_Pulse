from typing import Optional, List, TYPE_CHECKING, Any
from pydantic import EmailStr, Field, BaseModel, ConfigDict, field_validator
from datetime import datetime
import re

from db.models.user import UserRole

if TYPE_CHECKING:
    from schemas.task import TaskResponse, TimeLogResponse

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, max_length=128, description="User's password")
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name")
    role: UserRole = Field(default=UserRole.user, description="User's role in the system")
    organization_id: Optional[int] = Field(None, description="Organization ID")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(v) > 128:
            raise ValueError('Password cannot exceed 128 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
                "organization_id": 1
            }
        }
    )

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[UserRole] = None
    organization_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "role": "manager"
            }
        }
    )

class ShowUser(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    organization_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(ShowUser):
    pass

class UserProfile(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    organization_id: Optional[int]
    is_active: bool
    created_tasks_count: int
    assigned_tasks_count: int
    completed_tasks_count: int
    total_hours_logged: float
    
    model_config = ConfigDict(from_attributes=True)

class UserDashboard(BaseModel):
    user: UserProfile
    recent_tasks: List[Any] = []
    upcoming_deadlines: List[Any] = []
    time_logs_today: List[Any] = []
    total_hours_this_week: float = 0.0
    
    model_config = ConfigDict(from_attributes=True)

class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, max_length=128, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('New password must be at least 6 characters long')
        if len(v) > 128:
            raise ValueError('New password cannot exceed 128 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('New password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('New password must contain at least one number')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "CurrentPass123",
                "new_password": "NewSecurePass456"
            }
        }
    )

