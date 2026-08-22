from pydantic import BaseModel
from datetime import datetime

class IndicatorPoint(BaseModel):
    value: float
    ts: datetime