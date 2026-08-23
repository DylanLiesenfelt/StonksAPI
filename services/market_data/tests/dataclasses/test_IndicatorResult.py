from services.market_data.models.dataclasses import IndicatorResult
from datetime import datetime
import pydantic
import pytest

valid_data = {
    "indicator": "SMA",
    "timeframe": "1d",
    "points": [(100.0, datetime.now())]
}

invalid_data = [
    {"indicator": 123, "timeframe": "1d", "points": [(100.0, datetime.now())]},
    {"indicator": "SMA", "timeframe": "1d", "points": [("not_a_number", datetime.now())]},
    {"indicator": "SMA", "timeframe": "1d", "points": [(100.0, "not_a_datetime")]}
]

def test_IndicatorResult_accepts_valid_data():
    i = IndicatorResult(**valid_data)
    assert i.indicator == "SMA"
    assert i.timeframe == "1d"
    assert isinstance(i.points, list)


def test_IndicatorResult_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            IndicatorResult(**d)