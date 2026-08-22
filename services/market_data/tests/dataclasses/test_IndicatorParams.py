from services.market_data.models.dataclasses.IndicatorParams import IndicatorParams
from datetime import datetime
import pydantic
import pytest

valid_data = {
    "indicator": "SMA",
    "period": 20,
    "timeframe": "1d"
}

invalid_data = [
    {"indicator": 123, "period": 20, "timeframe": "1d"},
    {"indicator": "SMA", "period": "not_a_number", "timeframe": "1d"},
    {"indicator": "SMA", "period": 20, "timeframe": 123}
]

def test_IndicatorParams_accepts_valid_data():
    i = IndicatorParams(**valid_data)
    assert i.indicator == "SMA"
    assert i.period == 20
    assert i.timeframe == "1d"


def test_IndicatorParams_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            IndicatorParams(**d)