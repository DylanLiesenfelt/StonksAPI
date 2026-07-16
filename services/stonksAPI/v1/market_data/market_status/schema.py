from pydantic import BaseModel

class MarketStatus(BaseModel):
    status: str
    pre_market: bool
    after_market: bool
    holiday: bool
    date_info: dict[str, str | int]
    trading_days: dict[str, str | tuple[str, int | None]]
