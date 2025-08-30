from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, DateTime, Boolean, ForeignKey, Enum, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from db.base_class import Base

# Many-to-many association table for task assignees
task_assignees = Table(
    'task_assignees',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('task.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now()),
    Column('assigned_by', Integer, ForeignKey('user.id'))
)

class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class TaskStatusType(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    review = "review"
    completed = "completed"
    cancelled = "cancelled"

class TaskType(str, enum.Enum):
    task = "task"
    project = "project"
    bug = "bug"
    feature = "feature"
    maintenance = "maintenance"

class Task(Base):
    __tablename__ = 'task'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    slug = Column(String(250), nullable=False, unique=True, index=True)
    
    # Task Classification
    task_type = Column(Enum(TaskType), default=TaskType.task, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium, nullable=False)
    status = Column(Enum(TaskStatusType), default=TaskStatusType.pending, nullable=False)
    
    # Assignment
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("user.id"), nullable=False)  # Primary assignee (backward compatibility)
    
    # Time Management
    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    start_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Task Properties
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    tags = Column(String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships - using string references to avoid circular imports
    author = relationship("User", back_populates="created_tasks", foreign_keys=[author_id])
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])  # Primary assignee
    assignees = relationship(
        "User", 
        secondary=task_assignees, 
        back_populates="assigned_tasks_multi",
        primaryjoin="Task.id == task_assignees.c.task_id",
        secondaryjoin="User.id == task_assignees.c.user_id"
    )  # Multiple assignees
    subtasks = relationship("Subtask", back_populates="parent_task", cascade="all, delete-orphan")
    time_logs = relationship("TimeLog", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != TaskStatusType.completed:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            # Ensure due_date is timezone-aware
            if self.due_date.tzinfo is None:
                due_date = self.due_date.replace(tzinfo=timezone.utc)
            else:
                due_date = self.due_date
            return now > due_date
        return False
    
    @property
    def progress_percentage(self):
        # Simple progress calculation without accessing relationships
        if self.status == TaskStatusType.completed:
            return 100
        elif self.status == TaskStatusType.in_progress:
            return 50
        elif self.status == TaskStatusType.review:
            return 75
        else:
            return 0


class Subtask(Base):
    __tablename__ = 'subtask'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Parent Task
    parent_task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    
    # Assignment
    assignee_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Status and Priority
    status = Column(Enum(TaskStatusType), default=TaskStatusType.pending, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium, nullable=False)
    
    # Time Management
    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Order and Dependencies
    order_index = Column(Integer, default=0)
    depends_on_subtask_id = Column(Integer, ForeignKey("subtask.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent_task = relationship("Task", back_populates="subtasks")
    assignee = relationship("User", back_populates="subtasks")
    depends_on = relationship("Subtask", remote_side=[id])
    time_logs = relationship("TimeLog", back_populates="subtask", cascade="all, delete-orphan")


class TimeLog(Base):
    __tablename__ = 'time_log'
    
    id = Column(Integer, primary_key=True)
    
    # User and Task
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    subtask_id = Column(Integer, ForeignKey("subtask.id"), nullable=True)
    
    # Time Tracking
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=0)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="time_logs")
    task = relationship("Task", back_populates="time_logs")
    subtask = relationship("Subtask", back_populates="time_logs")
    
    @property
    def is_active(self):
        return self.end_time is None
    
    @property
    def duration_hours(self):
        return self.duration_minutes / 60.0


class TaskComment(Base):
    __tablename__ = 'task_comment'
    
    id = Column(Integer, primary_key=True)
    
    # Task and User
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Comment Content
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes vs user comments
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="task_comments")


class Organization(Base):
    __tablename__ = 'organization'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization")


