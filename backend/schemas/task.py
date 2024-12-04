from typing import List,Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from db.models.task import TaskStatusType
from db.models.user import User
class TaskCreate(BaseModel):
    task_title: str
    description: str
    is_active: bool = True
    slug: Optional[str] = None 
    # Validator for generating slug if not provided
    @field_validator('slug', mode='before')
    def generate_slug(cls, value, values):
        if not value and 'task_title' in values:
            return values['task_title'].replace(" ", "-").lower()
        return value
    
    class Config:
        from_attributes = True
class AssigneeResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True
        

    

class TaskResponse(BaseModel):
    id: int
    task_title: str
    description: str
    slug: str
    is_active: bool
    assigned_at: datetime
    status:TaskStatusType
    assignee: Optional[AssigneeResponse]

    class Config:
        from_attributes = True
        
class PaginatedTaskResponse(BaseModel):
    tasks: List[TaskResponse]  # List of tasks
    total: int  # Total number of tasks
    skip: int   # The offset (skip value)
    limit: int  # The limit (number of tasks per page)

    class Config:
        from_attribute = True


class TaskAssignment(BaseModel):
    task_id: int
    assignee_id: int

    class Config:
        from_attributes=True


class TaskStatuseChange(BaseModel):
    status:TaskStatusType
    class Config:
        from_attributes=True
        
class UpdateTask(TaskCreate):
    
    pass

class AssigneeResponse(BaseModel):
    id: int
    email: str  

    class Config:
        from_attributes = True
        
class TaskAssignment(BaseModel):
    task_id: int
    assignee_email: str     
    
    
from pydantic import BaseModel

class TaskTitleResponse(BaseModel):
    id: int
    task_title: str
    assignee_id: int
    # Add other fields as needed

    class Config:
        orm_mode = True  # Ensure this is included to handle SQLAlchemy objects


