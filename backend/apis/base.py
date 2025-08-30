from fastapi import APIRouter
from apis.v1 import route_login, route_user, route_task, route_admin, route_dashboard

api_router = APIRouter()

api_router.include_router(route_login.router, prefix="/login", tags=["login"])
api_router.include_router(route_user.router, prefix="/user", tags=["users"])
api_router.include_router(route_task.router, prefix="/task", tags=["tasks"])
api_router.include_router(route_admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(route_dashboard.router, tags=["dashboard"])