from pydantic import BaseModel
from market_data.data.providers.schemas import PriceBar

class IndicatorData(BaseModel):
    request_id: dict
    ticker: str
    price_history: dict[int, PriceBar]  # ms timestamp : PriceBar
    window: int


class IndicatorResult(BaseModel):
    request_id: dict
    ticker: str
    result: dict
    indicator_method: str
    completed_at: int


class IndicatorRequest(BaseModel):
    request_id: dict
    ticker: str
    period: int
    timeframe: str
    window: int
    start: int
    end: int
    received_at: int
