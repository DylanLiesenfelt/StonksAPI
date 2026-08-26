from datetime import datetime

from market_data.models.schemas import PriceBar
from market_data.service.indicators.schemas import IndicatorResult
from market_data.service.indicators.strategies import SMA


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


def test_SMA_calculate_computes_rolling_mean():
    result = SMA().calculate(history, 3, request_id)
    expected = {
        datetime(2023, 1, 3): 2.0,
        datetime(2023, 1, 4): 3.0,
        datetime(2023, 1, 5): 4.0,
    }
    assert result.result == expected


def test_SMA_calculate_drops_incomplete_windows():
    result = SMA().calculate(history, 3, request_id)
    assert len(result.result) == len(history) - 3 + 1


def test_SMA_calculate_returns_indicator_result():
    result = SMA().calculate(history, 3, request_id)
    assert isinstance(result, IndicatorResult)
    assert result.request_id == request_id
    assert result.indicator_method == "SMA"
    assert isinstance(result.completed, int)
