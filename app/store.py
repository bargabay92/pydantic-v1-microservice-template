from typing import Dict, List
from uuid import UUID

from app.models.order import Order


class OrderStore:
    """In-memory store; swap for a real database in production."""

    def __init__(self) -> None:
        self._orders: Dict[UUID, dict] = {}

    def add(self, order: Order) -> Order:
        self._orders[order.id] = order.dict()
        return order

    def get(self, order_id: UUID) -> Order:
        return Order.parse_obj(self._orders[order_id])

    def list(self) -> List[Order]:
        return [Order.parse_obj(o) for o in self._orders.values()]

    def update(self, order: Order) -> Order:
        self._orders[order.id] = order.dict()
        return order


store = OrderStore()
