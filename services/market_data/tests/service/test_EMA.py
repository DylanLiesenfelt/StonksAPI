from datetime import datetime

from market_data.models.schemas import PriceBar
from market_data.service.indicators.schemas import IndicatorResult
from market_data.service.indicators.strategies import EMA


def make_bar(day, close):
    return PriceBar(
        ticker="AAPL",
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1000,
        ts=datetime(2023, 1, day)
    )


request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}

history = [make_bar(day, close) for day, close in enumerate([1.0, 2.0, 3.0, 4.0, 5.0], start=1)]


def test_EMA_calculate_computes_ema():
    result = EMA().calculate(history, 3, request_id)
    # mult = 2 / (3 + 1) = 0.5
    # seed (day 3) = SMA(1, 2, 3) = 2.0
    # day 4 = 4.0 * 0.5 + 2.0 * 0.5 = 3.0
    # day 5 = 5.0 * 0.5 + 3.0 * 0.5 = 4.0
    expected = {
        datetime(2023, 1, 3): 2.0,
        datetime(2023, 1, 4): 3.0,
        datetime(2023, 1, 5): 4.0,
    }
    assert result.result == expected


def test_EMA_calculate_drops_incomplete_windows():
    result = EMA().calculate(history, 3, request_id)
    assert len(result.result) == len(history) - 3 + 1


def test_EMA_calculate_returns_indicator_result():
    result = EMA().calculate(history, 3, request_id)
    assert isinstance(result, IndicatorResult)
    assert result.request_id == request_id
    assert result.indicator_method == "EMA"
    assert isinstance(result.completed, int)
