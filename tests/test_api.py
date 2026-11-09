from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PAYLOAD = {"customer_email": "Bar@Example.com",
           "items": [{"sku": "abc-1234", "quantity": 3, "unit_price": "2.50"}]}


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_create_get_total_and_status():
    r = client.post("/orders", json=PAYLOAD)
    assert r.status_code == 201, r.text
    order = r.json()
    assert order["customer_email"] == "bar@example.com"
    assert order["status"] == "pending"

    assert client.get(f"/orders/{order['id']}").status_code == 200
    assert client.get(f"/orders/{order['id']}/total").json()["total"] == "7.50"

    r = client.patch(f"/orders/{order['id']}/status", json={"status": "PAID"})
    assert r.json()["status"] == "paid"


def test_validation_error():
    bad = dict(PAYLOAD, items=[])
    assert client.post("/orders", json=bad).status_code == 422


def test_not_found():
    assert client.get("/orders/00000000-0000-0000-0000-000000000000").status_code == 404
