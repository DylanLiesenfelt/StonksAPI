from collections import deque

import pandas as pd

from market_data.data.providers.schemas import PriceBarsResult, PriceBar
from market_data.service.indicators.strategy import IndicatorStrategy
from market_data.service.indicators.schemas import IndicatorRequest, IndicatorResult


class SMA(IndicatorStrategy):
    def calculate(self, data:PriceBarsResult, request: IndicatorRequest ) -> IndicatorResult:
        bars = {ts : bar.close for ts, bar in  data.data.items()}

        s = pd.Series(bars)
        d = s.rolling(window=request.period).mean()
        d = d.dropna().to_dict()

        return IndicatorResult(
            request_id=request.request_id,
            ticker=request.ticker,
            result=d
        )


class EMA(IndicatorStrategy):
    def get_multipler(self, periods: int) -> float:
        return 2 / (periods + 1)

    def get_ema(self, curr_price: float, prev_ema: float, mult: float):
        return (curr_price * mult) + (prev_ema * (1 - mult))

    def calculate(self, data:PriceBarsResult, request: IndicatorRequest ) -> IndicatorResult:
        result = {}
        mult = self.get_multipler(request.period)
        seed_closes = deque(maxlen=request.period)
        prev_ema = None

        for ts, bar in data.data.items():
            if prev_ema is None:
                seed_closes.append(bar.close)
                if len(seed_closes) < request.period:
                    continue
                prev_ema = sum(seed_closes) / request.period
            else:
                prev_ema = self.get_ema(bar.close, prev_ema, mult)

            result[ts] = prev_ema

        return IndicatorResult(
            request_id=request.request_id,
            ticker=request.ticker,
            result=result
        )


class VWAP(IndicatorStrategy):
    def get_typical_price(self, high: float, low: float, close: float):
        return (high + low + close) / 3

    def get_price_x_volume(self, high: float, low: float, close: float, vol: float):
        tp = self.get_typical_price(high, low, close)
        return tp * vol

    def calculate(self, data:PriceBarsResult, request: IndicatorRequest ) -> IndicatorResult:
        bars = data.data.items()
        pv_data = {
            ts : self.get_price_x_volume(
                bar.high, 
                bar.low,
                bar.close,
                bar.volume
            ) for ts, bar in bars
        }
        vol_data = {ts : bar.volume for ts, bar in bars}

        pv = pd.Series(pv_data)
        vol = pd.Series(vol_data)

        d = pv.rolling(window=request.period).sum() / vol.rolling(window=request.period).sum()
        d = d.dropna().to_dict()

        return IndicatorResult(
            request_id=request.request_id,
            ticker=request.ticker,
            result=d
        )


class ATR(IndicatorStrategy):
    def get_true_range(self, curr_bar: PriceBar, prev_bar: PriceBar):
        high = curr_bar.high
        low = curr_bar.low
        prev_close = prev_bar.close

        hl = high - low
        hc = abs(high - prev_close)
        lc = abs(low - prev_close)

        return max([hl, hc, lc])

    def get_atr(self, prev_atr, curr_tr, period):
        return ((prev_atr * (period - 1)) + curr_tr) / period

    def calculate(self, data:PriceBarsResult, request: IndicatorRequest ) -> IndicatorResult:
        results = {}
        prev_bar = None
        seed_trs = deque(maxlen=request.period)
        prev_atr = None

        for ts, bar in data.data.items():
            if prev_bar is None:
                prev_bar = bar
                continue

            tr = self.get_true_range(bar, prev_bar)
            prev_bar = bar

            if prev_atr is None:
                seed_trs.append(tr)
                if len(seed_trs) < request.period:
                    continue
                prev_atr = sum(seed_trs) / request.period
            else:
                prev_atr = self.get_atr(prev_atr, tr, request.period)

            results[ts] = prev_atr

        return IndicatorResult(
            request_id=request.request_id,
            ticker=request.ticker,
            result=results
        )
