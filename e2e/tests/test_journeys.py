import uuid

from playwright.sync_api import Page, expect

def register(page: Page, name: str, email: str, password: str = "secret123", role: str = "Customer"):
    page.goto("/account")
    page.get_by_role("button", name="Create an account").click()
    page.get_by_label("Full name").fill(name)
    page.get_by_label("Email address").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_label("Date of birth").fill("2000-01-01")
    page.get_by_label("Account type").select_option(role)
    page.get_by_role("button", name="Create account").click()
    expect(page.get_by_role("heading", name=f"Hi, {name}")).to_be_visible()



def test_customer_registers_and_orders(page: Page, product):
    register(page, "Jo Customer", f"jo-{uuid.uuid4().hex[:8]}@example.com")

    page.goto("/shop")
    page.get_by_role("button", name=f"Add {product['name']} to cart").click()
    page.goto("/cart")
    page.get_by_role("link", name="Continue to checkout").click()

    page.get_by_label("First name").fill("Jo")
    page.get_by_label("Last name").fill("Customer")
    page.get_by_label("Street address").fill("1 Example Street")
    page.get_by_label("Suburb / City").fill("Melbourne")
    page.get_by_label("State").fill("VIC")
    page.get_by_label("Postcode").fill("3000")
    page.get_by_role("button", name="Place order").click()

    expect(page.get_by_role("heading", name="Thanks for shopping with us.")).to_be_visible()
    page.goto("/account")
    expect(page.get_by_text("Processing")).to_be_visible()


def test_customer_cannot_open_admin(page: Page):
    register(page, "Sam Customer", f"sam-{uuid.uuid4().hex[:8]}@example.com")
    page.goto("/admin")
    expect(page.get_by_role("heading", name="Staff only")).to_be_visible()


def test_staff_manages_products_and_orders(page: Page, api, product):
    email = f"order-{uuid.uuid4().hex[:8]}@example.com"
    api.post("accounts/create", data={"name": "Buyer", "email": email, "password": "secret123", "dob": "2000-01-01T00:00:00"})
    token = api.post("accounts/login", data={"email": email, "password": "secret123"}).json()["token"]
    order = api.post("orders", data={"items": [{"place_id": product["id"], "quantity": 1}]}, headers={"Authorization": f"Bearer {token}"}).json()

    register(page, "Sam Staff", f"staff-{uuid.uuid4().hex[:8]}@example.com", role="Staff")
    page.goto("/admin")
    expect(page.get_by_role("heading", name="Admin dashboard")).to_be_visible()

    name = f"Test Vase {uuid.uuid4().hex[:6]}"
    page.get_by_role("button", name="Add product").click()
    page.get_by_label("Product name").fill(name)
    page.get_by_label("Price (AUD)", exact=True).fill("25")
    page.get_by_label("Stock").fill("5")
    page.get_by_label("Description").fill("A vase for testing")
    page.get_by_role("button", name="Save product").click()
    row = page.get_by_role("row").filter(has_text=name)
    expect(row).to_be_visible()

    row.get_by_role("button", name="Edit").click()
    page.get_by_label("Price (AUD)", exact=True).fill("30")
    page.get_by_role("button", name="Save product").click()
    expect(row).to_contain_text("30.00")

    page.get_by_label(f"Status for {order['id']}").select_option("Shipped")
    expect(page.get_by_label(f"Status for {order['id']}")).to_have_value("Shipped")

    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name="Delete").click()
    expect(row).to_have_count(0)
