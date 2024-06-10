import httpx
import pytest

from app.main import app
from app.api.schema import Order
from app.api.services import OrdersQueue


class TestWorkerFacing:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.orders_queue = OrdersQueue()
        self.orders_queue.add_new_orders([Order(id=1), Order(id=2)])

        yield
        OrdersQueue.reset_instance()

    @pytest.mark.asyncio
    async def test_sync_orders(self):
        self.orders_queue.ready_orders = {3, 4}
        async with httpx.AsyncClient(
            app=app, base_url="http://localhost:8080/api/v1/worker"
        ) as ac:
            payload = [{"id": 5}, {"id": 6}]
            response = await ac.post("/sync_orders/", json=payload)
            assert response.status_code == 200
            assert response.json() == [{"id": 3}, {"id": 4}]

            assert self.orders_queue.new_orders == {1, 2, 5, 6}
            assert self.orders_queue.ready_orders == set()

    @pytest.mark.asyncio
    async def test_get_orders(self):
        async with httpx.AsyncClient(
            app=app, base_url="http://localhost:8080/api/v1/worker"
        ) as ac:
            response = await ac.get("/start/")
            assert response.status_code == 200
            assert response.json() == [{"id": 1}, {"id": 2}]

    @pytest.mark.asyncio
    async def test_start_order(self):
        async with httpx.AsyncClient(
            app=app, base_url="http://localhost:8080/api/v1/worker"
        ) as ac:
            response = await ac.get("/start_order/1/")
            assert response.status_code == 200
            assert self.orders_queue.new_orders == {2}
            assert self.orders_queue.in_progress_orders == {1}

    @pytest.mark.asyncio
    async def test_start_unknown_order(self):
        async with httpx.AsyncClient(
            app=app, base_url="http://localhost:8080/api/v1/worker"
        ) as ac:
            response = await ac.get("/start_order/3/")
            assert response.status_code == 404
            assert self.orders_queue.new_orders == {1, 2}
            assert self.orders_queue.in_progress_orders == set()

    @pytest.mark.asyncio
    async def test_finish_order(self):
        self.orders_queue.move_to_in_progress(1)
        async with httpx.AsyncClient(
            app=app, base_url="http://localhost:8080/api/v1/worker"
        ) as ac:
            response = await ac.post("/finish/1/")
            assert response.status_code == 200
            assert self.orders_queue.in_progress_orders == set()
            assert self.orders_queue.ready_orders == {1}
