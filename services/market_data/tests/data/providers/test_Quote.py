import pydantic
import pytest

from market_data.data.providers.schemas import Quote

valid_data = {
    "price": 220.36,
    "ts": 1_700_000_000_000
}

invalid_price = {
    "price": "not_a_number",
    "ts": 1_700_000_000_000
}

invalid_ts = {
    "price": 220.36,
    "ts": "not_a_valid_timestamp"
}

invalid_data = [invalid_price, invalid_ts]


def test_Quote_accepts_valid_data():
    quote = Quote(**valid_data)
    assert quote.price == 220.36
    assert quote.ts == 1_700_000_000_000
    assert isinstance(quote.ts, int)


def test_Quote_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            Quote(**d)
