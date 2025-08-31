from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta

from db.session import get_db
from apis.v1.route_login import get_current_active_user
from db.models.user import User, UserRole
from db.models.task import Task
from db.repository.task import get_admin_dashboard, get_user_task_summary, create_task_with_subtasks
from db.repository.user import user_repository
from schemas.task import AdminDashboard, UserTaskSummary, TaskCreate, TaskResponse
from schemas.user import UserResponse, UserUpdate, UserCreate
from core.hashing import Hasher

router = APIRouter()

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure the current user is an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_current_super_admin_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Ensure the current user is a super admin (first admin created)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if this is the first admin (super admin)
    db_session = db
    admin_count = await db_session.execute(
        select(func.count(User.id)).filter(User.role == UserRole.admin)
    )
    total_admins = admin_count.scalar()
    
    if total_admins == 1 and current_user.role == UserRole.admin:
        return current_user  # This is the super admin
    elif total_admins > 1:
        # For multiple admins, check if they can promote others
        if current_user.role == UserRole.admin:
            return current_user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin access required for user management"
            )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Super admin access required"
    )

@router.post("/setup", response_model=UserResponse)
async def setup_first_admin(
    admin_data: UserCreate,
    setup_token: str = Query(..., description="Setup token for first admin creation"),
    db: AsyncSession = Depends(get_db)
):
    """Setup the first admin user (system initialization)."""
    try:
        # Verify setup token (you can store this in environment variables)
        expected_token = "TASK_PULSE_SETUP_2024"  # In production, use environment variable
        if setup_token != expected_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid setup token"
            )
        
        # Check if any admin already exists
        existing_admin = await db.execute(
            select(User).filter(User.role == UserRole.admin)
        )
        if existing_admin.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin already exists. Use regular admin creation."
            )
        
        # Create the first admin
        admin_data.role = UserRole.admin
        admin = await user_repository.create_new_user(admin_data, db)
        
        return admin
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup admin: {str(e)}"
        )

