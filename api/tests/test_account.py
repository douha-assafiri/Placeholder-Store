import pytest

from conftest import auth

def test_create_account(client):
    response = client.post("/accounts/create", json={
        "name": "John Smith", "email": "john@smith.com", "password": "johnSmith<3",
        "dob": "2000-01-01T00:00:00"})
    assert response.status_code == 201

# Asserts that pydantic works basically
@pytest.mark.parametrize("missing", ["name", "email", "password", "dob"])
def test_create_account_missing_field(client, missing):
    body = {"name": "John Smith", "email": "john@smith.com",
            "password": "pw", "dob": "2000-01-01T00:00:00"}
    del body[missing]
    r = client.post("/accounts/create", json=body)
    assert r.status_code == 422

def test_duplicate_email(client):
    client.post("/accounts/create", json={
        "name": "John Smith", "email": "john@smith.com", "password": "johnSmith<3",
        "dob": "2000-01-01T00:00:00"})
    response = client.post("/accounts/create", json={
        "name": "John Smith", "email": "john@smith.com", "password": "johnSmith<3",
        "dob": "2000-01-01T00:00:00"})
    assert response.status_code == 400

def test_login_wrong_password(client, customer):
    response = client.post("/accounts/login", json={"email": customer.email, "password": "nope"})
    assert response.status_code == 400

def test_login_wrong_email(client):
    response = client.post("/accounts/login", json={"email": "incorrect@email.com", "password": "nope"})
    assert response.status_code == 400

def test_me_requires_auth(client):
    assert client.get("/accounts/me").status_code == 422  # missing header

def test_me_with_jwt(client, customer):
    response = client.get("/accounts/me", headers=auth(customer))
    assert response.status_code == 200

def test_places_create_forbidden_for_customer(client, customer):
    response = client.post("/places", headers=auth(customer), json={
        "name": "a", "description": "b", "image_path": "c", "stock": True, "price": 1})
    assert response.status_code == 403