from shared.config import MASSIVE_KEY

class TickerInfoProvider:
    def __init__(self, client):
        self.client = client
        self.api_key = "apiKey=" + MASSIVE_KEY
        self.base = "https://api.massive.com/v3/reference/tickers/"


    async def get_tickerinfo(self, ticker: str, date: str|int|None):
        ticker = ticker.upper()
        if date:
            url = self.base + f"{ticker}?date={date}&" + self.api_key
        else: 
            url = self.base + f"{ticker}?" + self.api_key
        data = await self.client.fetch(url)

        result = {
            "ticker"    : data["results"]["ticker"],
            "name"      : data["results"]["name"],
            "locale"    : data["results"]["locale"].upper(),
            "active"    : data["results"]["active"],
            "marketcap" : data["results"]["market_cap"],
            "hq_state"  : data["results"]["address"]["state"].upper(),
            "logo"      : data["results"]["branding"]["logo_url"],
            "icon"      : data["results"]["branding"]["icon_url"]
        }
            
        return result