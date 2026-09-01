from market_data.service.indicators.schemas import IndicatorRequest, IndicatorResult
from market_data.service.indicators.strategy import IndicatorStrategy
from market_data.data.providers.schemas import PriceBarsResult

class Indicator:
    def __init__(self, strategy: IndicatorStrategy, data: PriceBarsResult, request: IndicatorRequest):
        self.strategy = strategy
        self.data = data
        self.request = request

        
    def make_indicator(self) -> IndicatorResult:
        return self.strategy.calculate(self.data, self.request)
