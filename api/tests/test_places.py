import pytest
from conftest import auth, staff


def test_get_places_no_filter(client, places):
    response = client.get("/places")
    assert response.status_code == 200
    assert len(response.json()) == 3

@pytest.mark.parametrize(
    "test_filter, value, expected",
    [
        # Test the max and min price filters
        ("price_max", 45.0, 1),
        ("price_max", 55.0, 2),
        ("price_min", 45.0, 2),
        ("price_min", 55.0, 1),
        # Test the description and name searching for keywords
        ("description", "eat", 2),
        ("description", "sleep", 1),
        ("description", "here", 3),
        ("name", "a", 3),
        ("name", "cafe", 1),
        # And stock
        ("stock", True, 2),
        ("stock", False, 1),
    ]
)
def test_get_with_filters(client, places,test_filter, value, expected):
    response = client.get("/places", params={test_filter: value})
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) == expected

def test_places_create_forbidden_for_customer(client, customer):
    response = client.post("/places", headers=auth(customer), json={
        "name": "a", "description": "b", "image_path": "c", "stock": True, "price": 1})
    assert response.status_code == 403

def test_add_place_with_admin(client, staff):
    response = client.post("/places", headers=auth(staff), json={
        "name": "a", "description": "b", "image_path": "c", "stock": True, "price": 1})
    assert response.status_code == 201

def test_delete_place_with_admin(client, staff, places):
    response = client.delete(f"/places/{places[0].id}", headers=auth(staff))
    assert response.status_code == 204
    assert len(client.get("/places").json()) == 2 # Assert there are 2 left

def test_delete_non_existent_place(client, staff, places):
    response = client.delete(f"/places/{len(places)+1}", headers=auth(staff))
    assert response.status_code == 404
    assert len(client.get("/places").json()) == 3 # Assert there are 3 left
def test_get_place(client, places):
    response = client.get(f"/places/{places[0].id}")
    assert response.status_code == 200
    assert response.json()["name"] == places[0].name

def test_get_non_existent_place(client, places):
    response = client.get(f"/places/{len(places)+1}")
    assert response.status_code == 404
