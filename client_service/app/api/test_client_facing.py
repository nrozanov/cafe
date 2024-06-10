import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.api.services import OrdersQueue


@pytest.mark.asyncio
async def test_order():
    orders_queue = OrdersQueue()
    orders_queue.add = MagicMock()
    orders_queue.add.side_effect = [1]
    orders_queue.get_prepared_order = AsyncMock()
    orders_queue.get_prepared_order.side_effect = [{"id": 1}]
    async with httpx.AsyncClient(
        app=app, base_url="http://localhost:8080/api/v1/client"
    ) as ac:
        response = await ac.get("/order/")
        assert response.status_code == 200
        assert response.json() == {"id": 1}

        assert orders_queue.add.call_count == 1
        orders_queue.get_prepared_order.assert_called_with(1)

    OrdersQueue.reset_instance()
