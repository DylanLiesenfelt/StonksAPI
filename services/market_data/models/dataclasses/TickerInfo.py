from pydantic import BaseModel

# TickerInfo data comes from:
# https://massive.com/docs/rest/stocks/tickers/ticker-overview

class TickerInfo(BaseModel):
    ticker: str
    company_name: str
    hq_location: str
    logo_url: str
    market_cap: float