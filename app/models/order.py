from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, root_validator, validator

from app.types.money import Money
from app.types.sku import Sku


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    cancelled = "cancelled"


class OrderItem(BaseModel):
    sku: Sku
    quantity: int = Field(..., gt=0, le=1000)
    unit_price: Money

    class Config:
        anystr_strip_whitespace = True

    @property
    def total(self) -> Money:
        return Money(self.unit_price * self.quantity)


class OrderCreate(BaseModel):
    customer_email: str = Field(..., regex=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    items: List[OrderItem] = Field(..., min_items=1)
    coupon: Optional[str] = None

    @validator("customer_email")
    def lowercase_email(cls, v):
        return v.lower()

    @validator("coupon")
    def coupon_format(cls, v):
        if v is not None and not v.isalnum():
            raise ValueError("coupon must be alphanumeric")
        return v.upper() if v else v

    @root_validator
    def unique_skus(cls, values):
        items = values.get("items") or []
        skus = [i.sku for i in items]
        if len(skus) != len(set(skus)):
            raise ValueError("each sku may appear only once per order")
        return values


class Order(OrderCreate):
    id: UUID = Field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.pending
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        use_enum_values = True
        json_encoders = {datetime: lambda d: d.isoformat() + "Z"}

    @property
    def total(self) -> Money:
        return Money(sum(i.total for i in self.items))


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

    @validator("status", pre=True)
    def normalize(cls, v):
        return v.lower() if isinstance(v, str) else v
