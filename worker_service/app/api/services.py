from typing import Type

from app.api.schema import Order


class OrderNotFoundException(Exception):
    pass


class OrdersQueue:
    _instance = None

    def __new__(cls: Type["OrdersQueue"]) -> "OrdersQueue":
        if not cls._instance:
            cls._instance = super(OrdersQueue, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls: Type["OrdersQueue"]) -> "OrdersQueue":
        if not cls._instance:
            raise ValueError("OrdersQueue is not initialized")
        return cls._instance

    @classmethod
    def reset_instance(cls: Type["OrdersQueue"]) -> None:
        cls._instance = None

    def __init__(self) -> None:
        self.new_orders = set()
        self.ready_orders = set()
        self.in_progress_orders = set()

    def add_new_orders(self, new_orders: list[Order]) -> None:
        self.new_orders.update(set([new_order.id for new_order in new_orders]))

    def get_ready_orders_and_reset(self) -> list[Order]:
        ready_orders = [Order(id=order_id) for order_id in self.ready_orders]
        self.ready_orders = set()
        return ready_orders

    def get_new_orders(self) -> list[Order]:
        return [Order(id=order_id) for order_id in self.new_orders]

    def move_to_in_progress(self, order_id: int) -> None:
        if order_id not in self.new_orders:
            raise OrderNotFoundException(f"Order {order_id} not found in new orders.")

        self.new_orders.remove(order_id)
        self.in_progress_orders.add(order_id)

    def move_to_ready(self, order_id: int) -> None:
        self.in_progress_orders.remove(order_id)
        self.ready_orders.add(order_id)
