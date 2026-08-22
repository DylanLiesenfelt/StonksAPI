from pydantic import BaseModel

class IndicatorParams(BaseModel):
    indicator: str
    period: int
    timeframe: str