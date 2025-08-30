from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from db.session import get_db
from apis.v1.route_login import get_current_active_user
from db.models.user import User
from db.repository.task import get_user_task_summary, get_user_tasks
from schemas.task import (
    TaskFilter, UserTaskSummary, TaskCreate, SubtaskCreate, 
    TimeLogCreate, TimeLogUpdate, TaskCommentCreate
)
from schemas.user import UserDashboard, UserProfile

router = APIRouter()

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's profile with task statistics."""
    return await get_user_task_summary(current_user.id, db)

@router.get("/dashboard", response_model=UserDashboard)
async def get_user_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive user dashboard data."""
    try:
        from db.repository.task import task_repository
        from schemas.task import TimeLogResponse
        from schemas.user import UserProfile
        
        # Get user task summary
        user_task_summary = await get_user_task_summary(current_user.id, db)
        
        # Create UserProfile object from current_user and task summary
        user_profile = UserProfile(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            role=current_user.role,
            organization_id=current_user.organization_id,
            is_active=current_user.is_active,
            created_tasks_count=user_task_summary.total_assigned_tasks,
            assigned_tasks_count=user_task_summary.total_assigned_tasks,
            completed_tasks_count=user_task_summary.completed_tasks,
            total_hours_logged=user_task_summary.total_hours_logged
        )
        
        # Get recent tasks
        filters = TaskFilter()
        recent_tasks, _ = await get_user_tasks(current_user.id, db, filters, skip=0, limit=5)
        
        # Get upcoming deadlines (tasks due in next 7 days)
        upcoming_filters = TaskFilter(
            due_date_from=datetime.now(),
            due_date_to=datetime.now() + timedelta(days=7)
        )
        upcoming_tasks, _ = await get_user_tasks(current_user.id, db, upcoming_filters, skip=0, limit=5)
        
        # Get today's time logs
        from sqlalchemy import select, and_, func
        from db.models.task import TimeLog
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        time_logs_result = await db.execute(
            select(TimeLog).filter(
                and_(
                    TimeLog.user_id == current_user.id,
                    TimeLog.start_time >= today_start,
                    TimeLog.start_time < today_end
                )
            )
        )
        time_logs_today = time_logs_result.scalars().all()
        
        # Get this week's total hours
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        week_hours_result = await db.execute(
            select(func.sum(TimeLog.duration_minutes)).filter(
                and_(
                    TimeLog.user_id == current_user.id,
                    TimeLog.start_time >= week_start,
                    TimeLog.end_time.is_not(None)
                )
            )
        )
        total_minutes_this_week = week_hours_result.scalar() or 0
        total_hours_this_week = total_minutes_this_week / 60.0
        
        # Convert tasks to proper response format
        from schemas.task import TaskResponse
        
        recent_task_responses = []
        for task in recent_tasks:
            try:
                task_dict = {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description or "",
                    'slug': task.slug,
                    'task_type': task.task_type,
                    'priority': task.priority,
                    'status': task.status,
                    'author_id': task.author_id,
                    'assignee_id': task.assignee_id,
                    'estimated_hours': task.estimated_hours,
                    'actual_hours': task.actual_hours,
                    'start_date': task.start_date,
                    'due_date': task.due_date,
                    'completed_at': task.completed_at,
                    'is_active': task.is_active,
                    'is_public': task.is_public,
                    'tags': task.tags,
                    'created_at': task.created_at,
                    'updated_at': task.updated_at or task.created_at,
                    'progress_percentage': task.progress_percentage,
                    'is_overdue': task.is_overdue
                }
                recent_task_responses.append(TaskResponse.model_validate(task_dict))
            except Exception:
                continue
        
        upcoming_task_responses = []
        for task in upcoming_tasks:
            try:
                task_dict = {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description or "",
                    'slug': task.slug,
                    'task_type': task.task_type,
                    'priority': task.priority,
                    'status': task.status,
                    'author_id': task.author_id,
                    'assignee_id': task.assignee_id,
                    'estimated_hours': task.estimated_hours,
                    'actual_hours': task.actual_hours,
                    'start_date': task.start_date,
                    'due_date': task.due_date,
                    'completed_at': task.completed_at,
                    'is_active': task.is_active,
                    'is_public': task.is_public,
                    'tags': task.tags,
                    'created_at': task.created_at,
                    'updated_at': task.updated_at or task.created_at,
                    'progress_percentage': task.progress_percentage,
                    'is_overdue': task.is_overdue
                }
                upcoming_task_responses.append(TaskResponse.model_validate(task_dict))
            except Exception:
                continue

        # Convert time logs to proper response format
        from schemas.task import TimeLogResponse
        
        time_log_responses = []
        for log in time_logs_today:
            try:
                log_dict = {
                    'id': log.id,
                    'user_id': log.user_id,
                    'task_id': log.task_id,
                    'subtask_id': log.subtask_id,
                    'start_time': log.start_time,
                    'end_time': log.end_time,
                    'duration_minutes': log.duration_minutes,
                    'description': log.description,
                    'created_at': log.created_at,
                    'is_active': log.is_active,
                    'duration_hours': log.duration_hours
                }
                time_log_responses.append(TimeLogResponse.model_validate(log_dict))
            except Exception:
                continue

        return UserDashboard(
            user=user_profile,
            recent_tasks=recent_task_responses,
            upcoming_deadlines=upcoming_task_responses,
            time_logs_today=time_log_responses,
            total_hours_this_week=round(total_hours_this_week, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard: {str(e)}"
        )

@router.get("/tasks", response_model=List[dict])
async def get_user_tasks_dashboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_overdue: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's tasks with filtering and pagination."""
    try:
        from db.models.task import TaskStatusType, TaskPriority, TaskType
        
        # Convert string filters to enums
        status_enum = TaskStatusType(status) if status else None
        priority_enum = TaskPriority(priority) if priority else None
        task_type_enum = TaskType(task_type) if task_type else None
        
        filters = TaskFilter(
            status=status_enum,
            priority=priority_enum,
            task_type=task_type_enum,
            search=search,
            is_overdue=is_overdue
        )
        
        tasks, total = await get_user_tasks(current_user.id, db, filters, skip, limit)
        
        # Convert to response format
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "progress_percentage": task.progress_percentage,
                "is_overdue": task.is_overdue,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "subtasks_count": len(task.subtasks),
                "completed_subtasks_count": len([s for s in task.subtasks if s.status == "Completed"])
            })
        
        return {
            "tasks": task_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )

