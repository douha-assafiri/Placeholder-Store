import os

import pytest

# Defaults are for running locally, CI and CD point these at the app they're testing
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")


@pytest.fixture(scope="session")
def base_url():
    return FRONTEND_URL


@pytest.fixture
def api(playwright):
    context = playwright.request.new_context(base_url=API_URL.rstrip("/") + "/")
    yield context
    context.dispose()
