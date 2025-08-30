import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.session import get_db
from schemas.task import (
    TaskCreate, TaskResponse, TaskAssignment, TaskStatusChange, 
    UpdateTask, AssigneeResponse, PaginatedTaskResponse, TaskTitleResponse
)
from db.repository.task import (
    create_new_task, retrieve_task, retrieve_tasks_by_user, update_task_title,
    delete_task_by_id, change_task_status, update_task, assign_task_by_email
)
from db.models.user import User
from db.models.task import Task
from apis.v1.route_login import get_current_user, get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/", 
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
    description="Create a new task and assign it to a user"
)
async def create_task(
    request: Request,
    task: TaskCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new task.
    
    Args:
        request: FastAPI request object
        task: Task creation data
        db: Async database session
        current_user: Currently authenticated user
        
    Returns:
        Created task information
    """
    try:
        # Log task creation
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Task creation from IP: {client_ip} by user: {current_user.email}")
        
        # Use the enhanced task creation with multiple assignees support
        from db.repository.task import create_task_with_subtasks
        task_obj = await create_task_with_subtasks(task_data=task, db=db, author_id=current_user.id)
        return TaskResponse.model_validate(task_obj)
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating task"
        )


@router.get(
    "/{id}",
    response_model=TaskResponse,
    summary="Get task by ID",
    description="Retrieve a specific task by its ID"
)
async def get_task(
    id: int,
    request: Request,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific task by ID.
    
    Args:
        id: Task ID
        request: FastAPI request object
        user: Currently authenticated user
        db: Async database session
        
    Returns:
        Task information
        
    Raises:
        HTTPException: If task not found
    """
    try:
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Task retrieval request from IP: {client_ip} for task: {id}")
        
        task = await retrieve_task(task_id=id, user=user, db=db)
        if not task:
            logger.warning(f"Task not found: {id}")
            raise HTTPException(
                detail=f"Task with id {id} is not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving task"
        )


@router.get(
    "/assignee/tasks",
    response_model=List[TaskResponse],
    summary="Get user's assigned tasks",
    description="Get list of tasks assigned to the current user"
)
async def get_user_task(
    request: Request,
    assignee: User = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(5, ge=1, le=100, description="Number of records to return"),
    is_ascending: bool = Query(True, description="Sort order (True for ascending, False for descending)")
):
    """
    Get tasks assigned to the current user with pagination.
    
    Args:
        request: FastAPI request object
        assignee: Currently authenticated user
        db: Async database session
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        is_ascending: Sort order
        
    Returns:
        Paginated list of tasks
    """
    try:
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"User tasks request from IP: {client_ip} for user: {assignee.email}")
        
        # Get tasks
        # Get tasks assigned to or authored by the user
        query = select(Task).filter(
            (Task.assignee_id == assignee.id) | (Task.author_id == assignee.id)
        )
        
        if is_ascending:
            query = query.order_by(Task.created_at.asc())
        else:
            query = query.order_by(Task.created_at.desc())
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # Get total count for pagination
        count_result = await db.execute(
            select(func.count(Task.id)).filter(
                (Task.assignee_id == assignee.id) | (Task.author_id == assignee.id)
            )
        )
        total_count = count_result.scalar()
        
        logger.info(f"Retrieved {len(tasks)} tasks for user {assignee.email}")
        
        # Convert to TaskResponse objects with proper error handling
        task_responses = []
        for task in tasks:
            try:
                # Ensure all required fields are present
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
                    'updated_at': task.updated_at or task.created_at,  # Fallback for null updated_at
                    'progress_percentage': task.progress_percentage,
                    'is_overdue': task.is_overdue
                }
                task_response = TaskResponse.model_validate(task_dict)
                task_responses.append(task_response)
            except Exception as e:
                logger.error(f"Error converting task {task.id} to TaskResponse: {e}")
                continue
        
        return task_responses
        
    except Exception as e:
        logger.error(f"Error retrieving user tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving tasks"
        )


@router.delete(
    "/{task_id}",
    summary="Delete task",
    description="Delete a task by ID"
)
async def delete_a_task(
    request: Request,
    task_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a task.
    
    Args:
        request: FastAPI request object
        task_id: ID of the task to delete
        db: Async database session
        current_user: Currently authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        # Log deletion attempt
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Task deletion attempt from IP: {client_ip} for task: {task_id}")
        
        message = await delete_task_by_id(id=task_id, db=db, deleting_user_id=current_user.id)
        if message.get("error"):
            logger.warning(f"Task deletion failed: {message.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=message.get("error")
            )
        
        logger.info(f"Task {task_id} deleted successfully by user {current_user.email}")
        return {"msg": message.get("msg")}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting task"
        )


