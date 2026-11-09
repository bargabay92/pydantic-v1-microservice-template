from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

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
    model_config = ConfigDict(str_strip_whitespace=True)

    @property
    def total(self) -> Money:
        return Money(self.unit_price * self.quantity)


class OrderCreate(BaseModel):
    customer_email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    items: List[OrderItem] = Field(..., min_length=1)
    coupon: Optional[str] = None

    @field_validator("customer_email")
    @classmethod
    def lowercase_email(cls, v):
        return v.lower()

    @field_validator("coupon")
    @classmethod
    def coupon_format(cls, v):
        if v is not None and not v.isalnum():
            raise ValueError("coupon must be alphanumeric")
        return v.upper() if v else v

    @model_validator(mode="after")
    def unique_skus(self):
        skus = [i.sku for i in self.items]
        if len(skus) != len(set(skus)):
            raise ValueError("each sku may appear only once per order")
        return self


class Order(OrderCreate):
    id: UUID = Field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.pending
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    @field_serializer("created_at", when_used="json")
    def _created_at_json(self, d: datetime) -> str:
        # v1 used json_encoders for this; same output: ISO time with a trailing Z
        return d.isoformat() + "Z"

    @property
    def total(self) -> Money:
        return Money(sum(i.total for i in self.items))


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

    @field_validator("status", mode="before")
    @classmethod
    def normalize(cls, v):
        return v.lower() if isinstance(v, str) else v
