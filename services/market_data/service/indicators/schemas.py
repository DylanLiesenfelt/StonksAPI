from pydantic import BaseModel

class IndicatorResult(BaseModel):
    request_id: dict[str,str]
    ticker: str
    result: dict


class IndicatorRequest(BaseModel):
    request_id: dict[str,str]
    indicator_method: str
    ticker: str
    period: int # number of bars to roll over for the indicator calculation, e.g. 20-period SMA
    timeframe: str
    multiplier: int # size of the underlying price bar, forwarded to PriceBarsRequest.multiplier
    start: int
    end: int
