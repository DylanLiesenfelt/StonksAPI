from shared.config import MASSIVE_KEY
from shared.time_tools import convert_from_ms, is_market_hours

INTRADAY_TIMEFRAMES = {"minute", "hour"}

class HistoricalProvider:
    def __init__(self, client):
        self.client = client
        self.api_key = "&apiKey=" + MASSIVE_KEY
        self.base = "https://api.massive.com/v2/aggs/ticker/"


    async def get_historical(self, ticker: str, interval: int, timeframe: str, start_date: str|int, end_date: str|int):
        result = {}

        url = self.base + f"{ticker.upper()}/range/{interval}/{timeframe}/{start_date}/{end_date}?adjusted=true&sort=asc&limit=50000" + self.api_key
        data = await self.client.fetch(url)

        for entry in data["results"]:
            date_str = convert_from_ms(entry["t"])
            if timeframe in INTRADAY_TIMEFRAMES and not is_market_hours(date_str):
                continue

            result[date_str] = {
                "open": entry["o"],
                "high": entry["h"],
                "low": entry["l"],
                "close": entry['c'],
                "volume": entry["v"]
            }

        return result