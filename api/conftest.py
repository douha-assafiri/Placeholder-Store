import os
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION", "1")
os.environ.setdefault("DB_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from database import Base
from helpers import get_db, create_jwt, hasher
from models import User, Roles, Place
from main import app

# Set the default environment variables for testing

# Set in CI to test on MariaDB
TEST_DB_URL = os.getenv("TEST_DB_URL")


@pytest.fixture
def db():
    if TEST_DB_URL:
        engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
    else:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False}, # Allow multiple threads to talk to the db for speed
            poolclass=StaticPool,  # Keeps only one db alive in memory only for speed
        )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app, base_url="http://testserver/api")
    app.dependency_overrides.clear()


def make_user(db, email="test@customer.com", password="test123!", role=Roles.Customer):
    user = User(name="Test", email=email, password=hasher.hash(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def customer(db):
    return make_user(db)

@pytest.fixture
def staff(db):
    return make_user(db, email="test@staff.com", password="test456@", role=Roles.Staff)

@pytest.fixture
def places(db):
    items = [
        Place(name="Cheap Cafe", description="Eat here", image_path="a", stock=True, price=5),
        Place(name="Mid Bar", description="Eat here", image_path="b", stock=False, price=50),
        Place(name="Fancy Hotel", description="Sleep here", image_path="c", stock=True, price=200),
    ]
    db.add_all(items)
    db.commit()
    return items

def auth(user):
    return {"Authorization": f"Bearer {create_jwt(user.id)}"}