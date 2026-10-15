import pytest
from pydantic import ValidationError

from initial_data import SAMPLE_PLACES
from schemas import OrderItemRequest, OrderRequest, CreatePlace, UpdatePlace


def test_item_quantity_defaults_to_one():
    assert OrderItemRequest(place_id=1).quantity == 1

def test_item_quantity_must_be_positive():
    with pytest.raises(ValidationError):
        OrderItemRequest(place_id=1, quantity=0)

def test_order_needs_items():
    with pytest.raises(ValidationError):
        OrderRequest(items=[])

def test_new_place_defaults():
    place = CreatePlace(name="a", description="b", image_path="c", price=1)
    assert place.stock is True
    assert place.category == "Other"
    assert place.quantity is None

def test_update_only_has_sent_fields():
    assert UpdatePlace(price=5).model_dump(exclude_unset=True) == {"price": 5}

def test_sample_places_are_valid():
    for place in SAMPLE_PLACES:
        assert CreatePlace(**place).quantity > 0
