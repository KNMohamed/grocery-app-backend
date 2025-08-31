from enum import Enum
from datetime import datetime
from typing import List, Optional


class ItemStatus(Enum):
    PENDING = "pending"
    PURCHASED = "purchased"


class GroceryItem:
    def __init__(self, name: str, quantity: int = 1):
        self.name = name
        self.quantity = quantity
        self.status = ItemStatus.PENDING
        self.purchased_at: Optional[datetime] = None
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()

    def mark_as_purchased(self):
        self.status = ItemStatus.PURCHASED
        self.purchased_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_as_pending(self):
        self.status = ItemStatus.PENDING
        self.purchased_at = None
        self.updated_at = datetime.now()

    def update(
        self, name: Optional[str] = None, quantity: Optional[int] = None
    ):
        if name is not None:
            self.name = name
        if quantity is not None:
            self.quantity = quantity
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert GroceryItem to dictionary for JSON serialization."""
        return {
            "id": getattr(self, "id", None),
            "name": self.name,
            "quantity": self.quantity,
            "is_purchased": self.status == ItemStatus.PURCHASED,
            "purchased_at": self.purchased_at.isoformat() if self.purchased_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class GroceryList:
    def __init__(self, name: str):
        self.name = name
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()

    def add_item(self, item: GroceryItem) -> GroceryItem:
        self.grocery_items.append(item)
        self.updated_at = datetime.now()
        return item

    def remove_item(self, item_id: int):
        """Remove grocery item by a given id"""
        item_to_remove = next(
            (item for item in self.grocery_items if item.id == item_id), None
        )
        if item_to_remove:
            self.grocery_items.remove(item_to_remove)
            self.updated_at = datetime.now()

    def get_pending_items(self) -> List[GroceryItem]:
        return [
            item
            for item in self.grocery_items
            if item.status == ItemStatus.PENDING
        ]

    def get_purchased_items(self) -> List[GroceryItem]:
        return [
            item
            for item in self.grocery_items
            if item.status == ItemStatus.PURCHASED
        ]

    def update(self, name: Optional[str] = None):
        """Update grocery list properties."""
        if name is not None:
            self.name = name
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert GroceryList to dictionary for JSON serialization."""
        return {
            "id": getattr(self, "id", None),
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "grocery_items": [item.to_dict() for item in getattr(self, "grocery_items", [])],
        }
