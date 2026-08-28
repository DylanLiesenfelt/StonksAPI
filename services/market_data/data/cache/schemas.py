from pydantic import BaseModel
from market_data.service.indicators.schemas import IndicatorResult
from market_data.data.providers.schemas import QuotesResult, TickerInfoResult, PriceBarsResult

class CacheEntry(BaseModel):
    data: IndicatorResult | QuotesResult | TickerInfoResult | PriceBarsResult
    expire_at: int
