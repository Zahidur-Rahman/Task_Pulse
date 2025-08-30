from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from db.base_class import Base
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class AsyncRepository(Generic[ModelType]):
    """
    Base async repository class providing common CRUD operations.
    
    Generic type parameter should be a SQLAlchemy model class.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with a specific model.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Async database session
            id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        try:
            result = await db.execute(select(self.model).filter(self.model.id == id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} with id {id}: {e}")
            raise
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and optional filtering.
        
        Args:
            db: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional dictionary of field filters
            
        Returns:
            List of model instances
        """
        try:
            query = select(self.model).offset(skip).limit(limit)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)
            
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            raise
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Async database session
            obj_in: Dictionary of field values
            
        Returns:
            Created model instance
        """
        try:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            await db.rollback()
            raise
    
    async def update(
        self, 
        db: AsyncSession, 
        id: Any, 
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update an existing record.
        
        Args:
            db: Async database session
            id: Record ID
            obj_in: Dictionary of field values to update
            
        Returns:
            Updated model instance or None if not found
        """
        try:
            result = await db.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**obj_in)
                .returning(self.model)
            )
            updated_obj = result.scalar_one_or_none()
            
            if updated_obj:
                await db.commit()
                return updated_obj
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} with id {id}: {e}")
            await db.rollback()
            raise
    
    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """
        Delete a record by ID.
        
        Args:
            db: Async database session
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            result = await db.execute(
                delete(self.model).where(self.model.id == id)
            )
            
            if result.rowcount > 0:
                await db.commit()
                return True
            return False
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            await db.rollback()
            raise
    
    async def count(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering.
        
        Args:
            db: Async database session
            filters: Optional dictionary of field filters
            
        Returns:
            Number of records
        """
        try:
            query = select(self.model)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)
            
            result = await db.execute(query)
            return len(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise
    
    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """
        Check if a record exists by ID.
        
        Args:
            db: Async database session
            id: Record ID
            
        Returns:
            True if exists, False otherwise
        """
        try:
            result = await db.execute(select(self.model.id).filter(self.model.id == id))
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {id}: {e}")
            raise 