import pytest
from conftest import auth, staff, places


def test_place_order(client, customer, places):
    response = client.post("/orders", json={
        "place_id" : places[0].id
    }, headers=auth(customer))
    assert response.status_code == 201


def test_place_order_non_existent_place(client, customer, places):
    response = client.post("/orders", json={
        "place_id" : len(places)+1
    }, headers=auth(customer))
    assert response.status_code == 404


def test_place_and_view_order(client, customer, places):
    response = client.post("/orders", json={
        "place_id" : places[0].id
    }, headers=auth(customer))
    assert response.status_code == 201
    response = client.get("/accounts/me/orders", headers=auth(customer))
    assert response.status_code == 200
    assert len(response.json()) == 1
    response = client.post("/orders", json={
        "place_id" : places[1].id
    }, headers=auth(customer))
    assert response.status_code == 201
    response = client.get("/accounts/me/orders", headers=auth(customer))
    assert response.status_code == 200
    assert len(response.json()) == 2
