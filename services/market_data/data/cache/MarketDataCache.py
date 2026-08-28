from market_data .utils import ms_now

from market_data.data.cache.schemas import CacheEntry
from market_data.service.indicators.schemas import IndicatorResult
from market_data.data.providers.schemas import QuotesResult, TickerInfoResult, PriceBarsResult


class MarketDataCache:
    # cache key will be the object type of the value + plus the ticker the data is for
    def __init__(self, ttl: int = 180):
        self.cache = {}
        self.ttl = ttl  # Configurable, Default 3 mins for staleness
        self.last_prune = ms_now()


    def get(self, ticker: str, data_type: type):
        self.prune_cache()

        entry = self.cache.get(ticker, {}).get(data_type)
        if entry:
            return entry.data
        return None


    def set(self, data: IndicatorResult | QuotesResult | TickerInfoResult | PriceBarsResult):
        self.prune_cache()

        entry = CacheEntry(
            data=data,  
            expire_at=ms_now() + self.ttl
        )
        
        self.cache.setdefault(data.ticker, {})[type(data)] = entry


    def prune_cache(self):
        now = ms_now()

        for ticker in list(self.cache.keys()):
            entries = self.cache[ticker]
            for data_type in list(entries.keys()):
                if entries[data_type].expire_at <= now:
                    del entries[data_type]
            if not entries:
                del self.cache[ticker]

        self.last_prune = now
