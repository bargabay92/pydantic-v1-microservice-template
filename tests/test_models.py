import json

import pytest
from pydantic import ValidationError

from app.models.order import Order, OrderCreate, OrderItem
from app.types.money import Money


def item(**kw):
    data = {"sku": "abc-1234", "quantity": 2, "unit_price": "9.99"}
    data.update(kw)
    return data


def test_sku_is_normalized():
    assert OrderItem(**item()).sku == "ABC-1234"


def test_invalid_sku_rejected():
    with pytest.raises(ValidationError):
        OrderItem(**item(sku="bad"))


def test_money_precision():
    with pytest.raises(ValidationError):
        OrderItem(**item(unit_price="1.999"))


def test_negative_money_rejected():
    with pytest.raises(ValidationError):
        OrderItem(**item(unit_price="-1"))


def test_email_lowercased_and_coupon_upper():
    o = OrderCreate(customer_email="Bar@Example.COM", items=[item()], coupon="save10")
    assert o.customer_email == "bar@example.com"
    assert o.coupon == "SAVE10"


def test_duplicate_skus_rejected():
    with pytest.raises(ValidationError):
        OrderCreate(customer_email="a@b.co", items=[item(), item()])


def test_order_total_and_roundtrip():
    o = Order(customer_email="a@b.co", items=[item(), item(sku="XYZ-0001", quantity=1, unit_price="5")])
    assert o.total == Money("24.98")
    again = Order.parse_raw(o.json())
    assert again.id == o.id
    assert json.loads(o.json())["created_at"].endswith("Z")


def test_schema_has_money_pattern():
    schema = OrderItem.schema()
    assert schema["properties"]["unit_price"]["pattern"].startswith("^")
