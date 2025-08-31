from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import registry, relationship
from sqlalchemy.sql import func

from domain import models
from domain.models import ItemStatus

metadata = MetaData()
mapper_registry = registry()

grocery_items = Table(
    "grocery_items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255)),
    Column("quantity", Integer, nullable=False),
    Column("status", Enum(ItemStatus, name="item_status")),
    Column("grocery_list_id", Integer, ForeignKey("grocery_lists.id")),
    Column("purchased_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    ),
)

grocery_lists = Table(
    "grocery_lists",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255)),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    ),
)


def start_mappers():
    mapper_registry.map_imperatively(
        models.GroceryItem,
        grocery_items,
        properties={
            "grocery_list": relationship(
                models.GroceryList, back_populates="grocery_items"
            )
        },
    )

    mapper_registry.map_imperatively(
        models.GroceryList,
        grocery_lists,
        properties={
            "grocery_items": relationship(
                models.GroceryItem, back_populates="grocery_list"
            )
        },
    )
