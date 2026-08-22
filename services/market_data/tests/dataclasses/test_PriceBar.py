from market_data.models.dataclasses.PriceBar import PriceBar
from datetime import datetime
import pydantic
import pytest

valid_data = {
    "ticker": "AAPL",
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": datetime.now()
}

invalid_ticker = {
   "ticker" : 12345,
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": datetime.now()
}

invalid_open = {
    "ticker": "AAPL",
    "open": "not_a_number",
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": datetime.now()     
}

invalid_high = {
    "ticker": "AAPL",
    "open": 150.0,         
    "high": "not_a_number",
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": datetime.now()       
}

invalid_low = {
    "ticker": "AAPL",
    "open": 150.0,
    "high": 155.0,
    "low": "not_a_number",
    "close": 152.0,
    "volume": 1000000,
    "ts": datetime.now()
}

invalid_close = {
    "ticker": "AAPL",
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": "not_a_number",
    "volume": 1000000,
    "ts": datetime.now()
}

invalid_volume = {
    "ticker": "AAPL",
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": "not_a_number",
    "ts": datetime.now()
}

invalid_dt = {
    "ticker": "AAPL",
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": "not_a_valid_timestamp"
}

invalid_data = [invalid_ticker, invalid_open, invalid_high, invalid_low, invalid_close, invalid_volume, invalid_dt]


def test_PriceBar_accepts_valid_data():
    p = PriceBar(**valid_data)
    assert p.ticker == "AAPL"
    assert p.open == 150.0
    assert p.high == 155.0
    assert p.low == 149.0
    assert p.close == 152.0
    assert p.volume == 1000000
    assert isinstance(p.ts, datetime)


def test_PriceBar_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            PriceBar(**d)