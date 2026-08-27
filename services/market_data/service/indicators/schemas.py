from pydantic import BaseModel

from market_data.models.schemas import PriceBar


class IndicatorData(BaseModel):
    request_id: dict
    price_history: list[PriceBar]
    window: int


class IndicatorResult(BaseModel):
    request_id: dict
    ticker: str
    result: dict
    indicator_method: str
    completed: float


class IndicatorRequest(BaseModel):
    request_id: dict
    ticker: str
    period: int
    timeframe: str
    window: int
    start: float
    end: float
    recieved: float
