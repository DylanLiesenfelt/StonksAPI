from datetime import datetime

from market_data.models.schemas import PriceBar
from market_data.service.indicators.schemas import IndicatorResult
from market_data.service.indicators.strategies import VWAP


def make_bar(day, close, volume):
    return PriceBar(
        ticker="AAPL",
        open=close,
        high=close,
        low=close,
        close=close,
        volume=volume,
        ts=datetime(2023, 1, day)
    )


request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}

bars = [(1.0, 100), (2.0, 100), (3.0, 200), (4.0, 100), (5.0, 100)]
history = [make_bar(day, close, volume) for day, (close, volume) in enumerate(bars, start=1)]


def test_VWAP_calculate_computes_volume_weighted_average():
    result = VWAP().calculate(history, 3, request_id)
    # window sums of (typical_price * volume) / volume:
    # day 3: (1*100 + 2*100 + 3*200) / (100+100+200) = 900 / 400 = 2.25
    # day 4: (2*100 + 3*200 + 4*100) / (100+200+100) = 1200 / 400 = 3.0
    # day 5: (3*200 + 4*100 + 5*100) / (200+100+100) = 1500 / 400 = 3.75
    expected = {
        datetime(2023, 1, 3): 2.25,
        datetime(2023, 1, 4): 3.0,
        datetime(2023, 1, 5): 3.75,
    }
    assert result.result == expected


def test_VWAP_calculate_drops_incomplete_windows():
    result = VWAP().calculate(history, 3, request_id)
    assert len(result.result) == len(history) - 3 + 1


def test_VWAP_calculate_returns_indicator_result():
    result = VWAP().calculate(history, 3, request_id)
    assert isinstance(result, IndicatorResult)
    assert result.request_id == request_id
    assert result.indicator_method == "VWAP"
    assert isinstance(result.completed, int)
