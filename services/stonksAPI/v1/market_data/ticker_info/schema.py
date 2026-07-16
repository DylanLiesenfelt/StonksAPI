from pydantic import BaseModel

class TickerInfoResponse(BaseModel):
    ticker    : str
    name      : str
    locale    : str
    active    : bool
    marketcap : float
    hq_state  : str
    logo      : str
    icon      : str

class RelatedResponse(BaseModel):
    tickers : list[str] | str
