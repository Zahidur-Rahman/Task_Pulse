from db.base_class import Base
from sqlalchemy import Column, Boolean, Integer, String
from sqlalchemy.orm import relationship
from .task import Task

class User(Base):
    __tablename__ = 'user'  # Specify the table name

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
  
    created_tasks = relationship("Task", back_populates="author", foreign_keys="[Task.author_id]")
    
  
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="[Task.assignee_id]")
