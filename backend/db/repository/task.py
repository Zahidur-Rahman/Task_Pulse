from db.models.task import Task,TaskStatusType
from db.models.user import User
from fastapi import HTTPException
from sqlalchemy.orm import Session 
from schemas.task import TaskCreate,TaskStatuseChange,UpdateTask
from schemas.task import TaskResponse 
from fastapi import status,HTTPException 
from sqlalchemy import case


def create_new_task(task: TaskCreate, db: Session, author_id: int):

    # assignee_id = task.assignee_id if task.assignee_id != 0 else author_id
    new_task = Task(
        task_title=task.task_title,
        slug=task.slug,
        description=task.description,
        is_active=task.is_active,
        assignee_id=author_id,
        author_id=author_id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)



    db.commit()

    return TaskResponse.model_validate(new_task)





def retrieve_task(task_id: int, user: User, db: Session):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .filter((Task.author_id == user.id) | (Task.assignee_id == user.id))  
        .first()
    )
    
    if not task:
        return {"error": "Task not found or you are not authorized to view it."}
    
    return task






def retrieve_tasks_by_user(assignee_id: int, db: Session, skip: int = 0, limit: int = 5,is_ascending:bool=True):
    status_order = ["Pending", "In Progress", "Completed"]   
   
    if not is_ascending:
        status_order = status_order[::-1]
    tasks = db.query(Task).filter(Task.assignee_id == assignee_id).all()
             
    tasks_sorted=sorted(tasks,key=lambda task:status_order.index(task.status))  
    paginated_tasks = tasks_sorted[skip:skip + limit]  
  
    
    return paginated_tasks



def delete_task_by_id(id: int, db: Session, deleting_user_id:int):
    task_in_db = db.query(Task).filter(Task.id == id).first()

    if not task_in_db:
        return {"error": f"Task with id {id} not found"}
    if task_in_db.assignee_id != deleting_user_id:
        return{"error":"Only the assignee can delete this task"}
    db.delete(task_in_db)
    db.commit()
    return {"msg": f"Task with id {id} has been deleted"}

def change_task_status(id: int, new_status: TaskStatusType, db: Session, assignee_id: int):
    task = db.query(Task).filter(Task.id == id, Task.assignee_id == assignee_id).first()
    if not task:
        return None
    task.status = new_status
    db.commit()
    db.refresh(task)
    return task
def update_task_title(id:int,task_title:str,db:Session,assignee_id:int):
    task=db.query(Task).filter(Task.id == id, Task.assignee_id == assignee_id).first()
    if not task:
        return
    
    task.task_title=task_title
    db.commit()
    db.refresh(task)
    return task


def update_task(id:int,task:UpdateTask,db:Session,assignee_id:int):
    task_in_db=db.query(Task).filter(Task.id==id,Task.assignee_id == assignee_id).first()
    if not task_in_db:
        return None
    task_in_db.task_title=task.task_title
    task_in_db.description=task.description
    task_in_db.slug=task.slug
    task_in_db.is_active=task.is_active
    
    db.add(task_in_db)
    db.commit()
    db.refresh(task_in_db)
    return task_in_db

def assign_task_by_email(task_id: int, assignee_email: str, db: Session, current_user_id: int):
    # Fetch the task and ensure it exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None

    
    if task.author_id != current_user_id and task.assignee_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to change the assignee for this task.",
        )

    # Fetch the new assignee by email
    new_assignee = db.query(User).filter(User.email == assignee_email).first()
    if not new_assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee with the provided email not found",
        )

    # Update the task's assignee
    task.assignee_id = new_assignee.id
    task.status="pending"
    db.commit()
    db.refresh(task)
    return task

    
    
    
    

    
    