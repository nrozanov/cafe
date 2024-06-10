from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
import os

from app.api.client_facing import client_facing
from app.api.services import OrdersQueue

SYNC_INTERVAL = 5


@asynccontextmanager
async def lifespan(app: FastAPI):
    orders_queue = OrdersQueue()
    scheduler = AsyncIOScheduler()
    sync_interval = os.environ.get("SYNC_INTERVAL") or SYNC_INTERVAL
    scheduler.add_job(
        func=orders_queue.sync_orders, trigger="interval", seconds=int(sync_interval)
    )
    scheduler.start()
    yield


app = FastAPI(
    openapi_url="/api/v1/client/openapi.json",
    docs_url="/api/v1/client/docs",
    lifespan=lifespan,
)

app.include_router(client_facing, prefix="/api/v1/client", tags=["client"])
