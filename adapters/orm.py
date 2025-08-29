from sqlalchemy import Table, MetaData, Column, Integer, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import mapper, relationship
from sqlalchemy.sql import func

from domain import models

metadata = MetaData()

grocery_items = Table(
    'grocery_items', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255)),
    Column('quantity', Integer, nullable=False),
    Column('status', Enum('pending', 'purchased', name='item_status')),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
)


def start_mappers():
    grocery_items_mapper = mapper(models.GroceryItem, grocery_items)