# Market Data ADRs

## 001 Indicator Restructuring

Date: 26 AUG 2026

### Context

The original implementation of handling indicator calculations, such as SMA, was obtuse and unnecessary. It used data classes to represent Indicator Parameters, Indicator Points, and Indicator Results, and placed `IndicatorStrategy` under `models/indicators/`.

`IndicatorParams` defeated the whole purpose of using a strategy design pattern: the param class took the indicator method as a value, which is not needed. The indicator method being used is implicit in which concrete `IndicatorStrategy` subclass is called, so the calculation itself does not care which method was selected. Further, the calculations are timeframe (minute, day, month) and period (how wide our data set is) agnostic, they only care about the data passed in (`PriceBar` data) and the window for the sliding window.

`IndicatorPoint` was also unnecessary, just a bloated tuple of value and timestamp that a plain key-value pair in a dict can represent just as well, making the dataclass pointless and inefficient.

`IndicatorResult` had the same problem: it carried the indicator method and timeframe (both implicit to the request, not the result) alongside a list of `IndicatorPoint` objects, which, per the point above, collapses into a single `dict`.

Per `ARCHITECTURE.md`, `models/` must stay plain classes with no knowledge of HTTP, databases, or other services, while `service/` is where business/application logic is orchestrated. `IndicatorStrategy` and its concrete indicators depend on pandas and encode the actual calculation logic, which is business logic, not a plain model, so keeping it under `models/indicators/` violated that layer split.

We were taking a very OOP approach, and overall still are, but simplified things considerably by pushing everything into each strategy's `calculate()` method, implemented with pandas instead of vanilla Python. Pandas was chosen specifically because its core is backed by compiled C and Cython code (via NumPy), so calculating indicators over large data sets is significantly more efficient than doing the same rolling-window math in vanilla Python.

Once `IndicatorStrategy`, `Indicator`, the DTOs, and every concrete `calculate()` implementation all lived together in one `service/Indicator.py` file, that file had multiple reasons to change: a new indicator, a DTO field change, and a change to the orchestration logic would all touch the same file. Splitting along those seams keeps each piece testable and changeable on its own, and keeps Open/Closed intact for adding new indicators.

### Decision

- Deleted `IndicatorParams` and `IndicatorPoint`, and deleted `models/indicators/IndicatorStrategy.py`.
- `IndicatorData`, `IndicatorResult`, and `IndicatorRequest` are kept, but rebuilt as Pydantic `BaseModel`s, since they represent service-layer request/response shapes rather than plain domain models. `PriceBar`, `Quote`, and `TickerInfo` remain the only classes in `models/schemas.py`; they are independent leaf models with no strategy-style growth axis, so they were left as one file rather than split.
- `IndicatorResult.result` is now a plain `dict` (timestamp key to value) instead of a `list[IndicatorPoint]`. Neither `IndicatorData` nor `IndicatorResult` carries an indicator-method field anymore, since that's implicit in the concrete `IndicatorStrategy` subclass used, not passed as data.
- The old single `service/Indicator.py` file was split into a `service/indicators/` package, so each concern has its own module:
  - `service/indicators/schemas.py`: the DTOs, `IndicatorData`, `IndicatorResult`, `IndicatorRequest`.
  - `service/indicators/strategy.py`: `IndicatorStrategy`, the `ABC` declaring the strategy interface, just the abstract `calculate()`.
  - `service/indicators/indicator.py`: `Indicator`, the context object that pairs a strategy with a request and drives `strategy.calculate(...)`, kept separate from the strategy interface it depends on.
  - `service/indicators/strategies.py`: concrete strategies, currently just `SMA`. New indicators (`EMA`, `VWAP`, `ATR`) are added here without touching the interface or the DTOs.
  - `service/indicators/__init__.py` re-exports all of the above so callers can still do `from market_data.service.indicators import SMA, IndicatorData, ...`.
- `SMA(IndicatorStrategy)` is the first concrete strategy. `SMA.calculate()` takes `history: list[PriceBar]`, `window: int`, and `request_id: dict` directly as arguments (no params object), builds a pandas `Series` from `PriceBar.close` keyed by `PriceBar.ts`, and computes the moving average with `Series.rolling(window).mean()`.
- Fetching the underlying `PriceBar` data (`Indicator.get_data`) is stubbed out pending client integration.
- The indicator strategy moved from `models/indicators/` to `service/indicators/`, since it's business logic per `ARCHITECTURE.md`, not a plain model.
- `dt_to_unixMS()` and `unixMS_to_dt()` moved out of `IndicatorStrategy` into `market_data/utils.py` as plain functions. They never used `self`, they're generic timestamp conversion, not indicator-specific behavior, so keeping them on the strategy interface only forced every concrete strategy to inherit unrelated helpers. `SMA.calculate()` now calls `dt_to_unixMS()` directly instead of `self.dt_to_unixMS()`.

