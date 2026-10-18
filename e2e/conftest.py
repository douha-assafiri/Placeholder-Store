import os
import uuid

import pytest

# Defaults are for running locally, CI and CD point these at the app they're testing
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def base_url():
    return FRONTEND_URL


@pytest.fixture
def api(playwright):
    context = playwright.request.new_context(base_url=API_URL.rstrip("/") + "/")
    yield context
    context.dispose()


@pytest.fixture
def product(api):
    # Own product, so tests don't use up the sample stock
    email = f"stock-{uuid.uuid4().hex[:8]}@example.com"
    api.post("accounts/create", data={"name": "Stock Staff", "email": email, "password": "secret123",
                                      "dob": "2000-01-01T00:00:00", "role": "Staff"})
    token = api.post("accounts/login", data={"email": email, "password": "secret123"}).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    name = f"Test Lamp {uuid.uuid4().hex[:6]}"
    api.post("places", headers=headers, data={
        "name": name, "description": "A lamp for testing", "price": 10, "quantity": 5,
        "image_path": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=900&q=85"})
    place = api.get("places", params={"name": name}).json()[0]
    yield place
    api.delete(f"places/{place['id']}", headers=headers)
