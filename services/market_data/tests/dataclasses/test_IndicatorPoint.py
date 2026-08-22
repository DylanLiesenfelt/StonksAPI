from services.market_data.models.dataclasses.IndicatorPoint import IndicatorPoint
import pydantic
import pytest

from datetime import datetime

valid_data = {
    "value": 100.0,
    "ts": datetime.now()
}

invalid_data = [
    {"value": "not_a_number", "ts": datetime.now()},
    {"value": 100.0, "ts": "not_a_datetime"}
]

def test_IndicatorPoint_accepts_valid_data():
    i = IndicatorPoint(**valid_data)
    assert i.value == 100.0
    assert isinstance(i.ts, datetime)


def test_IndicatorPoint_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            IndicatorPoint(**d)