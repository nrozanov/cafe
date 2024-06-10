#!/usr/bin/env python3.10

import asyncio
import httpx
import sys
import random

BASE_URL = "http://localhost:8080/api/v1/worker"


class Worker:
    next_id = 0

    def __init__(self) -> None:
        self.id = Worker.next_id
        Worker.next_id += 1

    async def get_order_to_process(self, client: httpx.AsyncClient) -> int:
        try:
            response = await client.get(f"{BASE_URL}/start/")
        except httpx.ConnectError as e:
            print(f"An error occurred while getting order to process: {e}")
            return None
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return min(item["id"] for item in data)

    async def run(self):
        print(f"Start running worker {self.id}")
        async with httpx.AsyncClient() as client:
            while True:
                order_id = await self.get_order_to_process(client)
                if order_id is None:
                    await asyncio.sleep(1)
                    continue

                response = await client.get(f"{BASE_URL}/start_order/{order_id}/")
                if response.status_code != 200:
                    continue

                print(f"Worker {self.id} started order {order_id}")

                await asyncio.sleep(random.randint(30, 60))
                print(f"Worker {self.id} finished order {order_id}")
                await client.post(f"{BASE_URL}/finish/{order_id}/")


async def main():
    workers = [Worker() for _ in range(int(sys.argv[1]))]
    print(f"Starting {len(workers)} workers")
    tasks = [worker.run() for worker in workers]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
