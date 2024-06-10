import asyncio
import pytest
import respx
from httpx import Response

from app.api.schema import ReadyOrder
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

    def test_add(self):
        assert self.queue.add() == 1
        assert self.queue.add() == 2

    @pytest.mark.asyncio
    async def test_get_prepared_order(self):
        order_promise = asyncio.create_task(self.queue.get_prepared_order(1))
        await asyncio.sleep(1)
        assert not order_promise.done()

        self.queue.ready_orders.add(1)
        await asyncio.sleep(1)
        assert order_promise.done()
        assert await order_promise == ReadyOrder(id=1)

    @pytest.mark.asyncio
    async def test_sync_orders(self):
        self.queue.new_orders = {1, 2}
        self.queue.ready_orders = {3}
        url = "http://localhost:8002/api/v1/worker/sync_orders/"
        with respx.mock:
            respx.post(url).mock(
                return_value=Response(200, json=[{"id": 4}, {"id": 5}])
            )

            await self.queue.sync_orders()

            assert self.queue.new_orders == set()
            assert self.queue.ready_orders == {3, 4, 5}
