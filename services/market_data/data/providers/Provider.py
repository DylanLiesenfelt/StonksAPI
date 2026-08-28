from abc import ABC, abstractmethod

from market_data.data.providers.schemas import (
    QuotesRequest,
    QuotesResult,
    TickerInfoRequest,
    TickerInfoResult,
    PriceBarsRequest,
    PriceBarsResult,
)


class Provider(ABC):
    @abstractmethod
    def get_quotes(self, request: QuotesRequest) -> QuotesResult:
        pass

    @abstractmethod
    def get_ticker_info(self, request: TickerInfoRequest) -> TickerInfoResult:
        pass

    @abstractmethod
    def get_ticker_bars(self, request: PriceBarsRequest) -> PriceBarsResult:
        pass
