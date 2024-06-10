import asyncio
from fastapi.testclient import TestClient
import pytest
from unittest.mock import AsyncMock

from app.main import app
from app.api.services import OrdersQueue


@pytest.mark.asyncio
async def test_lifespan():
    orders_queue = OrdersQueue()
    orders_queue.sync_orders = AsyncMock()
    with TestClient(app):
        assert orders_queue.sync_orders.call_count == 0
        await asyncio.sleep(5)
        assert orders_queue.sync_orders.call_count == 1

    OrdersQueue.reset_instance()
