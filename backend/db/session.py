from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

from typing import Generator


SQLALCHEMY_DATABASE=settings.DATABASE_URL
print("DATABASE URL IS ",SQLALCHEMY_DATABASE)

engine=create_engine(SQLALCHEMY_DATABASE)
SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)


def get_db()->Generator:
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()    


