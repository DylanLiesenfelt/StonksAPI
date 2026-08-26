import pandas as pd
from datetime import datetime

from market_data.models.schemas import PriceBar
from market_data.service.indicators.strategy import IndicatorStrategy
from market_data.service.indicators.schemas import IndicatorResult
from market_data.utils import dt_to_unixMS


# Indicator Methods
class SMA(IndicatorStrategy):

    def calculate(self, history: list[PriceBar], window: int, requst_id: dict):
        decomped_data = { bar.ts : bar.close for bar in history}
        s = pd.Series(decomped_data)
        d = s.rolling(window=window).mean()
        d = d.dropna().to_dict()

        return IndicatorResult(request_id=requst_id, result=d, indicator_method="SMA", completed=dt_to_unixMS(datetime.now()))
