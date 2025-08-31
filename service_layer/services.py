"""
The service layer is only concerned with orchestrate business logic,
transaction management (committing or rolling back) is handled by endpoints.
"""

from typing import List, Optional
from adapters.repository import AbstractRepository
from domain.models import GroceryList, GroceryItem
from sqlalchemy.orm import Session


class GroceryListService:
    """Service layer for grocery list operations."""

    def __init__(
        self,
        grocery_list_repo: AbstractRepository[GroceryList],
    ):
        self.grocery_list_repo = grocery_list_repo

    def create_grocery_list(self, name: str) -> GroceryList:
        """Create a new grocery list."""
        grocery_list = GroceryList(name=name)
        new_grocery_list = self.grocery_list_repo.add(grocery_list)
        return new_grocery_list

    def get_grocery_list(self, list_id: int) -> Optional[GroceryList]:
        """Get a grocery list by ID."""
        return self.grocery_list_repo.get_by_id(list_id)

    def get_all_grocery_lists(self) -> List[GroceryList]:
        """Get all grocery lists."""
        return self.grocery_list_repo.get_all()

    def update_grocery_list(
        self, list_id: int, name: str
    ) -> Optional[GroceryList]:
        """Update a grocery list's name."""
        grocery_list = self.grocery_list_repo.get_by_id(list_id)
        if grocery_list:
            grocery_list.update(name=name)
            updated_list = self.grocery_list_repo.update(grocery_list)
            return updated_list
        return None

    def delete_grocery_list(self, list_id: int) -> bool:
        """Delete a grocery list (cascade will automatically delete all items)."""
        # Get the grocery list object first to enable cascade
        grocery_list = self.grocery_list_repo.get_by_id(list_id)
        if not grocery_list:
            return False

        # Access the session from the repository
        session = self.grocery_list_repo.session
        # Delete the object through the session to trigger ORM cascade
        session.delete(grocery_list)
        return True


class GroceryItemService:
    """Service layer for grocery item operations."""

    def __init__(
        self,
        grocery_item_repo: AbstractRepository[GroceryItem],
        grocery_list_repo: AbstractRepository[GroceryList],
        session: Session,
    ):
        self.grocery_item_repo = grocery_item_repo
        self.grocery_list_repo = grocery_list_repo

    def add_item_to_list(
        self, list_id: int, name: str, quantity: int = 1
    ) -> Optional[GroceryItem]:
        """Add a new item to a grocery list."""
        # Get grocery list with given list_id
        grocery_list = self.grocery_list_repo.get_by_id(list_id)
        if not grocery_list:
            return None

        item = GroceryItem(name=name, quantity=quantity)
        item.grocery_list = grocery_list
        new_item = self.grocery_item_repo.add(item)
        return new_item

    def get_item(self, item_id: int) -> Optional[GroceryItem]:
        """Get a grocery item by ID."""
        return self.grocery_item_repo.get_by_id(item_id)

    def get_items_by_list(self, list_id: int) -> Optional[List[GroceryItem]]:
        """Get all grocery items for a specific grocery list."""
        grocery_list = self.grocery_list_repo.get_by_id(list_id)
        if not grocery_list:
            return None
        return grocery_list.grocery_items

    def update_item(
        self,
        item_id: int,
        name: Optional[str] = None,
        quantity: Optional[int] = None,
    ) -> Optional[GroceryItem]:
        """Update a grocery item."""
        item = self.get_item(item_id)
        if item:
            item.update(name=name, quantity=quantity)
            updated_item = self.grocery_item_repo.update(item)
            return updated_item
        return None

    def mark_item_as_purchased(self, item_id: int) -> Optional[GroceryItem]:
        """Mark an item as purchased."""
        item = self.get_item(item_id)
        if item:
            item.mark_as_purchased()
            updated_item = self.grocery_item_repo.update(item)
            return updated_item
        return None

    def mark_item_as_pending(self, item_id: int) -> Optional[GroceryItem]:
        """Mark an item as pending."""
        item = self.get_item(item_id)
        if item:
            item.mark_as_pending()
            updated_item = self.grocery_item_repo.update(item)
            return updated_item
        return None

    def delete_item(self, item_id: int) -> bool:
        """Delete a grocery item."""
        # Simply delete the item from the repository
        # The database foreign key relationship will handle the consistency
        is_deleted = self.grocery_item_repo.delete_by_id(item_id)
        return is_deleted
