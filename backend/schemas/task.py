from typing import List, Optional, TYPE_CHECKING, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from db.models.task import TaskStatusType, TaskPriority, TaskType
import re

if TYPE_CHECKING:
    from schemas.user import UserProfile

class SubtaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assignee_id: int
    priority: TaskPriority = TaskPriority.medium
    estimated_hours: float = Field(default=0.0, ge=0)
    due_date: Optional[datetime] = None
    order_index: int = Field(default=0, ge=0)
    depends_on_subtask_id: Optional[int] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Research API documentation",
                "description": "Find and review existing API documentation",
                "assignee_id": 2,
                "priority": "medium",
                "estimated_hours": 2.0,
                "due_date": "2024-01-20T10:00:00Z"
            }
        }
    )

class SubtaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    priority: Optional[TaskPriority] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    order_index: Optional[int] = Field(None, ge=0)
    depends_on_subtask_id: Optional[int] = None

class SubtaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    parent_task_id: int
    assignee_id: int
    status: TaskStatusType
    priority: TaskPriority
    estimated_hours: float
    actual_hours: float
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    order_index: int
    depends_on_subtask_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", min_length=0, max_length=2000)
    task_type: TaskType = TaskType.task
    priority: TaskPriority = TaskPriority.medium
    assignee_id: int  # Primary assignee (required for backward compatibility)
    assignee_ids: Optional[List[int]] = None  # Additional assignees (optional)
    estimated_hours: float = Field(default=0.0, ge=0)
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    is_public: bool = False
    tags: Optional[str] = None
    subtasks: Optional[List[SubtaskCreate]] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Task title cannot be empty')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        # Allow empty descriptions, just strip whitespace
        return v.strip() if v else ""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Build User Dashboard",
                "description": "Create a comprehensive user dashboard with task management features",
                "task_type": "feature",
                "priority": "high",
                "assignee_id": 2,
                "estimated_hours": 16.0,
                "due_date": "2024-01-25T17:00:00Z",
                "is_public": True,
                "tags": "dashboard,ui,frontend"
            }
        }
    )

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    task_type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    is_public: Optional[bool] = None
    tags: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    slug: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatusType
    author_id: int
    assignee_id: int
    estimated_hours: float
    actual_hours: float
    start_date: Optional[datetime]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    is_active: bool
    is_public: bool
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    progress_percentage: int
    is_overdue: bool
    
    model_config = ConfigDict(from_attributes=True)

class TaskDetailResponse(TaskResponse):
    subtasks: List[SubtaskResponse] = []
    time_logs: List[Any] = []
    comments: List[Any] = []
    author_name: str = ""
    assignee_name: str = ""

class TaskListResponse(BaseModel):
    id: int
    title: str
    status: TaskStatusType
    priority: TaskPriority
    assignee_name: str
    due_date: Optional[datetime]
    progress_percentage: int
    is_overdue: bool
    estimated_hours: float
    actual_hours: float
    
    model_config = ConfigDict(from_attributes=True)

class TaskFilter(BaseModel):
    status: Optional[TaskStatusType] = None
    priority: Optional[TaskPriority] = None
    task_type: Optional[TaskType] = None
    assignee_id: Optional[int] = None
    author_id: Optional[int] = None
    is_overdue: Optional[bool] = None
    search: Optional[str] = None
    tags: Optional[str] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None

class PaginatedTaskResponse(BaseModel):
    tasks: List[TaskListResponse]
    total: int
    skip: int
    limit: int
    
    model_config = ConfigDict(from_attributes=True)

class TaskAssignment(BaseModel):
    task_id: int
    assignee_email: str
    
    @field_validator('assignee_email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        return v.strip().lower()

class TaskStatusChange(BaseModel):
    status: TaskStatusType

class TaskBulkUpdate(BaseModel):
    task_ids: List[int] = Field(..., min_length=1, max_length=100)
    status: Optional[TaskStatusType] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None

class TimeLogCreate(BaseModel):
    task_id: int
    subtask_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None

class TimeLogUpdate(BaseModel):
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None

class TimeLogResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    subtask_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: int
    description: Optional[str]
    created_at: datetime
    is_active: bool
    duration_hours: float
    
    model_config = ConfigDict(from_attributes=True)

class TaskCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_internal: bool = False

class TaskCommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)

class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    content: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime
    user_name: str
    
    model_config = ConfigDict(from_attributes=True)

class AdminDashboard(BaseModel):
    total_users: int = 0
    total_tasks: int = 0
    active_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    total_hours_logged: float = 0.0
    users_by_role: dict = {}
    tasks_by_status: dict = {}
    tasks_by_priority: dict = {}
    recent_activities: List[dict] = []
    top_performers: List[dict] = []
    overdue_tasks_list: List[TaskListResponse] = []

class UserTaskSummary(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    user_role: str
    total_assigned_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0
    total_hours_logged: float = 0.0
    current_tasks: List[TaskListResponse] = []

# Missing schemas that are imported in routes
class UpdateTask(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    task_type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    is_public: Optional[bool] = None
    tags: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class AssigneeResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    
    model_config = ConfigDict(from_attributes=True)

class TaskTitleResponse(BaseModel):
    id: int
    title: str
    slug: str
    
    model_config = ConfigDict(from_attributes=True)


