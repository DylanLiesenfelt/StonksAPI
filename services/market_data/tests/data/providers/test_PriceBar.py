import pydantic
import pytest

from market_data.data.providers.schemas import PriceBar

valid_data = {
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": 1_700_000_000_000
}

invalid_open = {
    "open": "not_a_number",
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": 1_700_000_000_000
}

invalid_high = {
    "open": 150.0,
    "high": "not_a_number",
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": 1_700_000_000_000
}

invalid_low = {
    "open": 150.0,
    "high": 155.0,
    "low": "not_a_number",
    "close": 152.0,
    "volume": 1000000,
    "ts": 1_700_000_000_000
}

invalid_close = {
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": "not_a_number",
    "volume": 1000000,
    "ts": 1_700_000_000_000
}

invalid_volume = {
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": "not_a_number",
    "ts": 1_700_000_000_000
}

invalid_ts = {
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.0,
    "volume": 1000000,
    "ts": "not_a_valid_timestamp"
}

invalid_data = [invalid_open, invalid_high, invalid_low, invalid_close, invalid_volume, invalid_ts]


def test_PriceBar_accepts_valid_data():
    p = PriceBar(**valid_data)
    assert p.open == 150.0
    assert p.high == 155.0
    assert p.low == 149.0
    assert p.close == 152.0
    assert p.volume == 1000000
    assert p.ts == 1_700_000_000_000
    assert isinstance(p.ts, int)


def test_PriceBar_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            PriceBar(**d)
