from typing import Optional

from pydantic import BaseModel


class Policy(BaseModel):
    database: str
    table: str
    filters: Optional[dict] = None
