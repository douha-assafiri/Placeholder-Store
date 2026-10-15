from datetime import datetime
from enum import Enum as pyEnum

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship

from database import Base

# Keep the row, clear the link
SET_NULL = "SET NULL"


# Note the enum change. Bcs obviously cant be the same name, so a python enum is PyEnum !!

class Roles(pyEnum):
    Customer = "Customer"
    Staff = "Staff"

class OrderStatus(pyEnum):
    Processing = "Processing"
    Shipped = "Shipped"
    Delivered = "Delivered"
    Cancelled = "Cancelled"

# MariaDB needs String lengths
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    dob = Column(DateTime, default=datetime.now)
    role = Column(Enum(Roles), default=Roles.Customer)


class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(String(1000))
    image_path = Column(String(1000))
    stock = Column(Boolean, index=True)
    price = Column(Float, index=True)
    category = Column(String(100), index=True, default="Other")
    rating = Column(Float, default=0)
    old_price = Column(Float, nullable=True)
    tag = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=True) # None = not counted


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    owner = Column(Integer, ForeignKey("users.id", ondelete=SET_NULL), index=True, nullable=True)
    price = Column(Float) # Order total
    status = Column(Enum(OrderStatus), default=OrderStatus.Processing)
    created_at = Column(DateTime, default=datetime.now)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    street = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    items = relationship("OrderItem", cascade="all, delete-orphan", lazy="selectin")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    place_id = Column(Integer, ForeignKey("places.id", ondelete=SET_NULL), index=True, nullable=True)
    name = Column(String(255)) # Kept if the place is deleted
    quantity = Column(Integer)
    price = Column(Float) # Unit price when ordered

class InvalidJWTs(Base):
    __tablename__ = "invalid_jwts"
    jwt = Column(String(512), primary_key=True, index=True)
    expiry = Column(DateTime, index=True)
