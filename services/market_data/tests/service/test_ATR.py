from datetime import datetime

from market_data.models.schemas import PriceBar
from market_data.service.indicators.schemas import IndicatorResult
from market_data.service.indicators.strategies import ATR


def make_bar(day, high, low, close):
    return PriceBar(
        ticker="AAPL",
        open=close,
        high=high,
        low=low,
        close=close,
        volume=1000,
        ts=datetime(2023, 1, day)
    )


request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}

bars = [
    (10, 8, 9),
    (13, 9, 11),
    (12, 10, 11),
    (15, 11, 13),
    (14, 12, 13),
]
history = [make_bar(day, high, low, close) for day, (high, low, close) in enumerate(bars, start=1)]


def test_ATR_calculate_computes_wilder_smoothed_average():
    result = ATR().calculate(history, 2, request_id)
    # true ranges (using prev bar's close):
    # day 2: max(13-9, |13-9|, |9-9|)   = 4
    # day 3: max(12-10, |12-11|, |10-11|) = 2
    # day 4: max(15-11, |15-11|, |11-11|) = 4
    # day 5: max(14-12, |14-13|, |12-13|) = 2
    # seed (day 3) = avg(TR day2, TR day3) = avg(4, 2) = 3.0
    # day 4 = ((3.0 * (2-1)) + 4) / 2 = 3.5
    # day 5 = ((3.5 * (2-1)) + 2) / 2 = 2.75
    expected = {
        datetime(2023, 1, 3): 3.0,
        datetime(2023, 1, 4): 3.5,
        datetime(2023, 1, 5): 2.75,
    }
    assert result.result == expected


def test_ATR_calculate_drops_incomplete_windows():
    result = ATR().calculate(history, 2, request_id)
    # ATR needs an extra prior bar for the first true range, so it yields
    # one fewer point than SMA/EMA/VWAP would for the same window
    assert len(result.result) == len(history) - 2


def test_ATR_calculate_returns_indicator_result():
    result = ATR().calculate(history, 2, request_id)
    assert isinstance(result, IndicatorResult)
    assert result.request_id == request_id
    assert result.indicator_method == "ATR"
    assert isinstance(result.completed, int)
