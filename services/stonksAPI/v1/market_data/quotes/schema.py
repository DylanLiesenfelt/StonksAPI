from pydantic import BaseModel, RootModel


class Quote(BaseModel):
    name: str
    close: float
    last_updated: str


class QuotesResponse(RootModel[dict[str, Quote]]):
    pass