@router.post("/promote/{user_id}", response_model=UserResponse)
async def promote_user_to_admin(
    user_id: int,
    promotion_code: str = Query(..., description="Promotion code for admin access"),
    current_user: User = Depends(get_current_super_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Promote an existing user to admin role."""
    try:
        # Verify promotion code
        expected_code = "ADMIN_PROMOTION_2024"  # In production, use environment variable
        if promotion_code != expected_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid promotion code"
            )
        
        # Get the user to promote
        user = await user_repository.get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.role == UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already an admin"
            )
        
        # Promote user to admin
        update_data = {"role": UserRole.admin}
        promoted_user = await user_repository.update_user(user_id, update_data, db)
        
        return promoted_user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to promote user: {str(e)}"
        )

@router.post("/register", response_model=UserResponse)
async def register_admin_directly(
    admin_data: UserCreate,
    admin_registration_code: str = Query(..., description="Admin registration code"),
    db: AsyncSession = Depends(get_db)
):
    """Register a new admin user directly (requires special code)."""
    try:
        # Verify admin registration code
        expected_code = "DIRECT_ADMIN_REG_2024"  # In production, use environment variable
        if admin_registration_code != expected_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin registration code"
            )
        
        # Set role to admin
        admin_data.role = UserRole.admin
        
        # Create admin user
        admin = await user_repository.create_new_user(admin_data, db)
        
        return admin
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register admin: {str(e)}"
        )

@router.get("/dashboard", response_model=AdminDashboard)
async def get_admin_dashboard_endpoint(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive admin dashboard data."""
    from db.repository.task import get_admin_dashboard
    return await get_admin_dashboard(db)

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users with filtering and pagination."""
    try:
        users = await user_repository.get_all_users_with_filters(
            db, skip, limit, role, is_active, search
        )
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.get("/users/{user_id}/summary", response_model=UserTaskSummary)
async def get_user_task_summary(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive task summary for a specific user."""
    return await get_user_task_summary(user_id, db)

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user information (admin only)."""
    try:
        updated_user = await user_repository.update_user(user_id, user_update.dict(exclude_unset=True), db)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a user (admin only)."""
    try:
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate yourself"
            )
        
        success = await user_repository.deactivate_user(user_id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": f"User {user_id} has been deactivated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )

@router.get("/users/{user_id}/tasks")
async def get_user_tasks_admin(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    priority_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks for a specific user (admin view)."""
    try:
        from schemas.task import TaskFilter
        from db.repository.task import get_user_tasks
        
        filters = TaskFilter(
            status=status_filter,
            priority=priority_filter
        )
        
        tasks, total = await get_user_tasks(user_id, db, filters, skip, limit)
        
        return {
            "tasks": tasks,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user tasks: {str(e)}"
        )

@router.get("/analytics/overview")
async def get_analytics_overview(
    period: str = Query("week", regex="^(day|week|month|year)$"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics overview for the specified period."""
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
        
        # Tasks created in period
        tasks_created = await db.execute(
            select(func.count(Task.id)).filter(
                and_(Task.created_at >= start_date, Task.created_at <= end_date)
            )
        )
        total_tasks_created = tasks_created.scalar()
        
        # Tasks completed in period
        tasks_completed = await db.execute(
            select(func.count(Task.id)).filter(
                and_(Task.completed_at >= start_date, Task.completed_at <= end_date)
            )
        )
        total_tasks_completed = tasks_completed.scalar()
        
        # Hours logged in period
        hours_logged = await db.execute(
            select(func.sum(TimeLog.duration_minutes)).filter(
                and_(
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
            "tasks_created": total_tasks_created,
            "tasks_completed": total_tasks_completed,
            "completion_rate": (total_tasks_completed / total_tasks_created * 100) if total_tasks_created > 0 else 0,
            "hours_logged": round(total_hours, 2),
            "avg_completion_hours": round(avg_completion_hours, 2)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )

@router.get("/reports/user-performance")
async def get_user_performance_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user performance report for the specified period."""
    try:
        from sqlalchemy import select, func, and_, desc
        from db.models.task import Task, TimeLog
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get user performance data
        performance_query = select(
            User.id,
            User.first_name,
            User.last_name,
            User.role,
            func.count(Task.id).label('total_tasks'),
            func.count(Task.id).filter(Task.status == "Completed").label('completed_tasks'),
            func.sum(TimeLog.duration_minutes).label('total_minutes')
        ).outerjoin(
            Task, User.id == Task.assignee_id
        ).outerjoin(
            TimeLog, User.id == TimeLog.user_id
        ).filter(
            and_(
                Task.created_at >= start_date,
                Task.created_at <= end_date
            )
        ).group_by(
            User.id, User.first_name, User.last_name, User.role
        ).order_by(desc('completed_tasks'))
        
        result = await db.execute(performance_query)
        performance_data = []
        
        for row in result:
            total_hours = (row[6] or 0) / 60.0
            completion_rate = (row[5] / row[4] * 100) if row[4] > 0 else 0
            
            performance_data.append({
                "user_id": row[0],
                "user_name": f"{row[1]} {row[2]}",
                "role": row[3],
                "total_tasks": row[4],
                "completed_tasks": row[5],
                "completion_rate": round(completion_rate, 2),
                "total_hours_logged": round(total_hours, 2)
            })
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "performance_data": performance_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance report: {str(e)}"
        )

@router.get("/tasks", response_model=List[TaskResponse])
async def get_all_tasks_admin(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by task status"),
    priority_filter: Optional[str] = Query(None, description="Filter by task priority"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks in the system (admin only)."""
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        from sqlalchemy.orm import selectinload
        
        # First, let's check if there are any tasks at all
        count_query = select(func.count(Task.id))
        count_result = await db.execute(count_query)
        total_tasks = count_result.scalar()
        logger.info(f"Total tasks in database: {total_tasks}")
        
        # Build query to get all tasks with assignee information
        query = select(Task).options(
            selectinload(Task.assignee),
            selectinload(Task.author)
        )
        
        # Apply filters if provided
        if status_filter:
            query = query.filter(Task.status == status_filter)
            logger.info(f"Applied status filter: {status_filter}")
        if priority_filter:
            query = query.filter(Task.priority == priority_filter)
            logger.info(f"Applied priority filter: {priority_filter}")
            
        # Apply pagination and ordering
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        logger.info(f"Query parameters - skip: {skip}, limit: {limit}")
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        logger.info(f"Retrieved {len(tasks)} tasks for admin")
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error retrieving all tasks for admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )

@router.post("/tasks", response_model=TaskResponse)
async def create_task_for_user(
    task: TaskCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a task and assign it to a user (admin only)."""
    try:
        # Verify that the assignee exists
        assignee = await user_repository.get_user_by_id(task.assignee_id, db)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee user not found"
            )
        
        # Verify additional assignees if provided
        if task.assignee_ids:
            for assignee_id in task.assignee_ids:
                user = await user_repository.get_user_by_id(assignee_id, db)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User with ID {assignee_id} not found"
                    )
        
        # Create the task with admin as author
        task_obj = await create_task_with_subtasks(
            task_data=task, 
            db=db, 
            author_id=current_user.id
        )
        
        return TaskResponse.model_validate(task_obj)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        ) 