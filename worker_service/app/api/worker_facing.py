from fastapi import APIRouter, status, HTTPException

from app.api.schema import Order
from app.api.services import OrdersQueue, OrderNotFoundException


worker_facing = APIRouter()


@worker_facing.post(
    "/sync_orders/",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
)
async def sync_orders(new_orders: list[Order]):
    """
    Add new orders to the queue and return prepared orders.
    """
    orders_queue = OrdersQueue.get_instance()
    orders_queue.add_new_orders(new_orders)
    return orders_queue.get_ready_orders_and_reset()


@worker_facing.get(
    "/start/",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
)
async def get_orders():
    """
    Get a list of new orders.
    """
    orders_queue = OrdersQueue.get_instance()
    return orders_queue.get_new_orders()


@worker_facing.get(
    "/start_order/{order_id}/",
    status_code=status.HTTP_200_OK,
)
async def start_order(order_id: int):
    """
    Move an order from new to in-progress status.
    """
    orders_queue = OrdersQueue.get_instance()
    try:
        orders_queue.move_to_in_progress(order_id)
    except OrderNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found"
        )


@worker_facing.post(
    "/finish/{order_id}/",
    status_code=status.HTTP_200_OK,
)
async def finish_order(order_id: int):
    """
    Move an order from in-progress to ready status.
    """
    orders_queue = OrdersQueue.get_instance()
    orders_queue.move_to_ready(order_id)
