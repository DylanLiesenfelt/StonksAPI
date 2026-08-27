class MarketDataService:
    def __init__(self, providers: list):
        # Register of all providers
        self.providers = providers
        self.cache = MarketDataCache() # Needs to be implemented

        def get_quote(ticker:str) -> Quote:
            pass 

        def get_quotes(tickes:list[str]) -> dict[Quote]: # changing from list to dict, key = ticker 
            pass 

        def get_ticker_info(ticker:str) -> TickerInfo: # Needs to be implemented
            pass

        def get_ticker_bars(ticker: str, start: int, end: int, )