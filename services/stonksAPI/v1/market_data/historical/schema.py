from pydantic import BaseModel, RootModel


class Historical(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float


class HistoricalResponse(RootModel[dict[str, Historical]]):
    pass
