from initial_data import add_initial_data, SAMPLE_PLACES
from models import Place


def test_adds_sample_places(db):
    add_initial_data(db)
    assert db.query(Place).count() == len(SAMPLE_PLACES)

def test_running_twice_changes_nothing(db):
    add_initial_data(db)
    add_initial_data(db)
    assert db.query(Place).count() == len(SAMPLE_PLACES)

def test_keeps_existing_places(db, places):
    add_initial_data(db)
    assert db.query(Place).count() == len(places)
