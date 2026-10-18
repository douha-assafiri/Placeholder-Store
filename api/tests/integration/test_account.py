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
    assert response.status_code == 409

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


def test_delete_account(client, customer):
    response = client.delete("/accounts/me", headers=auth(customer))
    assert response.status_code == 200

def test_logout(client, customer):
    headers = auth(customer)
    response = client.post("/accounts/logout", headers=headers)
    assert response.status_code == 204
    assert client.get("/accounts/me", headers=headers).status_code == 401 # Token is now blocked

def test_logout_other_user(client, customer, staff):
    other_headers = auth(staff)
    other_token = other_headers["Authorization"].removeprefix("Bearer ")
    client.post("/accounts/logout", headers=auth(customer), params={"token": other_token})
    assert client.get("/accounts/me", headers=other_headers).status_code == 200

def test_update_account_without_password(client, customer):
    response = client.patch("/accounts/me", headers=auth(customer), json={
        "name": "New Name", "email": customer.email, "dob": "2000-01-01T00:00:00"})
    assert response.status_code == 204
    assert client.get("/accounts/me", headers=auth(customer)).json()["name"] == "New Name"

def test_update_account_taken_email(client, customer, staff):
    response = client.patch("/accounts/me", headers=auth(customer), json={
        "name": "Test", "email": staff.email, "dob": "2000-01-01T00:00:00"})
    assert response.status_code == 409

def test_register_as_staff(client):
    client.post("/accounts/create", json={
        "name": "Sam Staff", "email": "sam@staff.com", "password": "secret123",
        "dob": "2000-01-01T00:00:00", "role": "Staff"})
    token = client.post("/accounts/login", json={"email": "sam@staff.com", "password": "secret123"}).json()["token"]
    assert client.get("/accounts/me", headers={"Authorization": f"Bearer {token}"}).json()["role"] == "Staff"

def test_register_defaults_to_customer(client):
    client.post("/accounts/create", json={
        "name": "Jo", "email": "jo@test.com", "password": "secret123", "dob": "2000-01-01T00:00:00"})
    token = client.post("/accounts/login", json={"email": "jo@test.com", "password": "secret123"}).json()["token"]
    assert client.get("/accounts/me", headers={"Authorization": f"Bearer {token}"}).json()["role"] == "Customer"
