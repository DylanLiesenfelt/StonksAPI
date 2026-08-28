import pandas as pd
from market_data.utils import ms_now

from market_data.data.providers.schemas import PriceBar
from market_data.service.indicators.strategy import IndicatorStrategy
from market_data.service.indicators.schemas import IndicatorResult


class SMA(IndicatorStrategy):
    def calculate(self, history: dict[int, PriceBar], window: int, ticker: str, request_id: dict):
        decomped_data = {ts: bar.close for ts, bar in sorted(history.items())}
        s = pd.Series(decomped_data)
        d = s.rolling(window=window).mean()
        d = d.dropna().to_dict()

        return IndicatorResult(request_id=request_id, ticker=ticker, result=d, indicator_method="SMA", completed_at=ms_now())


class EMA(IndicatorStrategy):
    def get_sma(self, history: dict[int, PriceBar], window: int):
        decomped_data = {ts: bar.close for ts, bar in sorted(history.items())}
        s = pd.Series(decomped_data)
        d = s.rolling(window=window).mean()
        d = list(d.dropna().to_dict().items())
        return d[0]

    def get_multipler(self, periods: int) -> float:
        return 2 / (periods + 1)

    def get_ema(self, curr_price: float, prev_ema: float, mult: float):
        return (curr_price * mult) + (prev_ema * (1 - mult))

    def calculate(self, history: dict[int, PriceBar], window: int, ticker: str, request_id: dict):
        # get constants
        result = {}
        mult = self.get_multipler(window)
        bars = sorted(history.items())  # [(ts, PriceBar), ...] chronological

        # seed with the sma at the first complete window
        _, first_sma = self.get_sma(history, window)
        seed_ts, _ = bars[window - 1]
        result[seed_ts] = first_sma

        for i in range(window, len(bars)):
            ts, bar = bars[i]
            prev_ts, _ = bars[i - 1]
            result[ts] = self.get_ema(bar.close, result[prev_ts], mult)

        return IndicatorResult(request_id=request_id, ticker=ticker, result=result, indicator_method="EMA", completed_at=ms_now())


class VWAP(IndicatorStrategy):
    def get_typical_price(self, high: float, low: float, close: float):
        return (high + low + close) / 3

    # get price * volume
    def get_pv(self, high: float, low: float, close: float, vol: float):
        tp = self.get_typical_price(high, low, close)
        return tp * vol

    def calculate(self, history: dict[int, PriceBar], window: int, ticker: str, request_id: dict):
        sorted_bars = sorted(history.items())
        pv_data = {ts: self.get_pv(bar.high, bar.low, bar.close, bar.volume) for ts, bar in sorted_bars}
        vol_data = {ts: bar.volume for ts, bar in sorted_bars}

        pv = pd.Series(pv_data)
        vol = pd.Series(vol_data)

        d = pv.rolling(window=window).sum() / vol.rolling(window=window).sum()
        d = d.dropna().to_dict()

        return IndicatorResult(request_id=request_id, ticker=ticker, result=d, indicator_method="VWAP", completed_at=ms_now())


class ATR(IndicatorStrategy):
    def get_true_range(self, curr_bar: PriceBar, prev_bar: PriceBar):
        high = curr_bar.high
        low = curr_bar.low
        prev_close = prev_bar.close

        hl = high - low
        hc = abs(high - prev_close)
        lc = abs(low - prev_close)

        return max([hl, hc, lc])

    def get_atr(self, prev_atr, curr_tr, window):
        return ((prev_atr * (window - 1)) + curr_tr) / window

    def calculate(self, history: dict[int, PriceBar], window: int, ticker: str, request_id: dict):
        bars = sorted(history.items())  # [(ts, PriceBar), ...] chronological

        # get first atr, simple average of the first `window` true range values
        first_atr = sum(self.get_true_range(bars[i][1], bars[i - 1][1]) for i in range(1, window + 1)) / window

        results = {}
        results[bars[window][0]] = first_atr
        prev_atr = first_atr

        for i in range(window + 1, len(bars)):
            tr = self.get_true_range(bars[i][1], bars[i - 1][1])
            atr = self.get_atr(prev_atr, tr, window)

            results[bars[i][0]] = atr
            prev_atr = atr

        return IndicatorResult(request_id=request_id, ticker=ticker, result=results, indicator_method="ATR", completed_at=ms_now())
