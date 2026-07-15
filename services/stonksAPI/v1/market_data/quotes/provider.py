from shared.config import MASSIVE_KEY
from shared.time_tools import convert_from_ns

class QuotesProvider:
    def __init__(self, client):
        self.client = client
        self.api_key = "&apiKey=" + MASSIVE_KEY
        self.base = "https://api.massive.com/v3/snapshot?"


    async def get_quotes(self, tickers: list[str] = None):
        result = {}
        if not tickers:
            return result

        url = self.base + "order=asc&limit=250&sort=ticker&ticker.any_of=" + "%2C".join(t.upper() for t in tickers) + self.api_key
        data = await self.client.fetch(url)

        for item in data["results"]:
            last_minute = item.get("last_minute")
            if not last_minute:
                continue
            result[item["ticker"]] = {
                "name": item["name"],
                "close": last_minute["close"],
                "last_updated": convert_from_ns(last_minute["last_updated"])
            }

        return result