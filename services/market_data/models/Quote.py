from pydantic import BaseModel
from datetime import datetime

class Quote(BaseModel):
    ticker: str
    price: float
    ts: datetime