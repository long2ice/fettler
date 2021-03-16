from fastapi import Body
from pydantic import BaseModel


class Policy(BaseModel):
    database: str = Body(..., alias="schema")
    table: str
    key: str
    filters: dict = Body(default={})
    # example
    # {
    #     "id": 1,
    #     "num": ["AND", ["GT", 1], ["LT", 1]]
    # }
    # all comparison operators: GT,GTE,LT,LTE,!EQ
    # all logic operators: AND,OR
