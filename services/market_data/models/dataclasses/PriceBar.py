from pydantic import BaseModel
from datetime import datetime

# PriceBar data comes from:
# https://massive.com/docs/rest/stocks/aggregates/custom-bars

class PriceBar(BaseModel):
    ticker: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    ts: datetime