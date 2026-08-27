import time

from market_data.data.cache.schemas import CacheEntry
from market_data.service.indicators.schemas import IndicatorResult
from market_data.models.schemas import Quote, TickerInfo, PriceBar


class MarketDataCache:
    # cache key will be the object type of the value + plus the ticker the data is for
    def __init__(self, ttl: int = 180):
        self.cache = {}
        self.ttl = ttl  # Configurable, Default 3 mins for staleness
        self.last_prune = time.time()

    def get(self, ticker: str, data_type: type):
        self.prune_cache()

        entry = self.cache.get(ticker, {}).get(data_type)
        if entry:
            return entry.data
        return None

    def set(self, data: IndicatorResult | Quote | TickerInfo | PriceBar):
        self.prune_cache()

        entry = CacheEntry(
            data=data, 
            created_at=time.time(), 
            expire_at=time.time() + self.ttl
        )
        
        self.cache.setdefault(data.ticker, {})[type(data)] = entry

    def prune_cache(self):
        now = time.time()

        for ticker in list(self.cache.keys()):
            entries = self.cache[ticker]
            for data_type in list(entries.keys()):
                if entries[data_type].expire_at <= now:
                    del entries[data_type]
            if not entries:
                del self.cache[ticker]

        self.last_prune = now