### Consequences

- Less OOP overall, but calculations stay single-responsibility (one strategy per indicator) and the design stays open/closed: new indicators are added as a new file in `service/indicators/strategies.py` rather than by branching on a method field or editing the interface.
- Using pandas mainly pays off for large ranges of data: higher initial setup cost than vanilla Python, but better time and memory efficiency at scale.
- For short ranges, pandas could be marginally slower than vanilla Python, but the difference is negligible next to the overhead it saves elsewhere.
- Splitting `service/Indicator.py` into a package means one more import per module, but each file now has a single reason to change, which keeps future indicator additions and DTO changes from touching unrelated code.
- `MARKET_DATA_DESIGN.md`'s class diagram has been updated to match this ADR: `IndicatorStrategy`, `Indicator`, and the concrete indicators now live under `namespace service`, `IndicatorParams` and `IndicatorPoint` are gone, and `IndicatorResult` reflects its real fields.

## 002 Timestamps as Unix Seconds via time.time()

Date: 27 AUG 2026

### Context

Every timestamp in `market_data` was represented as a Python `datetime`, converted at the edges through `dt_to_unixMS()` / `unixMS_to_dt()` in `market_data/utils.py`. That round-trip added a conversion step everywhere a timestamp crossed a boundary (constructing a `PriceBar`, building an `IndicatorResult`, keying the rolling-window `dict`s in `strategies.py`), for no benefit: nothing in the service does calendar-aware arithmetic (month/day-of-week logic, timezones, formatting), it's all `window`-sized slices of a numeric series, so `datetime`'s extra structure was never used.

`datetime` objects also aren't naturally cache-friendly: `MarketDataCache`/`CacheEntry` (`data/cache/`) need to compare a stored value's age against now and against a configurable `ttl` (seconds), which is a plain numeric comparison. Doing that against `datetime` objects means either comparing `datetime`s directly (fine, but inconsistent with everything else already moving to plain numbers) or converting through `dt_to_unixMS()` first, which is exactly the indirection being removed.

### Decision

- Every timestamp field across `market_data` is now a plain `float` holding Unix seconds, populated via `time.time()` at the call site instead of `datetime.now()` + conversion.
- `market_data/utils.py` (`dt_to_unixMS()`, `unixMS_to_dt()`) is deleted. There is no longer a conversion boundary to maintain.
- `models/schemas.py`: `PriceBar.ts` and `Quote.ts` changed from `datetime` to `float`.
- `service/indicators/schemas.py`: `IndicatorResult.completed`, `IndicatorRequest.start`, `IndicatorRequest.end`, and `IndicatorRequest.recieved` changed from `datetime`/`int` to `float`, matching `time.time()`'s return type.
- `service/indicators/strategies.py`: every `calculate()` now does `completed=time.time()` directly; the rolling-window `dict`s built in `SMA`/`EMA`/`VWAP`/`ATR` are keyed by `PriceBar.ts` (a `float`) rather than a `datetime`, so no behavior changed beyond the key type.
- `data/cache/schemas.py`: `CacheEntry.created_at` / `CacheEntry.expire_at` are `float` Unix seconds, so `MarketDataCache.prune_cache()` compares them against `time.time()` directly with no conversion.

### Consequences

- One less concept (`datetime`) and one less module (`market_data/utils.py`) to reason about; every timestamp in the service is now the same type end to end.
- Loses `datetime`'s built-in calendar/timezone handling and human-readable `repr`, but the service never used either if `market_data` later needs calendar-aware logic (e.g. formatting a timestamp for a client response), that conversion should happen at the API boundary, not be threaded through the domain/service layer as it was before.
- Test fixtures that keyed expected results by `datetime(...)` (`tests/service/test_{SMA,EMA,VWAP,ATR}.py`) now use a fixed base Unix timestamp plus a day-second offset (`ts_for_day()`) instead, so results stay deterministic without depending on `datetime`.
