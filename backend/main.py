from db.session import engine
from db.base_class import Base
from fastapi import FastAPI
from core.config import settings
from apis.base import api_router
from fastapi.middleware.cors import CORSMiddleware

def include_router(app):
    app.include_router(api_router)

def start_application():
    app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)
    include_router(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3001"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = start_application()
