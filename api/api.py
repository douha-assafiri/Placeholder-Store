import datetime
import os

import argon2
import jwt
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.middleware.cors import CORSMiddleware


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
class Roles(Enum):
    Customer = "Customer"
    Staff = "Staff"

class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    dob = Column(DateTime)
    role = Column(roles)


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
## Next define the response we expect to recieve and send
# USERS
class CreateAccount(BaseModel):
    name: str
    email: str
    password: str
    dob: datetime

class AccountResponse(BaseModel):
    name: str
    email: str
    dob: datetime
    role = Column(String)


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    id: int

# JWT stuff (This is so we can identify someone who logs in without them logging in all the time
## JWT stuff


SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
TOKEN_EXPIRATION: int = int(os.getenv("JWT_TOKEN_EXPIRATION"))


# JWT Explained: https://www.geeksforgeeks.org/web-tech/json-web-token-jwt/
def create_jwt(ident: int) -> str:
    payload = {
        "sub": str(ident),  # Subject (so the user(
        "iat": datetime.now(timezone.utc),  # Issuing time
        "exp": datetime.now(timezone.utc) + timedelta(hours=int(TOKEN_EXPIRATION)),  # Expiry time
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # Encoded into base64 hs265


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Header")
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode with JWT, with what it encrypted with
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()  # Look for the subject in the db
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Functions (endpoints)

@app.post("/account")
async def create_account(account: CreateAccount, db: Session = Depends(get_db)):
    hashed = hasher.hash(account.password) # Argon2 automatically applies salt
    new_user = User(
        name=account.name,
        email=account.email,
        password=hashed,
        dob=account.dob,
        role=Roles.Customer
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    #TODO, return a success or something? We shouldnt need a response model for creating an account, just http 200

@app.get("/account/{account_id}", response_model=User)
async def get_account(account_id: int, current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/login", response_model=LoginResponse)
async def login(account: LoginRequest, db: Session = Depends(get_db)):
    db_account = db.query(User).filter(User.email == account.email).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Incorrect credentials")
    try:
        hasher.verify(account.password, db_account.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=404, detail="Incorrect credentials")
    token = create_jwt(db_account.id)
    return LoginResponse(token=token, id=db_account.id)

@app.delete("/account/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    db.refresh(current_user)

@app.post("/logout")
async def logout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass
    #TODO, logout stuff here, maintain a table of invalid JWTs?

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


# For filters none are necessary.
class PlacesFilterRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    stock: bool | None = None
    price_min: float | int | None = None
    price_max: float| int | None = None

class PlacesResponse(BaseModel):
    places: list[PlaceResponse]

@app.get("/places", response_model=PlacesResponse)
async def get_places_filter(filters: PlacesFilterRequest , db : Session = Depends(get_db)):
    #https://stackoverflow.com/questions/31063860/conditionally-filtering-in-sqlalchemy
    query = db.query(Place)

    if filters.name is not None:
        query = query.filter(Place.name.ilike(f"%{filters.name}%"))
    if filters.description is not None:
        query = query.filter(Place.description.ilike(f"%{filters.description}%"))
    if filters.stock is not None:
        query = query.filter(Place.stock == filters.stock)
    if filters.price_min is not None:
        query = query.filter(Place.price >= filters.price_min )
    if filters.price_min is not None:
        query = query.filter(Place.price <= filters.price_max )

    return PlaceResponse(places=query.all())

# For things that require admin access, acts as middleware basically
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Roles.Staff:
        raise HTTPException(status_code=403, detail="You are not an admin :(")
    return current_user

@app.post("/places", response_model=PlacesResponse)
async def create_place(place: CreatePlace, db: Session = Depends(get_db), user = Depends(require_admin)):
    db.add(Place(
        name=place.name,
        description=place.description,

    ))
    db.commit()
    db.refresh(place)

## ORDERS
class OrderRequest(BaseModel):
    id: int
