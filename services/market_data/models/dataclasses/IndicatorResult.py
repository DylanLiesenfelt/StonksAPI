from pydantic import BaseModel
from datetime import datetime

class IndicatorResult(BaseModel):
    indicator: str
    timeframe: str
    points: list[tuple[float, datetime]]