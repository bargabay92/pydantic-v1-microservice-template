from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException

from app.models.order import Order, OrderCreate, OrderStatusUpdate
from app.settings import settings
from app.store import store

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.post("/orders", response_model=Order, status_code=201)
def create_order(payload: OrderCreate) -> Order:
    if len(payload.items) > settings.max_items_per_order:
        raise HTTPException(422, f"max {settings.max_items_per_order} items per order")
    order = Order(**payload.model_dump())
    return store.add(order)


@app.get("/orders", response_model=List[Order])
def list_orders() -> List[Order]:
    return store.list()


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: UUID) -> Order:
    try:
        return store.get(order_id)
    except KeyError:
        raise HTTPException(404, "order not found")


@app.get("/orders/{order_id}/total")
def order_total(order_id: UUID) -> dict:
    try:
        order = store.get(order_id)
    except KeyError:
        raise HTTPException(404, "order not found")
    return {"order_id": str(order.id), "total": str(order.total)}


@app.patch("/orders/{order_id}/status", response_model=Order)
def update_status(order_id: UUID, payload: OrderStatusUpdate) -> Order:
    try:
        order = store.get(order_id)
    except KeyError:
        raise HTTPException(404, "order not found")
    updated = order.model_copy(update={"status": payload.status})
    return store.update(updated)
