from pydantic import BaseModel


class ReadyOrder(BaseModel):
    id: int
