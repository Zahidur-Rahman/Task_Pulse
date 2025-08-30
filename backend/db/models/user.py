from db.base_class import Base
from sqlalchemy import Column, Boolean, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    manager = "manager"

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_tasks = relationship("Task", back_populates="author", foreign_keys="[Task.author_id]")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="[Task.assignee_id]")
    assigned_tasks_multi = relationship(
        "Task", 
        secondary="task_assignees", 
        back_populates="assignees",
        primaryjoin="User.id == task_assignees.c.user_id",
        secondaryjoin="Task.id == task_assignees.c.task_id"
    )  # Multiple task assignments
    subtasks = relationship("Subtask", back_populates="assignee")
    time_logs = relationship("TimeLog", back_populates="user")
    organization = relationship("Organization", back_populates="users")
    task_comments = relationship("TaskComment", back_populates="user")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self):
        return self.role == UserRole.admin
    
    @property
    def is_manager(self):
        return self.role in [UserRole.admin, UserRole.manager]
