from pydantic import BaseModel

# PriceBar data comes from:
# https://massive.com/docs/rest/stocks/aggregates/custom-bars
class PriceBar(BaseModel):
    ticker: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    ts: float

# PriceBar data comes from:
# https://massive.com/docs/rest/stocks/snapshots/single-ticker-snapshot
class Quote(BaseModel):
    ticker: str
    price: float
    ts: float

# TickerInfo data comes from:
# https://massive.com/docs/rest/stocks/tickers/ticker-overview
class TickerInfo(BaseModel):
    ticker: str
    company_name: str
    hq_location: str
    logo_url: str
    market_cap: float