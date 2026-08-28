from market_data.service.indicators.schemas import IndicatorRequest
from market_data.service.indicators.strategy import IndicatorStrategy
from market_data.data.providers.schemas import PriceBarsResult

class Indicator:
    def __int__(self, strategy: IndicatorStrategy, request: IndicatorRequest):
        self.strategy = strategy
        self.request = request
        self.data = self.get_data()
        self.history = self.data.data
        self.window = self.data.window

    def get_data(self) -> PriceBarsResult:
        pass

    def make_indicator(self):
        self.strategy.calculate(self.history, self.window)
