from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, DateTime, Boolean, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
import enum

from db.base_class import Base

# Define an Enum for task status types
class TaskStatusType(str, enum.Enum):
    pending = "Pending"
    in_progress = "In Progress"
    completed = "Completed"

# Association table for the many-to-many relationship between Task and User (assignees)
# task_assignees = Table(
#     'task_assignees',
#     Base.metadata,
#     Column('task_id', Integer, ForeignKey('task.id'), primary_key=True),
#     Column('user_id', Integer, ForeignKey('user.id'), primary_key=True)
# )

class Task(Base):
    __tablename__ = 'task'
    
    id = Column(Integer, primary_key=True)
    task_title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(Text, nullable=False)
   
    author_id = Column(Integer, ForeignKey("user.id"))
    author = relationship("User", back_populates="created_tasks",foreign_keys=[author_id]) 

    assignee_id = Column(Integer, ForeignKey("user.id"))
    assignee = relationship("User", back_populates="assigned_tasks",foreign_keys=[assignee_id])  
    
    #assignees = relationship("User", secondary=task_assignees, back_populates="assigned_tasks")  # Assuming "assigned_tasks" in User model
    
    status = Column(Enum(TaskStatusType), nullable=False,default=TaskStatusType.pending)
    #status = relationship("TaskStatus", back_populates="task", cascade="all, delete-orphan")

    assigned_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)


