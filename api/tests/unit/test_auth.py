from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION
from helpers import create_jwt, get_jwt_expiry, verify_password, get_current_user, require_admin, hasher
from models import User, Roles


def test_token_holds_the_user_id():
    payload = jwt.decode(create_jwt(42), JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "42"

def test_token_expires_after_the_set_hours():
    expected = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION)
    assert abs(get_jwt_expiry(create_jwt(1)) - expected) < timedelta(seconds=5)

def test_correct_password():
    assert verify_password(User(password=hasher.hash("secret123")), "secret123")

def test_wrong_password():
    assert not verify_password(User(password=hasher.hash("secret123")), "nope")

@pytest.mark.parametrize("header", ["", "Token abc", "Bearer not-a-real-token"])
def test_bad_authorization_header(header):
    with pytest.raises(HTTPException) as error:
        get_current_user(header, db=None)
    assert error.value.status_code == 401

def test_customer_is_not_admin():
    customer = User(email="c@test.com", role=Roles.Customer)
    with pytest.raises(HTTPException) as error:
        require_admin(customer)
    assert error.value.status_code == 403

def test_staff_is_admin():
    staff = User(email="s@test.com", role=Roles.Staff)
    assert require_admin(staff) is staff
