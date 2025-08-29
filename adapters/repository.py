from typing import TypeVar, Generic, List, Optional, Type
from abc import abstractmethod, ABC
from sqlalchemy.orm import Session

T = TypeVar('T')


class AbstractRepository(ABC, Generic[T]):
    """Abstract Repository for CRUD operations."""
    
    @abstractmethod
    def add(self, entity: T) -> T:
        """Add a new entity to the repository."""
        ...
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve an entity by its ID."""
        ...
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all entities from the repository."""
        ...
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity in the repository."""
        ...
    
    @abstractmethod
    def delete_by_id(self, entity_id: int) -> bool:
        """Delete an entity by its ID. Returns True if successful."""
        ...


class BaseSqlAlchemyRepository(AbstractRepository[T]):
    """Base SQLAlchemy repository implementation."""
    
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    def add(self, entity: T) -> T:
        """Add a new entity to the repository."""
        self.session.add(entity)
        self.session.flush()  # populate entity.id immediately
        # we will commit the transaction at the service level 
        # to allow for grouping multiple operations        
        return entity
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve an entity by its ID."""
        return self.session.query(self.model_class).filter_by(id=entity_id).first()
    
    def get_all(self) -> List[T]:
        """Retrieve all entities from the repository."""
        return self.session.query(self.model_class).all()
    
    def update(self, entity: T) -> T:
        """Update an existing entity in the repository."""
        self.session.merge(entity)
        # we will commit the transaction at the service level 
        # to allow for grouping multiple operations
        return entity
    
    def delete_by_id(self, entity_id: int) -> bool:
        """Delete an entity by its ID. Returns True if successful."""
        deleted_count = self.session.query(self.model_class).filter_by(id=entity_id).delete(
            synchronize_session='fetch'
        )
        # we will commit the transaction at the service level 
        # to allow for grouping multiple operations
        return deleted_count > 0