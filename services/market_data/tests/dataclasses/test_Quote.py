from market_data.models.schemas import Quote
from datetime import datetime
import pydantic
import pytest

valid_data = {
    "ticker": "AAPL",
    "price": 220.36,
    "ts": datetime.now()
}

invalid_ticker = {
    "ticker": 12345,  
    "price": 220.36,
    "ts": datetime.now()
}

invalid_price = {
    "ticker": "AAPL",
    "price": "not_a_number",
    "ts": datetime.now()
}

invalid_dt = {
    "ticker": "AAPL",
    "price": 220.36,
    "ts": "not_a_valid_timestamp"
}

invalid_data = [invalid_ticker, invalid_price, invalid_dt]


def test_quote_accepts_valid_data():
    quote = Quote(**valid_data)
    assert quote.ticker == "AAPL"
    assert quote.price == 220.36


def test_quote_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            Quote(**d)