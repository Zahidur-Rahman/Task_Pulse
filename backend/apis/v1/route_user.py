from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.models.task import Task
from db.models.user import User
from apis.v1.route_login import get_current_user


from db.session import get_db
from schemas.user import UserCreate,ShowUser,UserResponse
from db.repository.user import create_new_user


router=APIRouter()

@router.post('/',response_model=ShowUser,status_code=status.HTTP_201_CREATED)
def create_user(user:UserCreate,db:Session=Depends(get_db)):
    user=create_new_user(user=user,db=db)
    return user


@router.get('/available-assignees/{task_id}',response_model=List[UserResponse])
def get_available_assignees(task_id: int, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    # Fetch the task by ID to get the current assignee
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.author_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view available assignees for this task."
        )
    

    available_assignees = db.query(User).filter(User.id != task.assignee_id).all()
    
    return available_assignees



