from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Organization name")
    description: Optional[str] = Field(None, max_length=500, description="Organization description")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Tech Solutions Inc",
                "description": "A leading technology solutions company"
            }
        }
    )

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class OrganizationWithUsers(OrganizationResponse):
    user_count: int = 0
    active_user_count: int = 0
