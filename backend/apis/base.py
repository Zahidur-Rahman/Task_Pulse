from apis.v1 import route_user
from apis.v1 import route_task
from apis.v1 import route_login
from fastapi import APIRouter



api_router=APIRouter()

api_router.include_router(route_user.router,prefix="/user",tags=["user"])
api_router.include_router(route_task.router,prefix="/task",tags=["task"])
api_router.include_router(route_login.router,prefix="/login",tags=["login"])