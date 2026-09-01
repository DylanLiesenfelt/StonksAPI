from market_data.data.providers.MassiveProvider import MASSIVE
from market_data.data.providers.schemas import  (
    QuotesRequest, QuotesResult,
    TickerInfoRequest, TickerInfoResult,
    PriceBarsRequest, PriceBarsResult
)

from market_data.service.indicators.schemas import IndicatorRequest, IndicatorResult
from market_data.service.indicators.indicator import Indicator
from market_data.service.indicators.strategies import (
    SMA, EMA, ATR, VWAP
)

class MarketDataService:
    def __init__(self):
        self.provider = MASSIVE
        self.indicator_register = {
            "SMA" : SMA,
            "EMA" : EMA,
            "VWAP" : VWAP,
            "ATR" : ATR
        }

    def get_quotes(self, request: QuotesRequest) -> QuotesResult:
        return self.provider.get_quotes(request)

    def get_ticker_info(self, request: TickerInfoRequest) -> TickerInfoResult:
        return self.provider.get_ticker_info(request)

    def get_ticker_bars(self, request: PriceBarsRequest) -> PriceBarsResult:
        return self.provider.get_ticker_bars(request)

    def get_indicator(self, request: IndicatorRequest) -> IndicatorResult:
        data_request = PriceBarsRequest(
            request_id=request.request_id,
            ticker=request.ticker,
            multiplier=request.multiplier,
            timeframe=request.timeframe,
            start=request.start,
            end=request.end
        )

        price_bar_data = self.get_ticker_bars(data_request)
        strategy = self.indicator_register[request.indicator_method]
        i = Indicator(strategy=strategy(), data=price_bar_data, request=request)

        return i.make_indicator()
