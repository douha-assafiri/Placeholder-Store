import pytest
from conftest import auth


def test_place_order(client, customer, places):
    response = client.post("/orders", json={"items": [{"place_id": places[0].id}]}, headers=auth(customer))
    assert response.status_code == 201


def test_place_order_non_existent_place(client, customer, places):
    response = client.post("/orders", json={"items": [{"place_id": len(places)+1}]}, headers=auth(customer))
    assert response.status_code == 404


def test_place_and_view_order(client, customer, places):
    response = client.post("/orders", json={"items": [{"place_id": places[0].id}]}, headers=auth(customer))
    assert response.status_code == 201
    response = client.get("/accounts/me/orders", headers=auth(customer))
    assert response.status_code == 200
    assert len(response.json()) == 1
    response = client.post("/orders", json={"items": [{"place_id": places[1].id}]}, headers=auth(customer))
    assert response.status_code == 201
    response = client.get("/accounts/me/orders", headers=auth(customer))
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_order_with_items_and_details(client, customer, places):
    response = client.post("/orders", headers=auth(customer), json={
        "items": [{"place_id": places[0].id, "quantity": 2}, {"place_id": places[2].id, "quantity": 1}],
        "first_name": "Jo", "street": "1 Main St", "city": "Melbourne", "country": "Australia"})
    assert response.status_code == 201
    order = response.json()
    assert order["price"] == 5 * 2 + 200
    assert order["status"] == "Processing"
    assert [(i["name"], i["quantity"]) for i in order["items"]] == [("Cheap Cafe", 2), ("Fancy Hotel", 1)]
    assert order["first_name"] == "Jo"
    assert order["city"] == "Melbourne"

def test_order_reduces_quantity(client, customer, staff, places):
    client.patch(f"/places/{places[0].id}", headers=auth(staff), json={"quantity": 2})
    client.post("/orders", headers=auth(customer), json={"items": [{"place_id": places[0].id, "quantity": 2}]})
    place = client.get(f"/places/{places[0].id}").json()
    assert place["quantity"] == 0
    assert place["stock"] is False

def test_order_more_than_in_stock(client, customer, staff, places):
    client.patch(f"/places/{places[0].id}", headers=auth(staff), json={"quantity": 1})
    response = client.post("/orders", headers=auth(customer), json={"items": [{"place_id": places[0].id, "quantity": 2}]})
    assert response.status_code == 409

@pytest.mark.parametrize("body", [{}, {"items": []}, {"items": [{"place_id": 1, "quantity": 0}]}])
def test_invalid_order(client, customer, places, body):
    assert client.post("/orders", headers=auth(customer), json=body).status_code == 422

def test_staff_views_all_orders(client, customer, staff, places):
    client.post("/orders", headers=auth(customer), json={"items": [{"place_id": places[0].id}]})
    response = client.get("/orders", headers=auth(staff))
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_customer_cannot_view_all_orders(client, customer):
    assert client.get("/orders", headers=auth(customer)).status_code == 403

def test_update_order_status(client, customer, staff, places):
    order = client.post("/orders", headers=auth(customer), json={"items": [{"place_id": places[0].id}]}).json()
    response = client.patch(f"/orders/{order['id']}/status", headers=auth(staff), json={"status": "Shipped"})
    assert response.status_code == 200
    assert client.get("/accounts/me/orders", headers=auth(customer)).json()[0]["status"] == "Shipped"

def test_update_status_forbidden_for_customer(client, customer, places):
    order = client.post("/orders", headers=auth(customer), json={"items": [{"place_id": places[0].id}]}).json()
    response = client.patch(f"/orders/{order['id']}/status", headers=auth(customer), json={"status": "Shipped"})
    assert response.status_code == 403
