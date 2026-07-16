from services.stonksAPI.v1.market_data.ticker_info.provider import TickerInfoProvider
from shared.time_tools import convert_to_iso_date

class TickerInfoService:
    def __init__(self, provider: TickerInfoProvider):
        self.provider = provider

    async def get_tickerinfo(
        self,
        ticker: str,
        date: str|int|None = None
    ):

        if date:
            date = convert_to_iso_date(date)

        return await self.provider.get_tickerinfo(ticker, date)
    
    async def get_related(
        self,
        ticker: str,
    ):
        return await self.provider.get_related(ticker)