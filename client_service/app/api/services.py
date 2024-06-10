import asyncio
import os
import httpx

from app.api.schema import ReadyOrder

WORKER_SERVICE_HOST_URL = "http://localhost:8002/api/v1/worker/"
CHECK_FOR_READY_INTERVAL = 1


class OrdersQueue:
    _instance = None

    def __new__(cls):
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
        self.next_id = 0

    def add(self):
        self.next_id += 1
        self.new_orders.add(self.next_id)
        return self.next_id

    async def get_prepared_order(self, order_id: int) -> int:
        check_interval = (
            os.environ.get("CHECK_FOR_READY_INTERVAL") or CHECK_FOR_READY_INTERVAL
        )
        while True:
            if order_id in self.ready_orders:
                self.ready_orders.remove(order_id)
                return ReadyOrder(id=order_id)
            await asyncio.sleep(int(check_interval))

    async def sync_orders(self):
        url = os.environ.get("WORKER_SERVICE_HOST_URL") or WORKER_SERVICE_HOST_URL
        async with httpx.AsyncClient() as client:
            payload = [{"id": order_id} for order_id in self.new_orders]
            try:
                response = await client.post(f"{url}sync_orders/", json=payload)
            except Exception as e:
                print(f"An error occurred while syncing: {e}")
                return
            if response.status_code == 200:
                self.new_orders = set()
                ready_orders = response.json()
                self.ready_orders.update(
                    [ready_order["id"] for ready_order in ready_orders]
                )
            else:
                print(f"Failed sync request: {response.text}")