@router.post("/tasks", response_model=dict)
async def create_user_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task (user can create tasks for themselves)."""
    try:
        from db.repository.task import create_task_with_subtasks
        
        # Ensure user is creating task for themselves
        if task_data.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only create tasks for yourself"
            )
        
        task = await create_task_with_subtasks(task_data, db, current_user.id)
        
        return {
            "message": "Task created successfully",
            "task_id": task.id,
            "title": task.title
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

@router.post("/tasks/{task_id}/subtasks", response_model=dict)
async def add_subtask_to_task(
    task_id: int,
    subtask_data: SubtaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a subtask to an existing task."""
    try:
        from db.repository.task import add_subtask
        
        subtask = await add_subtask(task_id, subtask_data, db, current_user.id)
        
        return {
            "message": "Subtask added successfully",
            "subtask_id": subtask.id,
            "title": subtask.title
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add subtask: {str(e)}"
        )

@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: int,
    status_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update task status."""
    try:
        from db.repository.task import update_task_status
        from db.models.task import TaskStatusType
        
        new_status = TaskStatusType(status_update.get("status"))
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status provided"
            )
        
        task = await update_task_status(task_id, new_status, db, current_user.id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or access denied"
            )
        
        return {
            "message": f"Task status updated to {new_status}",
            "task_id": task.id,
            "new_status": task.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task status: {str(e)}"
        )

@router.post("/time-logs/start", response_model=dict)
async def start_time_logging(
    time_log_data: TimeLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Start time logging for a task or subtask."""
    try:
        from db.repository.task import start_time_log
        
        time_log = await start_time_log(time_log_data, db, current_user.id)
        
        return {
            "message": "Time logging started",
            "time_log_id": time_log.id,
            "start_time": time_log.start_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start time logging: {str(e)}"
        )

