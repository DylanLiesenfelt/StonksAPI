from market_data.service.indicators.schemas import IndicatorRequest
from market_data.service.indicators.strategy import IndicatorStrategy


class Indicator:
    def __int__(self, strategy: IndicatorStrategy, request: IndicatorRequest):
        self.strategy = strategy
        self.request = request
        # self.client = client
        self.data = self.get_data()
        self.history = self.data.price_history
        self.window = self.data.window

    '''def get_data(self):
        res = client.tbd_getdata()
        # parse into indicator data
        data = IndicatorData()
        return data'''

    def make_indicator(self):
        self.strategy.calculate(self.history, self.window)
