from market_data.data.providers.schemas import PriceBar, PriceBarsResult
from market_data.service.indicators.schemas import IndicatorRequest, IndicatorResult
from market_data.service.indicators.strategies import VWAP

DAY_MS = 86400000
BASE_TS_MS = 1672531200000  # 2023-01-01T00:00:00Z, fixed so tests are deterministic


def ts_for_day(day):
    return BASE_TS_MS + (day - 1) * DAY_MS


def make_bar(day, close, volume):
    return PriceBar(
        open=close,
        high=close,
        low=close,
        close=close,
        volume=volume,
        ts=ts_for_day(day)
    )


request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}

bars = [(1.0, 100), (2.0, 100), (3.0, 200), (4.0, 100), (5.0, 100)]
history = {ts_for_day(day): make_bar(day, close, volume) for day, (close, volume) in enumerate(bars, start=1)}

data = PriceBarsResult(request_id=request_id, ticker="AAPL", data=history)

request = IndicatorRequest(
    request_id=request_id,
    indicator_method="VWAP",
    ticker="AAPL",
    period=3,
    timeframe="day",
    multiplier=1,
    start=ts_for_day(1),
    end=ts_for_day(5),
)


def test_VWAP_calculate_computes_volume_weighted_average():
    result = VWAP().calculate(data, request)
    # window sums of (typical_price * volume) / volume:
    # day 3: (1*100 + 2*100 + 3*200) / (100+100+200) = 900 / 400 = 2.25
    # day 4: (2*100 + 3*200 + 4*100) / (100+200+100) = 1200 / 400 = 3.0
    # day 5: (3*200 + 4*100 + 5*100) / (200+100+100) = 1500 / 400 = 3.75
    expected = {
        ts_for_day(3): 2.25,
        ts_for_day(4): 3.0,
        ts_for_day(5): 3.75,
    }
    assert result.result == expected


def test_VWAP_calculate_drops_incomplete_windows():
    result = VWAP().calculate(data, request)
    assert len(result.result) == len(history) - 3 + 1


def test_VWAP_calculate_returns_indicator_result():
    result = VWAP().calculate(data, request)
    assert isinstance(result, IndicatorResult)
    assert result.request_id == request_id
    assert result.ticker == "AAPL"
