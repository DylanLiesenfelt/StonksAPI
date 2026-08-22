from pydantic import BaseModel
from datetime import datetime
# PriceBar data comes from:
# https://massive.com/docs/rest/stocks/snapshots/single-ticker-snapshot

class Quote(BaseModel):
    ticker: str
    price: float
    ts: datetime