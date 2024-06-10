from fastapi import APIRouter, status

from app.api.schema import ReadyOrder
from app.api.services import OrdersQueue


# TODO:
# Add annotations
# Add pre-commit hooks
# Add inline comments for classes etc
# Clean up dependencies

client_facing = APIRouter()


@client_facing.get(
    "/order/",
    response_model=ReadyOrder,
    status_code=status.HTTP_200_OK,
)
async def order():
    """
    Add an order to the queue and wait for it to be prepared.
    """
    orders_queue = OrdersQueue.get_instance()
    order_id = orders_queue.add()
    return await orders_queue.get_prepared_order(order_id)
