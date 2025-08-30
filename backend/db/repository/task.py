import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from db.models.task import Task, TaskStatusType, TaskPriority, TaskType, Subtask, TimeLog, TaskComment
from db.models.user import User, UserRole
from schemas.task import (
    TaskCreate, TaskUpdate, SubtaskCreate, SubtaskUpdate, 
    TimeLogCreate, TimeLogUpdate, TaskCommentCreate, TaskCommentUpdate,
    TaskFilter, AdminDashboard, UserTaskSummary
)
from db.repository.base import AsyncRepository

logger = logging.getLogger(__name__)


class TaskRepository(AsyncRepository[Task]):
    """Enhanced async repository for Task operations with subtasks and time tracking."""
    
    def __init__(self):
        super().__init__(Task)
    
    def _generate_slug(self, title: str) -> str:
        """Generate a slug from title."""
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    async def create_task_with_subtasks(
        self, 
        task_data: TaskCreate, 
        db: AsyncSession, 
        author_id: int
    ) -> Task:
        """Create a new task with optional subtasks."""
        try:
            # Generate slug
            slug = self._generate_slug(task_data.title)
            
            # Create main task
            new_task = Task(
                title=task_data.title,
                description=task_data.description,
                slug=slug,
                task_type=task_data.task_type,
                priority=task_data.priority,
                author_id=author_id,
                assignee_id=task_data.assignee_id,
                estimated_hours=task_data.estimated_hours,
                start_date=task_data.start_date,
                due_date=task_data.due_date,
                is_public=task_data.is_public,
                tags=task_data.tags
            )
            
            db.add(new_task)
            await db.flush()  # Get the task ID
            
            # Handle multiple assignees if provided
            if task_data.assignee_ids:
                # Add primary assignee to the many-to-many table
                from db.models.task import task_assignees
                
                # Add primary assignee
                await db.execute(
                    task_assignees.insert().values(
                        task_id=new_task.id,
                        user_id=task_data.assignee_id,
                        assigned_by=author_id
                    )
                )
                
                # Add additional assignees (excluding primary to avoid duplicates)
                additional_assignees = [uid for uid in task_data.assignee_ids if uid != task_data.assignee_id]
                for assignee_id in additional_assignees:
                    await db.execute(
                        task_assignees.insert().values(
                            task_id=new_task.id,
                            user_id=assignee_id,
                            assigned_by=author_id
                        )
                    )
            else:
                # Add only primary assignee to many-to-many table
                from db.models.task import task_assignees
                await db.execute(
                    task_assignees.insert().values(
                        task_id=new_task.id,
                        user_id=task_data.assignee_id,
                        assigned_by=author_id
                    )
                )
            
            # Create subtasks if provided
            if task_data.subtasks:
                for subtask_data in task_data.subtasks:
                    subtask = Subtask(
                        title=subtask_data.title,
                        description=subtask_data.description,
                        parent_task_id=new_task.id,
                        assignee_id=subtask_data.assignee_id,
                        priority=subtask_data.priority,
                        estimated_hours=subtask_data.estimated_hours,
                        due_date=subtask_data.due_date,
                        order_index=subtask_data.order_index,
                        depends_on_subtask_id=subtask_data.depends_on_subtask_id
                    )
                    db.add(subtask)
            
            await db.commit()
            await db.refresh(new_task)
            
            logger.info(f"Task created successfully: {new_task.id} by user {author_id}")
            return new_task
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating task: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task due to database error"
            )
    
    async def get_task_with_details(self, task_id: int, user: User, db: AsyncSession) -> Optional[Task]:
        """Get task with all related details."""
        try:
            result = await db.execute(
                select(Task)
                .filter(Task.id == task_id)
                .options(
                    selectinload(Task.subtasks),
                    selectinload(Task.time_logs),
                    selectinload(Task.comments),
                    selectinload(Task.author),
                    selectinload(Task.assignee)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting task details {task_id}: {e}")
            return None
    
    async def get_user_tasks(self, user_id: int, db: AsyncSession, filters: TaskFilter, skip: int = 0, limit: int = 20) -> tuple[List[Task], int]:
        """Get tasks for a specific user with filtering and pagination."""
        try:
            # Build base query
            query = select(Task).filter(Task.assignee_id == user_id)
            
            # Apply filters
            if filters.status:
                query = query.filter(Task.status == filters.status)
            if filters.priority:
                query = query.filter(Task.priority == filters.priority)
            if filters.task_type:
                query = query.filter(Task.task_type == filters.task_type)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Task.title.ilike(search_term),
                        Task.description.ilike(search_term)
                    )
                )
            if filters.due_date_from:
                query = query.filter(Task.due_date >= filters.due_date_from)
            if filters.due_date_to:
                query = query.filter(Task.due_date <= filters.due_date_to)
            
            # Get total count
            count_result = await db.execute(
                select(func.count()).select_from(query.subquery())
            )
            total = count_result.scalar()
            
            # Apply pagination and ordering
            query = query.order_by(Task.due_date.asc()).offset(skip).limit(limit)
            
            result = await db.execute(query)
            tasks = result.scalars().all()
            
            return list(tasks), total
            
        except Exception as e:
            logger.error(f"Error getting user tasks for user {user_id}: {e}")
            return [], 0
    
    async def update_task_status(self, task_id: int, new_status: TaskStatusType, db: AsyncSession, user_id: int) -> Optional[Task]:
        """Update task status."""
        try:
            result = await db.execute(
                select(Task).filter(
                    and_(Task.id == task_id, Task.assignee_id == user_id)
                )
            )
            task = result.scalar_one_or_none()
            if task:
                task.status = new_status
                if new_status == TaskStatusType.completed:
                    task.completed_at = datetime.now()
                await db.commit()
                await db.refresh(task)
            return task
        except Exception as e:
            logger.error(f"Error updating task status {task_id}: {e}")
            return None
    
    async def add_subtask(self, task_id: int, subtask_data: SubtaskCreate, db: AsyncSession, user_id: int) -> Subtask:
        """Add a subtask to a task."""
        try:
            # Verify user has access to the parent task
            task_result = await db.execute(
                select(Task).filter(
                    and_(Task.id == task_id, Task.assignee_id == user_id)
                )
            )
            task = task_result.scalar_one_or_none()
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or access denied"
                )
            
            subtask = Subtask(
                title=subtask_data.title,
                description=subtask_data.description,
                parent_task_id=task_id,
                assignee_id=subtask_data.assignee_id,
                priority=subtask_data.priority,
                estimated_hours=subtask_data.estimated_hours,
                due_date=subtask_data.due_date,
                order_index=subtask_data.order_index,
                depends_on_subtask_id=subtask_data.depends_on_subtask_id
            )
            
            db.add(subtask)
            await db.commit()
            await db.refresh(subtask)
            
            return subtask
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding subtask to task {task_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add subtask"
            )
    
    async def start_time_log(self, time_log_data: TimeLogCreate, db: AsyncSession, user_id: int) -> TimeLog:
        """Start a time log for a task."""
        try:
            # Verify user has access to the task
            task_result = await db.execute(
                select(Task).filter(
                    and_(Task.id == time_log_data.task_id, Task.assignee_id == user_id)
                )
            )
            task = task_result.scalar_one_or_none()
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or access denied"
                )
            
            time_log = TimeLog(
                user_id=user_id,
                task_id=time_log_data.task_id,
                subtask_id=time_log_data.subtask_id,
                start_time=time_log_data.start_time,
                end_time=time_log_data.end_time,
                duration_minutes=time_log_data.duration_minutes or 0,
                description=time_log_data.description
            )
            
            db.add(time_log)
            await db.commit()
            await db.refresh(time_log)
            
            return time_log
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting time log: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start time log"
            )
    
    async def stop_time_log(self, time_log_id: int, db: AsyncSession, user_id: int) -> TimeLog:
        """Stop a time log."""
        try:
            result = await db.execute(
                select(TimeLog).filter(
                    and_(TimeLog.id == time_log_id, TimeLog.user_id == user_id)
                )
            )
            time_log = result.scalar_one_or_none()
            if not time_log:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Time log not found or access denied"
                )
            
            if time_log.end_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Time log already stopped"
                )
            
            time_log.end_time = datetime.now()
            if time_log.start_time:
                duration = time_log.end_time - time_log.start_time
                time_log.duration_minutes = int(duration.total_seconds() / 60)
            
            await db.commit()
            await db.refresh(time_log)
            
            return time_log
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error stopping time log {time_log_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop time log"
            )
    
    async def get_admin_dashboard(self, db: AsyncSession) -> AdminDashboard:
        """Get comprehensive admin dashboard data."""
        try:
            # Basic counts - exclude admin users from total user count
            total_users = await db.scalar(
                select(func.count(User.id)).filter(User.role != UserRole.admin)
            )
            total_tasks = await db.scalar(select(func.count(Task.id)))
            active_tasks = await db.scalar(
                select(func.count(Task.id)).filter(Task.status != TaskStatusType.completed)
            )
            completed_tasks = await db.scalar(
                select(func.count(Task.id)).filter(Task.status == TaskStatusType.completed)
            )
            
            # Fix timezone issue for overdue tasks
            from datetime import timezone
            now = datetime.now(timezone.utc)
            overdue_tasks = await db.scalar(
                select(func.count(Task.id)).filter(
                    and_(
                        Task.due_date < now,
                        Task.status != TaskStatusType.completed
                    )
                )
            )
            
            # Time logs sum
            total_hours = await db.scalar(
                select(func.sum(TimeLog.duration_minutes)).filter(TimeLog.end_time.isnot(None))
            )
            total_hours_logged = (total_hours or 0) / 60.0
            
            # Users by role
            users_by_role_result = await db.execute(
                select(User.role, func.count(User.id)).group_by(User.role)
            )
            users_by_role = {role.value: count for role, count in users_by_role_result.all()}
            
            # Tasks by status
            tasks_by_status_result = await db.execute(
                select(Task.status, func.count(Task.id)).group_by(Task.status)
            )
            tasks_by_status = {status.value: count for status, count in tasks_by_status_result.all()}
            
            # Tasks by priority
            tasks_by_priority_result = await db.execute(
                select(Task.priority, func.count(Task.id)).group_by(Task.priority)
            )
            tasks_by_priority = {priority.value: count for priority, count in tasks_by_priority_result.all()}
            
            return AdminDashboard(
                total_users=total_users or 0,
                total_tasks=total_tasks or 0,
                active_tasks=active_tasks or 0,
                completed_tasks=completed_tasks or 0,
                overdue_tasks=overdue_tasks or 0,
                total_hours_logged=total_hours_logged,
                users_by_role=users_by_role,
                tasks_by_status=tasks_by_status,
                tasks_by_priority=tasks_by_priority,
                recent_activities=[],  # TODO: Implement activity tracking
                top_performers=[],  # TODO: Implement performance metrics
                overdue_tasks_list=[]  # TODO: Implement overdue tasks list
            )
            
        except Exception as e:
            logger.error(f"Error getting admin dashboard: {e}")
            return AdminDashboard()
    
    async def get_user_task_summary(self, user_id: int, db: AsyncSession) -> UserTaskSummary:
        """Get comprehensive user task summary."""
        try:
            user_result = await db.execute(
                select(User).filter(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get task counts
            total_tasks = await db.scalar(
                select(func.count(Task.id)).filter(Task.assignee_id == user_id)
            )
            completed_tasks = await db.scalar(
                select(func.count(Task.id)).filter(
                    and_(Task.assignee_id == user_id, Task.status == TaskStatusType.completed)
                )
            )
            pending_tasks = await db.scalar(
                select(func.count(Task.id)).filter(
                    and_(Task.assignee_id == user_id, Task.status == TaskStatusType.pending)
                )
            )
            overdue_tasks = await db.scalar(
                select(func.count(Task.id)).filter(
                    and_(
                        Task.assignee_id == user_id,
                        Task.due_date < datetime.now(),
                        Task.status != TaskStatusType.completed
                    )
                )
            )
            
            # Get total hours logged
            total_minutes = await db.scalar(
                select(func.sum(TimeLog.duration_minutes)).filter(
                    and_(TimeLog.user_id == user_id, TimeLog.end_time.isnot(None))
                )
            )
            total_hours_logged = (total_minutes or 0) / 60.0
            
            # Get current tasks (in progress or pending)
            current_tasks_result = await db.execute(
                select(Task).filter(
                    and_(
                        Task.assignee_id == user_id,
                        Task.status.in_([TaskStatusType.pending, TaskStatusType.in_progress])
                    )
                ).limit(10)
            )
            current_tasks = current_tasks_result.scalars().all()
            
            return UserTaskSummary(
                user_id=user_id,
                user_name=f"{user.first_name} {user.last_name}",
                user_email=user.email,
                user_role=user.role.value,
                total_assigned_tasks=total_tasks or 0,
                completed_tasks=completed_tasks or 0,
                pending_tasks=pending_tasks or 0,
                overdue_tasks=overdue_tasks or 0,
                total_hours_logged=total_hours_logged,
                current_tasks=[]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user task summary for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user task summary"
            )
    
async def create_new_task(task: TaskCreate, db: AsyncSession, author_id: int) -> Task:
    """Create a new task (simplified version without subtasks)."""
    try:
        # Generate slug
        slug = _generate_slug(task.title)
        
        # Create main task
        new_task = Task(
            title=task.title,
            description=task.description or "",
            slug=slug,
            task_type=task.task_type,
            priority=task.priority,
            author_id=author_id,
            assignee_id=task.assignee_id,
            estimated_hours=task.estimated_hours,
            start_date=task.start_date,
            due_date=task.due_date,
            is_public=task.is_public,
            tags=task.tags
        )
        
        db.add(new_task)
        await db.flush()
        await db.commit()
        await db.refresh(new_task)
        
        logger.info(f"Task created successfully: {new_task.id} by user {author_id}")
        return new_task
            
    except SQLAlchemyError as e:
        logger.error(f"Database error creating task: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task due to database error"
        )

async def retrieve_task(task_id: int, user: User, db: AsyncSession) -> Optional[Task]:
    """Retrieve a task by ID."""
    try:
        result = await db.execute(
            select(Task).filter(Task.id == task_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {e}")
        return None

async def retrieve_tasks_by_user(assignee_id: int, db: AsyncSession, skip: int = 0, limit: int = 100, is_ascending: bool = True) -> List[Task]:
    """Retrieve tasks assigned to a user."""
    try:
        order_by = Task.created_at.asc() if is_ascending else Task.created_at.desc()
        result = await db.execute(
            select(Task)
            .filter(Task.assignee_id == assignee_id)
            .order_by(order_by)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {assignee_id}: {e}")
        return []

async def update_task_title(id: int, task_title: str, db: AsyncSession, assignee_id: int) -> Optional[Task]:
    """Update task title."""
    try:
        result = await db.execute(
            select(Task).filter(
                and_(Task.id == id, Task.assignee_id == assignee_id)
            )
        )
        task = result.scalar_one_or_none()
        if task:
            task.title = task_title
            task.slug = _generate_slug(task_title)
            await db.commit()
            await db.refresh(task)
        return task
    except Exception as e:
        logger.error(f"Error updating task title {id}: {e}")
        return None

async def delete_task_by_id(id: int, db: AsyncSession, deleting_user_id: int) -> dict:
    """Delete a task by ID."""
    try:
        result = await db.execute(
            select(Task).filter(Task.id == id)
        )
        task = result.scalar_one_or_none()
        if not task:
            return {"error": "Task not found"}
        
        # Check if user has permission to delete
        if task.author_id != deleting_user_id and task.assignee_id != deleting_user_id:
            return {"error": "Permission denied"}
        
        await db.delete(task)
        await db.commit()
        return {"msg": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task {id}: {e}")
        return {"error": "Database error"}

async def change_task_status(id: int, new_status: TaskStatusType, db: AsyncSession, assignee_id: int) -> Optional[Task]:
    """Change task status."""
    try:
        result = await db.execute(
            select(Task).filter(
                and_(Task.id == id, Task.assignee_id == assignee_id)
            )
        )
        task = result.scalar_one_or_none()
        if task:
            task.status = new_status
            if new_status == TaskStatusType.completed:
                task.completed_at = datetime.now()
            await db.commit()
            await db.refresh(task)
        return task
    except Exception as e:
        logger.error(f"Error changing task status {id}: {e}")
        return None

async def update_task(id: int, task: 'UpdateTask', db: AsyncSession, assignee_id: int) -> Optional[Task]:
    """Update task information."""
    try:
        result = await db.execute(
            select(Task).filter(
                and_(Task.id == id, Task.assignee_id == assignee_id)
            )
        )
        db_task = result.scalar_one_or_none()
        if db_task:
            update_data = task.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(db_task, field) and value is not None:
                    setattr(db_task, field, value)
            await db.commit()
            await db.refresh(db_task)
        return db_task
    except Exception as e:
        logger.error(f"Error updating task {id}: {e}")
        return None

async def assign_task_by_email(task_id: int, assignee_email: str, db: AsyncSession, current_user_id: int) -> Optional[Task]:
    """Assign task to user by email."""
    try:
        # Find user by email
        user_result = await db.execute(
            select(User).filter(User.email == assignee_email)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None
        
        # Update task assignee
        task_result = await db.execute(
            select(Task).filter(Task.id == task_id)
        )
        task = task_result.scalar_one_or_none()
        if task:
            task.assignee_id = user.id
            await db.commit()
            await db.refresh(task)
        return task
    except Exception as e:
        logger.error(f"Error assigning task {task_id}: {e}")
        return None



def _generate_slug(title: str) -> str:
    """Generate a slug from title."""
    import re
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')



# Global instance
task_repository = TaskRepository()

# Convenience functions for backward compatibility
async def create_task_with_subtasks(task_data: TaskCreate, db: AsyncSession, author_id: int) -> Task:
    return await task_repository.create_task_with_subtasks(task_data, db, author_id)

async def get_task_with_details(task_id: int, user: User, db: AsyncSession) -> Optional[Task]:
    return await task_repository.get_task_with_details(task_id, user, db)

async def get_user_tasks(user_id: int, db: AsyncSession, filters: TaskFilter, skip: int = 0, limit: int = 20) -> tuple[List[Task], int]:
    return await task_repository.get_user_tasks(user_id, db, filters, skip, limit)

async def update_task_status(task_id: int, new_status: TaskStatusType, db: AsyncSession, user_id: int) -> Optional[Task]:
    return await task_repository.update_task_status(task_id, new_status, db, user_id)

async def add_subtask(task_id: int, subtask_data: SubtaskCreate, db: AsyncSession, user_id: int) -> Subtask:
    return await task_repository.add_subtask(task_id, subtask_data, db, user_id)

async def start_time_log(time_log_data: TimeLogCreate, db: AsyncSession, user_id: int) -> TimeLog:
    return await task_repository.start_time_log(time_log_data, db, user_id)

async def stop_time_log(time_log_id: int, db: AsyncSession, user_id: int) -> TimeLog:
    return await task_repository.stop_time_log(time_log_id, db, user_id)

async def get_admin_dashboard(db: AsyncSession) -> AdminDashboard:
    return await task_repository.get_admin_dashboard(db)

async def get_user_task_summary(user_id: int, db: AsyncSession) -> UserTaskSummary:
    return await task_repository.get_user_task_summary(user_id, db)

    
    
    
    

    
    