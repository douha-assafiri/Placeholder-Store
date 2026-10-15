from playwright.sync_api import Page, expect


def test_frontend_loads(page: Page):
    page.goto("/")
    expect(page.locator("#root")).not_to_be_empty()


def test_api_responds(api):
    response = api.get("places")
    assert response.ok
    assert isinstance(response.json(), list)
