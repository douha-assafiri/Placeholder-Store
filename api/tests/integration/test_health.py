from unittest.mock import MagicMock

from sqlalchemy.exc import OperationalError

from helpers import get_db
from main import app


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}

def test_health_without_database(client):
    broken = MagicMock()
    broken.execute.side_effect = OperationalError("SELECT 1", {}, Exception("connection refused"))
    app.dependency_overrides[get_db] = lambda: broken
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["database"] == "unavailable"

def test_routes_are_not_under_api(client):
    assert client.get("http://testserver/api/places").status_code == 404
    assert client.get("/places").status_code == 200
