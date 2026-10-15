import initial_data
from initial_data import add_initial_data, SAMPLE_PLACES
from models import User, Roles, Place


def test_adds_staff_and_places(db, monkeypatch):
    monkeypatch.setattr(initial_data, "ADMIN_EMAIL", "admin@store.com")
    monkeypatch.setattr(initial_data, "ADMIN_PASSWORD", "secret123")
    add_initial_data(db)
    assert db.query(User).filter(User.role == Roles.Staff).one().email == "admin@store.com"
    assert db.query(Place).count() == len(SAMPLE_PLACES)

def test_running_twice_changes_nothing(db, monkeypatch):
    monkeypatch.setattr(initial_data, "ADMIN_EMAIL", "admin@store.com")
    monkeypatch.setattr(initial_data, "ADMIN_PASSWORD", "secret123")
    add_initial_data(db)
    add_initial_data(db)
    assert db.query(User).count() == 1
    assert db.query(Place).count() == len(SAMPLE_PLACES)

def test_no_staff_without_settings(db, monkeypatch):
    monkeypatch.setattr(initial_data, "ADMIN_EMAIL", None)
    add_initial_data(db)
    assert db.query(User).count() == 0

def test_keeps_existing_places(db, places):
    add_initial_data(db)
    assert db.query(Place).count() == len(places)
