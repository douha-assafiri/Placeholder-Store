import datetime
from enum import Enum as pyEnum
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum
from pydantic import BaseModel

# Not the enum change. Bcs obvsiously cant be the same name, so a python enum is PyEnum !!

class Roles(pyEnum):
    Customer = "Customer"
    Staff = "Staff"

class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    dob = Column(DateTime, default=datetime.now)
    role = Column(Enum(Roles), default=Roles.Customer)


class Place(BaseModel):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    image_path = Column(String, index=True)
    stock = Column(Boolean, index=True)
    price = Column(Integer, index=True)


class Order(BaseModel):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, index=True, ForeignKey="users.id")
    place_id = Column(String, index=True, ForeignKey="places.id")