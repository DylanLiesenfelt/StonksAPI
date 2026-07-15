from services.stonksAPI.v1.market_data.historical.provider import HistoricalProvider
from shared.time_tools import convert_to_ms, convert_date_to_ms, get_current_datetime, get_default_startdate

class HistoricalService:
    def __init__(self, provider: HistoricalProvider):
        self.provider = provider

    async def get_historical(
            self,
            ticker: str,
            interval: int = 15,
            timeframe: str = "day",
            start_date: str|int|None = None,
            end_date: str|int|None = None
        ):
        if start_date is None:
            start_date = convert_to_ms(get_default_startdate())
        elif isinstance(start_date, str):
            start_date = convert_date_to_ms(start_date)

        if end_date is None:
            end_date = convert_to_ms(get_current_datetime())
        elif isinstance(end_date, str):
            end_date = convert_date_to_ms(end_date, end_of_day=True)

        return await self.provider.get_historical(ticker, interval, timeframe, start_date, end_date)