@router.put("/time-logs/{time_log_id}/stop", response_model=dict)
async def stop_time_logging(
    time_log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop time logging."""
    try:
        from db.repository.task import stop_time_log
        
        time_log = await stop_time_log(time_log_id, db, current_user.id)
        
        return {
            "message": "Time logging stopped",
            "time_log_id": time_log.id,
            "duration_minutes": time_log.duration_minutes,
            "duration_hours": round(time_log.duration_hours, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop time logging: {str(e)}"
        )

@router.get("/time-logs", response_model=List[dict])
async def get_user_time_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    task_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's time logs with filtering."""
    try:
        from sqlalchemy import select, and_
        from db.models.task import TimeLog
        
        query = select(TimeLog).filter(TimeLog.user_id == current_user.id)
        
        if task_id:
            query = query.filter(TimeLog.task_id == task_id)
        if start_date:
            query = query.filter(TimeLog.start_time >= start_date)
        if end_date:
            query = query.filter(TimeLog.start_time <= end_date)
        
        # Get total count
        from sqlalchemy import func
        count_query = select(func.count(TimeLog.id)).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(TimeLog.start_time.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        time_logs = result.scalars().all()
        
        # Convert to response format
        time_log_list = []
        for log in time_logs:
            time_log_list.append({
                "id": log.id,
                "task_id": log.task_id,
                "subtask_id": log.subtask_id,
                "start_time": log.start_time.isoformat(),
                "end_time": log.end_time.isoformat() if log.end_time else None,
                "duration_minutes": log.duration_minutes,
                "duration_hours": round(log.duration_hours, 2),
                "description": log.description,
                "is_active": log.is_active
            })
        
        return {
            "time_logs": time_log_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve time logs: {str(e)}"
        )

@router.get("/analytics/personal")
async def get_personal_analytics(
    period: str = Query("week", regex="^(day|week|month|year)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personal analytics for the specified period."""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import select, func, and_
        from db.models.task import Task, TimeLog
        
        # Calculate date range
        end_date = datetime.now()
        if period == "day":
            start_date = end_date - timedelta(days=1)
        elif period == "week":
            start_date = end_date - timedelta(weeks=1)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:  # year
            start_date = end_date - timedelta(days=365)
        
        # Tasks assigned in period
        tasks_assigned = await db.execute(
            select(func.count(Task.id)).filter(
                and_(
                    Task.assignee_id == current_user.id,
                    Task.created_at >= start_date,
                    Task.created_at <= end_date
                )
            )
        )
        total_tasks_assigned = tasks_assigned.scalar()
        
        # Tasks completed in period
        tasks_completed = await db.execute(
            select(func.count(Task.id)).filter(
                and_(
                    Task.assignee_id == current_user.id,
                    Task.completed_at >= start_date,
                    Task.completed_at <= end_date
                )
            )
        )
        total_tasks_completed = tasks_completed.scalar()
        
        # Hours logged in period
        hours_logged = await db.execute(
            select(func.sum(TimeLog.duration_minutes)).filter(
                and_(
                    TimeLog.user_id == current_user.id,
                    TimeLog.start_time >= start_date,
                    TimeLog.start_time <= end_date,
                    TimeLog.end_time.is_not(None)
                )
            )
        )
        total_hours = (hours_logged.scalar() or 0) / 60.0
        
        # Average task completion time
        completion_times = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', Task.completed_at - Task.created_at) / 3600
                )
        ).filter(
            and_(
                Task.assignee_id == current_user.id,
                Task.completed_at >= start_date,
                Task.completed_at <= end_date,
                Task.completed_at.is_not(None)
            )
        ))
        avg_completion_hours = completion_times.scalar() or 0
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "tasks_assigned": total_tasks_assigned,
            "tasks_completed": total_tasks_completed,
            "completion_rate": (total_tasks_completed / total_tasks_assigned * 100) if total_tasks_assigned > 0 else 0,
            "hours_logged": round(total_hours, 2),
            "avg_completion_hours": round(avg_completion_hours, 2)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}"
        ) 