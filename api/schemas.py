from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from models import Roles, OrderStatus


# USERS
class CreateAccount(BaseModel):
    name: str
    email: str
    password: str
    dob: datetime
    role: Roles = Roles.Customer


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    dob: datetime
    role: Roles


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
    # So ideally this would be just the id, and multiple images would go into a folder of the flower's id.
    # But that is annoying to do, so instead we just specify some remote image path it'll be fine.
    image_path: str
    stock: bool = True
    price: float
    category: str = "Other"
    rating: float = 0
    old_price: float | None = None
    tag: str | None = None
    quantity: int | None = None # Sets stock when given


class UpdatePlace(BaseModel):
    name: str | None = None
    description: str | None = None
    image_path: str | None = None
    stock: bool | None = None
    price: float | None = None
    category: str | None = None
    rating: float | None = None
    old_price: float | None = None
    tag: str | None = None
    quantity: int | None = None


class PlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    image_path: str
    stock: bool
    price: float
    category: str
    rating: float
    old_price: float | None
    tag: str | None
    quantity: int | None


# For filters none are necessary.
class PlacesFilterRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    stock: bool | None = None
    price_min: float | int | None = None
    price_max: float| int | None = None
    category: str | None = None

# ORDERS
class OrderItemRequest(BaseModel):
    place_id: int
    quantity: int = Field(default=1, ge=1)


class OrderRequest(BaseModel):
    items: list[OrderItemRequest] = Field(min_length=1)
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postcode: str | None = None
    country: str | None = None


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    place_id: int | None
    name: str
    quantity: int
    price: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    price: float
    status: OrderStatus
    created_at: datetime
    items: list[OrderItemResponse]
    first_name: str | None
    last_name: str | None
    email: str | None
    street: str | None
    city: str | None
    state: str | None
    postcode: str | None
    country: str | None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
