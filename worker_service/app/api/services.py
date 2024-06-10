class OrderNotFoundException(Exception):
    pass


class OrdersQueue:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OrdersQueue, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            raise ValueError("OrdersQueue is not initialized")
        return cls._instance

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    def __init__(self):
        self.new_orders = set()
        self.ready_orders = set()
        self.in_progress_orders = set()

    def add_new_orders(self, new_orders: list):
        self.new_orders.update(set([new_order.id for new_order in new_orders]))

    def get_ready_orders_and_reset(self) -> list:
        ready_orders = [{"id": order} for order in self.ready_orders]
        self.ready_orders = set()
        return ready_orders

    def get_new_orders(self) -> list:
        return [{"id": order} for order in self.new_orders]

    def move_to_in_progress(self, order_id: int):
        if order_id not in self.new_orders:
            raise OrderNotFoundException(f"Order {order_id} not found in new orders.")

        self.new_orders.remove(order_id)
        self.in_progress_orders.add(order_id)

    def move_to_ready(self, order_id: int):
        self.in_progress_orders.remove(order_id)
        self.ready_orders.add(order_id)
