import pytest

from app.api.schema import Order
from app.api.services import OrdersQueue


class TestOrdersQueue:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.queue = OrdersQueue()

        yield
        OrdersQueue.reset_instance()

    def test_singleton(self):
        queue = OrdersQueue()
        assert self.queue == queue

    def test_add_new_orders(self):
        self.queue.add_new_orders([Order(id=1), Order(id=2)])
        assert self.queue.new_orders == {1, 2}
        self.queue.add_new_orders([Order(id=3)])
        assert self.queue.new_orders == {1, 2, 3}

    def test_get_ready_orders_and_reset(self):
        self.queue.ready_orders = {1, 2}
        assert self.queue.get_ready_orders_and_reset() == [{"id": 1}, {"id": 2}]
        assert self.queue.ready_orders == set()

    def test_get_new_orders(self):
        self.queue.add_new_orders([Order(id=1), Order(id=2)])
        assert self.queue.get_new_orders() == [{"id": 1}, {"id": 2}]

    def test_move_to_in_progress(self):
        self.queue.add_new_orders([Order(id=1), Order(id=2)])
        self.queue.move_to_in_progress(1)
        assert self.queue.new_orders == {2}
        assert self.queue.in_progress_orders == {1}

    def test_move_to_ready(self):
        self.queue.add_new_orders([Order(id=1), Order(id=2)])
        self.queue.move_to_in_progress(1)
        self.queue.move_to_ready(1)
        assert self.queue.in_progress_orders == set()
        assert self.queue.ready_orders == {1}
