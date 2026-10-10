from datetime import datetime
from pydantic import BaseModel
from models import Roles


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
    role = Roles


class AccountUpdate(BaseModel):
    name: str
    email: str
    dob: datetime


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    id: int

# PLACES
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


# ORDERS
class OrderRequest(BaseModel):
    id: int