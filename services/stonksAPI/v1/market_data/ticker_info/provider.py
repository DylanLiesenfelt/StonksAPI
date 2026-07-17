from shared.config import MASSIVE_KEY

class TickerInfoProvider:
    def __init__(self, client):
        self.client = client
        self.api_key = "apiKey=" + MASSIVE_KEY
        self.base = "https://api.massive.com/"


    async def get_ticker_info(self, ticker: str, date: str|int|None):
        ticker = ticker.upper()
        if date:
            url = self.base + "v3/reference/tickers/" + f"{ticker}?date={date}&" + self.api_key
        else: 
            url = self.base + f"v3/reference/tickers/{ticker}?" + self.api_key
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
    
    async def get_related(self, ticker):
        ticker = ticker.upper()
        url = self.base + f"v1/related-companies/{ticker}?" + self.api_key 

        data = await self.client.fetch(url)
        tickers = []

        if "results" in data:
            data = data["results"]

            for t in data:
                tickers.append(t["ticker"])

        else:
            tickers.append("No Related Tickers")

        return {
            "tickers" : tickers
        }

