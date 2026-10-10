import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from database import Base
from helpers import get_db, create_jwt, hasher
from models import User, Roles
from main import app

# Set the default enviroment variables for testing
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION", "1")
os.environ.setdefault("DB_URL", "sqlite://")


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False}, # Allow multiple threads to talk to the db for speed
        poolclass=StaticPool,  # Keeps only one db alive in memory only for speeeed
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


def make_user(db, email="test@customer.com", password="test123!", role=Roles.Customer):
    user = User(name="Test", email=email, password=hasher.hash(password), role=role)
    db.add(user); db.commit(); db.refresh(user)
    return user

@pytest.fixture
def customer(db):
    return make_user(db)


@pytest.fixture
def staff(db):
    return make_user(db, email="test@staff.com", password="test456@")

def auth(user):
    return {"Authorization": f"Bearer {create_jwt(user.id)}"}