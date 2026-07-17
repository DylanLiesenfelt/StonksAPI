from shared import time_tools as tt

class MarketStatusService:

    async def get_market_status(self):
        
        now = tt.get_current_datetime()
        open_day = tt.is_trading_day(now)
        open_hours = tt.is_market_hours(now)
        
        return {
            "status"         : "open" if open_day and open_hours else "closed",
            "pre_market"     : tt.is_pre_market(now),
            "after_market"   : tt.is_after_hours(now),
            "holiday"        : tt.is_holiday(now),
            "date_info"      : {
                "day"        : tt.day_of_week(now),
                "date"       : now,
                "ms"         : tt.convert_to_ms(now),
            },
            "trading_days" : {
                "next_trading_day" : tt.next_trading_day(now),
                "previous_trading_day" : tt.previous_trading_day(now),
                "last_trading_day_of_week" : tt.last_trading_day_of_week(now),
                "last_trading_day_of_month" : tt.last_trading_day_of_month(now),
                "next_holiday" : tt.next_holiday(now)
            }   
        }
