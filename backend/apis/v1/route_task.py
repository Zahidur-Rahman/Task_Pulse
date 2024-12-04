from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.task import TaskCreate, TaskResponse,TaskAssignment,TaskStatuseChange,UpdateTask,AssigneeResponse,PaginatedTaskResponse,TaskTitleResponse
from db.repository.task import create_new_task,retrieve_task,retrieve_tasks_by_user,update_task_title
from db.repository.task import delete_task_by_id,change_task_status,update_task,assign_task_by_email
from db.models.user import User
from apis.v1.route_login import get_current_user 
from db.models.task import Task


router = APIRouter()

@router.post("/", response_model=TaskResponse,status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    task_obj = create_new_task(task=task, db=db, author_id=current_user.id)
    return TaskResponse.model_validate(task_obj) 


@router.get("/{id}",response_model=TaskResponse)
def get_task(id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    task=retrieve_task(task_id=id,user=user,db=db)
    if not task:
        raise HTTPException(detail=f"Task with id {id} is not found",status_code=status.HTTP_404_NOT_FOUND)
    
    return task


@router.get("/assignee/tasks",response_model=PaginatedTaskResponse)
def get_user_task(assignee:User=Depends(get_current_user), db:Session=Depends(get_db),skip:int=0,limit:int=5, is_ascending: bool = True):
    tasks=retrieve_tasks_by_user(assignee_id=assignee.id,db=db,skip=skip,limit=limit,is_ascending=is_ascending)
    total = db.query(Task).filter(Task.assignee_id == assignee.id).count()
    return PaginatedTaskResponse(tasks=tasks,total=total,skip=skip,limit=limit)

@router.delete("/{task_id}")
def delete_a_task(task_id: int, db: Session = Depends(get_db) ,current_user : User=Depends(get_current_user)):
    message = delete_task_by_id(id=task_id, db=db, deleting_user_id=current_user.id)
    if message.get("error"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message.get("error"))
    
    return {"msg": message.get("msg")}

@router.put("/status/{task_id}", response_model=TaskResponse)
def update_a_task_status(task_id:int,status_update:TaskStatuseChange,db:Session=Depends(get_db), assignee_user:User=Depends(get_current_user)):
    task=change_task_status(id=task_id,new_status=status_update.status,db=db,assignee_id=assignee_user.id)

    if not task:
            raise HTTPException( 
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Task with id {task_id} not found or this task is assigned with another one"
             )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_a_task(task_id:int,task:UpdateTask,db:Session=Depends(get_db), assignee_user:User=Depends(get_current_user)):
    task=update_task(id=task_id,task=task,db=db,assignee_id=assignee_user.id)

    if not task:
            raise HTTPException( 
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Task with id {task_id} not found or"
             )
    return task
@router.put("/task_title/{task_id}", response_model=TaskTitleResponse)
def update_a_task(task_id:int,task_title:str,db:Session=Depends(get_db), assignee_user:User=Depends(get_current_user)):
    task=update_task_title(id=task_id,task_title=task_title,db=db,assignee_id=assignee_user.id)

    if not task:
            raise HTTPException( 
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Task with id {task_id} not found or"
             )
    return task


@router.put("/change_assignee/{task_id}", response_model=TaskResponse)

def change_assignee(task_assignment: TaskAssignment,db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):

    updated_task = assign_task_by_email(task_id=task_assignment.task_id,assignee_email=task_assignment.assignee_email,db=db,current_user_id=current_user.id)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or could not be reassigned",
        )
    return updated_task

