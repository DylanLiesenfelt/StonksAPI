from services.stonksAPI.v1.market_data.quotes.provider import QuotesProvider

class QuotesService:
    def __init__(self, provider: QuotesProvider):
        self.provider = provider

    async def get_quotes(self, tickers: list[str]):
        return await self.provider.get_quotes(tickers)
