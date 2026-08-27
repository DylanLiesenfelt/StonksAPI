from pydantic import BaseModel
from market_data.service.indicators.schemas import IndicatorResult
from market_data.models.schemas import Quote, TickerInfo, PriceBar

class CacheEntry(BaseModel):
    data: IndicatorResult | Quote | TickerInfo | PriceBar
    created_at: float
    expire_at: float
