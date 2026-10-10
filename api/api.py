import datetime
import os

import argon2
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
if not os.getenv("DB_URL"):
    DB_URL = os.getenv("sqlite:///./dev.sqlite3")
else:
    DB_URL = os.getenv("DB_URL")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

engine = create_engine(DB_URL)
LocalSession = sessionmaker(bind=engine)
Base = declarative_base()

# The hasher creates and salts the passwords
# Argon2 is more secure than Bcrypt apparently
hasher = argon2.password_hash()


# Below represents the schema for the database, each class is a different table.
# Hence hwo fastAPI and Pydantic abstract it so I dont need to write any SQL yay
class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    dob = Column(DateTime)


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


# Create all the tabels
Base.metadata.create_all(engine)


# DB helper function, lets us know if we can get the db or not
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

# Fast API setup
app = FastAPI()

## Next define the response we expect to recieve and send
# USERS
class CreateAccount(BaseModel):
    name: str
    email: str
    password: str
    dob: datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    id: int




## PLACES
class CreatePlace(BaseModel):
    name: str
    description: str
    image_path: str
    stock: bool
    price: float


class PlaceResponse(BaseModel):
    id: int
    name: str
    description: str
    image_path: str
    stock: bool
    price: float


class PlacesResponse(BaseModel):
    places: list[PlaceResponse]

## ORDERS
class OrderRequest(BaseModel):
    id: int
