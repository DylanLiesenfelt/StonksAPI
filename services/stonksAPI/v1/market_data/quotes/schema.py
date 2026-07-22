from pydantic import BaseModel, RootModel


class Quote(BaseModel):
    ticker: str
    close: float
    updated: str


class QuotesResponse(RootModel[list[Quote]]):
    pass
