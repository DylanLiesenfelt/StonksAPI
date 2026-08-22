from pydantic import BaseModel

class TickerInfo(BaseModel):
    ticker: str
    company_name: str
    hq_location: str
    logo_url: str
    market_cap: float