from typing import Optional

from fastapi import FastAPI
from pydantic.main import BaseModel

app = FastAPI()


class Policy(BaseModel):
    database: str
    table: str
    filters: Optional[dict] = None


@app.post('/policy', summary="add cache refresh policy")
async def add_policy(policy: Policy):
    pass
