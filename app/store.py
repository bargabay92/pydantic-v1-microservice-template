from typing import Dict, List
from uuid import UUID

from app.models.order import Order


class OrderStore:
    """In-memory store; swap for a real database in production."""

    def __init__(self) -> None:
        self._orders: Dict[UUID, dict] = {}

    def add(self, order: Order) -> Order:
        self._orders[order.id] = order.model_dump()
        return order

    def get(self, order_id: UUID) -> Order:
        return Order.model_validate(self._orders[order_id])

    def list(self) -> List[Order]:
        return [Order.model_validate(o) for o in self._orders.values()]

    def update(self, order: Order) -> Order:
        self._orders[order.id] = order.model_dump()
        return order


store = OrderStore()
