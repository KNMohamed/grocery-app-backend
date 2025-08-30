from adapters.repository import AbstractRepository
from service_layer.services import GroceryListService
from typing import List, Optional
from domain.models import GroceryList


class FakeGroceryListRepository(AbstractRepository[GroceryList]):
    """
    In-memory implementation to simulate repository behavior of GroceryListRepository for testing purposes.
    This implementation supports dependency injection, mocks persistent storage and decouples
    the tests from the infrastructure
    """

    def __init__(self, grocery_lists: List[GroceryList] = None):
        self.grocery_lists = grocery_lists or []
        self._next_id = 1  # id attributes are added by SQLAlchemy through the ORM mapping. Simulate using counter

    def add(self, entity: GroceryList) -> GroceryList:
        """Add a new grocery list to the repository."""
        entity.id = self._next_id
        self._next_id += 1
        self.grocery_lists.append(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Optional[GroceryList]:
        """Retrieve a grocery list by its ID."""
        return next(
            (gl for gl in self.grocery_lists if gl.id == entity_id), None
        )

    def get_all(self) -> List[GroceryList]:
        """Retrieve all grocery lists from the repository."""
        return self.grocery_lists.copy()

    def update(self, entity: GroceryList) -> GroceryList:
        """Update an existing grocery list in the repository."""
        existing = self.get_by_id(entity.id)
        if existing:
            # Update the existing entity in place
            existing.name = entity.name
            existing.updated_at = entity.updated_at
            return existing
        return entity

    def delete_by_id(self, entity_id: int) -> bool:
        """Delete a grocery list by its ID. Returns True if successful."""
        grocery_list = self.get_by_id(entity_id)
        if grocery_list:
            self.grocery_lists.remove(grocery_list)
            return True
        return False


# TODO: FakeGroceryItemRepository


class FakeSession:
    """Mock session for testing that doesn't actually commit or rollback."""

    committed = False
    rollbacked = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rollbacked = True


# Test cases for GroceryListService
def test_create_grocery_list():
    repo, session = FakeGroceryListRepository(), FakeSession()
    grocery_list_service = GroceryListService(repo, session)

    grocery_list = grocery_list_service.create_grocery_list(
        "Test Shopping List"
    )

    assert grocery_list is not None
    assert grocery_list.name == "Test Shopping List"
    assert grocery_list.id == 1


def test_get_grocery_list():
    """Test retrieving a grocery list by ID."""
    repo, session = FakeGroceryListRepository(), FakeSession()
    grocery_list_service = GroceryListService(repo, session)

    # Create a grocery list first
    grocery_list = grocery_list_service.create_grocery_list(
        "Test Shopping List"
    )

    # Retrieve the created list
    retrieved_list = grocery_list_service.get_grocery_list(grocery_list.id)

    assert retrieved_list is not None
    assert retrieved_list.name == "Test Shopping List"
    assert retrieved_list.id == grocery_list.id


def test_get_all_grocery_lists():
    """Test retrieving all grocery lists."""
    repo, session = FakeGroceryListRepository(), FakeSession()
    grocery_list_service = GroceryListService(repo, session)

    # Create multiple lists
    grocery_list1 = grocery_list_service.create_grocery_list(
        "Test Shopping List 1"
    )
    grocery_list2 = grocery_list_service.create_grocery_list(
        "Test Shopping List 2"
    )

    all_lists = grocery_list_service.get_all_grocery_lists()

    assert len(all_lists) == 2
    assert all_lists[0].name == "Test Shopping List 1"
    assert all_lists[1].name == "Test Shopping List 2"
    assert all_lists[0].id == grocery_list1.id
    assert all_lists[1].id == grocery_list2.id


def test_delete_grocery_list():
    """Test deleting a grocery list."""
    repo, session = FakeGroceryListRepository(), FakeSession()
    grocery_list_service = GroceryListService(repo, session)

    # Create a grocery list first
    grocery_list = grocery_list_service.create_grocery_list(
        "Test Shopping List"
    )

    # Delete it
    is_deleted = grocery_list_service.delete_grocery_list(grocery_list.id)
    assert is_deleted is True

    # Verify it's gone
    retrieved_list = grocery_list_service.get_grocery_list(grocery_list.id)
    assert retrieved_list is None


# TODO: Implement GroceryItemService Tests
