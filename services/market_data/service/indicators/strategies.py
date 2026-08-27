import pandas as pd
from datetime import datetime

from market_data.models.schemas import PriceBar
from market_data.service.indicators.strategy import IndicatorStrategy
from market_data.service.indicators.schemas import IndicatorResult
from market_data.utils import dt_to_unixMS


class SMA(IndicatorStrategy):

    def calculate(self, history: list[PriceBar], window: int, request_id: dict):
        decomped_data = { bar.ts : bar.close for bar in history}
        s = pd.Series(decomped_data)
        d = s.rolling(window=window).mean()
        d = d.dropna().to_dict()

        return IndicatorResult(request_id=request_id, result=d, indicator_method="SMA", completed=dt_to_unixMS(datetime.now()))


class EMA(IndicatorStrategy):

    def get_sma(self, history: list[PriceBar], window: int):
        decomped_data = { bar.ts : bar.close for bar in history}
        s = pd.Series(decomped_data)
        d = s.rolling(window=window).mean()
        d = list(d.dropna().to_dict().items()) # makes the series into a list of tuples: (dt, sma)
        return d[0] 
           

    def get_multipler(self, periods: int) -> float:
        return 2 / (periods + 1)


    def get_ema(self, curr_price: float, prev_ema: float, mult: float):
        return (curr_price * mult) + (prev_ema * (1 - mult))


    def calculate(self, history: list[PriceBar],  window: int, request_id: dict):
        # get constants
        result = {}
        mult = self.get_multipler(window)

        # seed with the sma at the first complete window
        _, first_sma = self.get_sma(history, window)
        result[history[window - 1].ts] = first_sma

        # get rest of ema values
        for i in range(window, len(history)):
            result[history[i].ts] = self.get_ema(history[i].close, result[history[i-1].ts], mult)

        return IndicatorResult(request_id=request_id, result=result, indicator_method="EMA", completed=dt_to_unixMS(datetime.now()))
        

class VWAP(IndicatorStrategy):

    def get_typical_price(self, high: float, low: float, close: float ):
        return (high + low + close) / 3


    def get_pv(self, high: float, low: float, close: float, vol:float):
        tp = self.get_typical_price(high, low, close)
        return tp * vol

    
    def calculate(self, history: list[PriceBar],  window: int, request_id: dict):
        pv_data = {bar.ts: self.get_pv(bar.high, bar.low, bar.close, bar.volume) for bar in history}
        vol_data = {bar.ts: bar.volume for bar in history}

        pv = pd.Series(pv_data)
        vol = pd.Series(vol_data)

        d = pv.rolling(window=window).sum() / vol.rolling(window=window).sum()
        d = d.dropna().to_dict()

        return IndicatorResult(request_id=request_id, result=d, indicator_method="VWAP", completed=dt_to_unixMS(datetime.now()))
