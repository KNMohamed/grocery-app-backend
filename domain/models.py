from enum import Enum
from datetime import datetime
from typing import Optional

class ItemStatus(Enum):
    PENDING = "pending"
    PURCHASED = "purchased"

class GroceryItem:
    def __init__(self, name: str, quantity: int = 1):
        self.name = name
        self.quantity = quantity
        self.status = ItemStatus.PENDING
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.purchased_at: Optional[datetime] = None
        
    def mark_as_purchased(self):
        self.status = ItemStatus.PURCHASED
        self.purchased_at = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_as_pending(self):
        self.status = ItemStatus.PENDING
        self.purchased_at = None
        self.updated_at = datetime.now()
        
    def update(self, name: Optional[str] = None, quantity: Optional[int] = None):
        if name is not None:
            self.name = name
        if quantity is not None:
            self.quantity = quantity
        self.updated_at = datetime.now()