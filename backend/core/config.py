import os
from dotenv import load_dotenv
from pathlib import Path


env_path=Path('.')/'.env'
load_dotenv(dotenv_path=env_path)



class Settings:
    PROJECT_TITLE:str="Task Management"
    PROJECT_VERSION:str="0.1.0"

    POSTGRES_USER:str=os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD:str=os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER:str=os.getenv("POSTGRES_SERVER","localhost")
    POSTGRES_PORT:int=os.getenv("POSTGRES_PORT",5432)
    POSTGRESS_DB:str=os.getenv("POSTGRES_DB")
    DATABASE_URL:str=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRESS_DB}"
    SECRET_KEY:str=os.getenv("SUPER_SECRET")
    ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int=30

settings=Settings()