@router.put(
    "/status/{task_id}", 
    response_model=TaskResponse,
    summary="Update task status",
    description="Update the status of a specific task"
)
async def update_a_task_status(
    request: Request,
    task_id: int,
    status_update: TaskStatusChange,
    db: AsyncSession = Depends(get_db), 
    assignee_user: User = Depends(get_current_active_user)
):
    """
    Update task status.
    
    Args:
        request: FastAPI request object
        task_id: ID of the task
        status_update: New status information
        db: Async database session
        assignee_user: Currently authenticated user
        
    Returns:
        Updated task information
        
    Raises:
        HTTPException: If update fails
    """
    try:
        # Log status update
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Task status update from IP: {client_ip} for task: {task_id}")
        
        task = await change_task_status(
            id=task_id,
            new_status=status_update.status,
            db=db,
            assignee_id=assignee_user.id
        )

        if not task:
            logger.warning(f"Task status update failed for task: {task_id}")
            raise HTTPException( 
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found or this task is assigned to another user"
            )
        
        logger.info(f"Task {task_id} status updated to {status_update.status}")
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task status for task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating task status"
        )


@router.put(
    "/{task_id}", 
    response_model=TaskResponse,
    summary="Update task",
    description="Update task information"
)
async def update_a_task(
    request: Request,
    task_id: int,
    task: UpdateTask,
    db: AsyncSession = Depends(get_db), 
    assignee_user: User = Depends(get_current_active_user)
):
    """
    Update task information.
    
    Args:
        request: FastAPI request object
        task_id: ID of the task
        task: Updated task data
        db: Async database session
        assignee_user: Currently authenticated user
        
    Returns:
        Updated task information
        
    Raises:
        HTTPException: If update fails
    """
    try:
        # Log task update
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Task update from IP: {client_ip} for task: {task_id}")
        
        updated_task = await update_task(
            id=task_id,
            task=task,
            db=db,
            assignee_id=assignee_user.id
        )

        if not updated_task:
            logger.warning(f"Task update failed for task: {task_id}")
            raise HTTPException( 
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found or you are not authorized to update it"
            )
        
        logger.info(f"Task {task_id} updated successfully")
        return updated_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating task"
        )


@router.put(
    "/task_title/{task_id}", 
    response_model=TaskTitleResponse,
    summary="Update task title",
    description="Update only the title of a specific task"
)
async def update_task_title_only(
    request: Request,
    task_id: int,
    task_title: str,
    db: AsyncSession = Depends(get_db), 
    assignee_user: User = Depends(get_current_active_user)
):
    """
    Update task title.
    
    Args:
        request: FastAPI request object
        task_id: ID of the task
        task_title: New task title
        db: Async database session
        assignee_user: Currently authenticated user
        
    Returns:
        Updated task title information
        
    Raises:
        HTTPException: If update fails
    """
    try:
        # Log title update
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Task title update from IP: {client_ip} for task: {task_id}")
        
        task = await update_task_title(
            id=task_id,
            task_title=task_title,
            db=db,
            assignee_id=assignee_user.id
        )

        if not task:
            logger.warning(f"Task title update failed for task: {task_id}")
            raise HTTPException( 
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found or you are not authorized to update it"
            )
        
        logger.info(f"Task {task_id} title updated successfully")
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task title for task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating task title"
        )


@router.put(
    "/change_assignee/{task_id}", 
    response_model=TaskResponse,
    summary="Change task assignee",
    description="Reassign a task to a different user"
)
async def change_assignee(
    request: Request,
    task_assignment: TaskAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change task assignee.
    
    Args:
        request: FastAPI request object
        task_assignment: Task assignment data
        db: Async database session
        current_user: Currently authenticated user
        
    Returns:
        Updated task information
        
    Raises:
        HTTPException: If reassignment fails
    """
    try:
        # Log assignee change
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"Task assignee change from IP: {client_ip} for task: {task_assignment.task_id}")
        
        updated_task = await assign_task_by_email(
            task_id=task_assignment.task_id,
            assignee_email=task_assignment.assignee_email,
            db=db,
            current_user_id=current_user.id
        )
        
        if not updated_task:
            logger.warning(f"Task assignee change failed for task: {task_assignment.task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or could not be reassigned"
            )
        
        logger.info(f"Task {task_assignment.task_id} reassigned successfully")
        return updated_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing task assignee for task {task_assignment.task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while changing task assignee"
        )

