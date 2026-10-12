from datetime import datetime
from enum import Enum as pyEnum

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Float

from database import Base


# Note the enum change. Bcs obviously cant be the same name, so a python enum is PyEnum !!

class Roles(pyEnum):
    Customer = "Customer"
    Staff = "Staff"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    dob = Column(DateTime, default=datetime.now)
    role = Column(Enum(Roles), default=Roles.Customer)


class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    image_path = Column(String, index=True)
    stock = Column(Boolean, index=True)
    price = Column(Float, index=True)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    owner = Column(Integer, ForeignKey("users.id"), index=True)
    place_id = Column(Integer, ForeignKey("places.id"), index=True)
    price = Column(Float)

class InvalidJWTs(Base):
    __tablename__ = "invalid_jwts"
    jwt = Column(String, primary_key=True, index=True)
    expiry = Column(DateTime, index=True)