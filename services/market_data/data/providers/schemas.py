from pydantic import BaseModel

# https://massive.com/docs/rest/stocks/aggregates/custom-bars
class PriceBarsRequest(BaseModel):
    request_id: dict[str,str] # global_id : UUID, request_id : UUID
    ticker: str
    window: int # size of the bar, 1,5,15 etc...
    timeframe: str # min, day, etc...
    start: int
    end: int
    received_at: int


class PriceBar(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: int
    ts: int 


class PriceBarsResult(BaseModel):
    request_id: dict[str,str]
    ticker: str
    data: dict[int, PriceBar] # ms timestamp: PriceBar
    completed_at: int


# Quote data comes from:
# https://massive.com/docs/rest/stocks/snapshots/single-ticker-snapshot
class QuotesRequest(BaseModel):
    request_id: dict[str,str]
    tickers: list[str]
    received_at: int


class Quote(BaseModel):
    price: float
    ts: int


class QuotesResult(BaseModel):
    request_id: dict[str,str]
    tickers: list[str]
    data: dict[str, Quote] # ticker : Quote
    completed_at: int
    

# Ticker Info data comes from:
# https://massive.com/docs/rest/stocks/tickers/ticker-overview

class TickerInfoRequest(BaseModel):
    request_id : dict[str,str]
    ticker: str
    received_at: int


class TickerInfoResult(BaseModel):
    request_id: dict[str,str]
    ticker: str
    company_name: str
    hq_location: dict[str, str]  # {"city": ..., "state": ...}
    logo_url: str
    market_cap: float
    completed_at: int


