from typing import List, Optional
from adapters.repository import AbstractRepository
from domain.models import GroceryList, GroceryItem
from sqlalchemy.orm import Session


class GroceryListService:
    """Service layer for grocery list operations."""

    def __init__(
        self,
        grocery_list_repo: AbstractRepository[GroceryList],
        session: Session,
    ):
        self.grocery_list_repo = grocery_list_repo
        self.session = session

    def create_grocery_list(self, name: str) -> GroceryList:
        """Create a new grocery list."""
        try:
            grocery_list = GroceryList(name=name)
            new_grocery_list = self.grocery_list_repo.add(grocery_list)
            self.session.commit()
            return new_grocery_list
        except Exception as e:
            self.session.rollback()
            raise e

    def get_grocery_list(self, list_id: int) -> Optional[GroceryList]:
        """Get a grocery list by ID."""
        return self.grocery_list_repo.get_by_id(list_id)

    def get_all_grocery_lists(self) -> List[GroceryList]:
        """Get all grocery lists."""
        return self.grocery_list_repo.get_all()

    def delete_grocery_list(self, list_id: int) -> bool:
        """Delete a grocery list."""
        try:
            is_deleted = self.grocery_list_repo.delete_by_id(list_id)
            self.session.commit()
            return is_deleted
        except Exception as e:
            self.session.rollback()
            raise e


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
        self.session = session

    def add_item_to_list(
        self, list_id: int, name: str, quantity: int = 1
    ) -> Optional[GroceryItem]:
        """Add a new item to a grocery list."""
        try:
            # Get grocery list with given list_id
            grocery_list = self.grocery_list_repo.get_by_id(list_id)
            if not grocery_list:
                return None

            item = GroceryItem(name=name, quantity=quantity)
            item.grocery_list = grocery_list
            new_item = self.grocery_item_repo.add(item)
            self.session.commit()
            return new_item
        except Exception as e:
            self.session.rollback()
            raise e

    def get_item(self, item_id: int) -> Optional[GroceryItem]:
        """Get a grocery item by ID."""
        return self.grocery_item_repo.get_by_id(item_id)

    def update_item(
        self,
        item_id: int,
        name: Optional[str] = None,
        quantity: Optional[int] = None,
    ) -> Optional[GroceryItem]:
        """Update a grocery item."""
        try:
            item = self.get_item(item_id)
            if item:
                item.update(name=name, quantity=quantity)
                updated_item = self.grocery_item_repo.update(item)
                self.session.commit()
                return updated_item
            return None
        except Exception as e:
            self.session.rollback()
            raise e

    def mark_item_as_purchased(self, item_id: int) -> Optional[GroceryItem]:
        """Mark an item as purchased."""
        try:
            item = self.get_item(item_id)
            if item:
                item.mark_as_purchased()
                updated_item = self.grocery_item_repo.update(item)
                self.session.commit()
                return updated_item
            return None
        except Exception as e:
            self.session.rollback()
            raise e

    def mark_item_as_pending(self, item_id: int) -> Optional[GroceryItem]:
        """Mark an item as pending."""
        try:
            item = self.get_item(item_id)
            if item:
                item.mark_as_pending()
                updated_item = self.grocery_item_repo.update(item)
                self.session.commit()
                return updated_item
            return None
        except Exception as e:
            self.session.rollback()
            raise e

    def delete_item(self, item_id: int) -> bool:
        """Delete a grocery item."""
        # First get the item to find its grocery list
        try:
            item = self.get_item(item_id)
            if not item:
                return False

            # Get the grocery list that contains this item
            grocery_list = item.grocery_list
            if grocery_list:
                # Use the domain model's remove_item method
                grocery_list.remove_item(item_id)
                # Update the grocery list to persist the change
                self.grocery_list_repo.update(grocery_list)

            # Delete the item from the repository
            is_deleted = self.grocery_item_repo.delete_by_id(item_id)
            self.session.commit()
            return is_deleted
        except Exception as e:
            self.session.rollback()
            raise e
