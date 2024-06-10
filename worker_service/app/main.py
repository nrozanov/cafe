from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.worker_facing import worker_facing
from app.api.services import OrdersQueue


@asynccontextmanager
async def lifespan(app: FastAPI):
    OrdersQueue()
    yield


app = FastAPI(
    openapi_url="/api/v1/worker/openapi.json",
    docs_url="/api/v1/worker/docs",
    lifespan=lifespan,
)

app.include_router(worker_facing, prefix="/api/v1/worker", tags=["worker"])
