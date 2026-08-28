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

# 003 Unix Milliseconds, Not Seconds, for All Timestamps

Date: 28 AUG 2026

## Context

[[002]] moved every timestamp to a plain Unix-seconds `float` via `time.time()`. In practice that turned out to be the wrong unit for two of the fields it covered. The request-tracking fields (`received_at`/`completed_at`) in the result in the Request and Result data classes in `providers/schmea` are used to measure and log how long a request took to process, and whole seconds don't have enough resolution for that, most of this service's work completes in well under a second.

Separately, Massive.com returns every timestamp it produces as Unix milliseconds, not seconds and not `datetime`. Keeping the service's own internal clock in seconds while every value coming from the provider is natively in milliseconds meant a conversion at that boundary no matter what, and everything downstream of a `PriceBar.ts` (the indicator strategies' rolling-window keys, the cache's staleness math) inherits whichever unit was chosen.

Given the provider is already the ms convention, and the internal request-tracking timestamps need sub-second resolution anyway, seconds was the wrong choice from both directions. Standardizing on Unix milliseconds means the provider's timestamps pass through unconverted, and the service's own clock has the resolution `completed`/`received` actually need.

## Decision

- Every timestamp in `market_data` is now a plain `int` holding Unix milliseconds, not the `float` Unix seconds [[002]] introduced.
- `market_data/utils.py` is back, holding one function: `ms_now() -> int`, implemented as `time.time_ns() // 1_000_000`. `time.time_ns()` is used instead of `time.time()` because it returns whole nanoseconds as an `int`, so the millisecond conversion is exact integer floor division, no float rounding error the way `time.time() * 1000` would have.
- Every field that used to be `float` seconds is now `int` milliseconds: `PriceBar.ts`, `Quote.ts` (now in `data/providers/schemas.py`, see [[004]]), `IndicatorResult.completed_at` (renamed from `completed`), `IndicatorRequest.start`/`end`/`received_at` (renamed from `recieved`), `CacheEntry.expire_at`.
- `service/indicators/strategies.py`: every `calculate()` now does `completed_at=ms_now()`.
- `data/cache/MarketDataCache.py`: `expire_at=ms_now() + self.ttl` and staleness comparisons in `prune_cache()` are plain millisecond integer comparisons, matching how the provider and the rest of the service already represent time, no conversion at the cache boundary.
- `data/providers/MassiveProvider.py` passes Massive's own millisecond timestamps straight through (`ts=agg.timestamp`, `ts=res.min.timestamp`) into `PriceBar`/`Quote` with no conversion, since both sides now agree on the unit.

## Consequences

- `completed_at`/`received_at` now have millisecond resolution, which is what they're actually used for (measuring request duration), where seconds under [[002]] would have rounded most requests down to 0 or 1.
- Every timestamp in the service, from the provider response through the cache to the indicator output, is the same type and the same unit end to end, so there's no conversion step anywhere in the pipeline, not even at the provider boundary, which used to be the whole justification for `dt_to_unixMS()`/`unixMS_to_dt()` under the original `datetime`-based design.
- [[002]]'s reasoning against `datetime` still holds unchanged, this ADR only revisits which plain numeric unit to use, seconds vs. milliseconds. Nothing here reintroduces `datetime`.
- Test fixtures built on `ts_for_day()` ([[002]]) were rescaled from a seconds base/step to a milliseconds base/step (`BASE_TS_MS`, `DAY_MS = 86400000`), so they still produce distinct, ordered, deterministic timestamps, just in the new unit.

# 004 Provider DTOs as Request/Object/Response Trios, Under data/providers/

Date: 28 AUG 2026

## Context

`models/schemas.py` held `PriceBar`, `Quote`, and `TickerInfo` as flat, general-purpose domain models: each one field-for-field represented "the data," with no distinction between what a caller sends to request it, what a single data point looks like, and what a provider call actually returns (which is more than just the data point, e.g. `request_id`, the ticker the response is for, and a completion timestamp). Every provider method (`get_quotes`, `get_ticker_info`, `get_ticker_bars`) ended up building its response by hand out of these general models plus loose extra fields, with no schema actually describing the request or the full response shape.

`models/` also no longer matched where these types are used. `PriceBar`/`Quote`/`TickerInfo` only exist to describe what `data/providers/` sends and receives, they're the provider adapter layer's DTOs, not domain models shared by multiple layers, so keeping them in a separate top-level `models/` package split the type from the code that actually produces and consumes it.

## Decision

- `models/` is deleted. Its contents moved to `data/providers/schemas.py`, next to `Provider`/`MassiveProvider`, the only code that builds or consumes them.
- Each provider method now has its own Request/Result pair: `PriceBarsRequest`/`PriceBarsResult`, `QuotesRequest`/`QuotesResult`, `TickerInfoRequest`/`TickerInfoResult`. The `Request` carries what the caller supplies (`request_id`, the lookup parameters, `received_at`); the `Result` carries what the provider call actually returns (`request_id` echoed back, the ticker(s), the data, `completed_at`).
- `get_ticker_bars` and `get_quotes` additionally get a plain `Object` class for data sturcturing `PriceBar` and `Quote` respectively. Their `Result` wraps a `dict` of these (`PriceBarsResult.data: dict[int, PriceBar]` keyed by ms timestamp, `QuotesResult.data: dict[str, Quote]` keyed by ticker), since those two methods return more than one data point per call.
- `get_ticker_info` has no `Object` class, just `TickerInfoRequest`/`TickerInfoResult`. A ticker info lookup is inherently one record for one ticker, there's no collection to hold, so `TickerInfoResult` carries the company fields directly instead of wrapping a single-entry `dict`.
- `PriceBar` and `Quote` no longer carry a `ticker` field. Under the flat `models/schemas.py` design, each one was self-describing since nothing else scoped it to a ticker. Now that they only ever appear inside a `Result` that's already scoped to a ticker (`PriceBarsResult.ticker`, or the dict key in `QuotesResult.data`), repeating it on every point would be redundant. This is also why `IndicatorStrategy.calculate()` ([[001]]) gained an explicit `ticker: str` parameter: `PriceBar` can no longer supply it.

## Consequences

- Every provider method's request and response shape is now an explicit, checkable schema instead of an implicit convention, so a missing or mistyped field fails at construction time (a Pydantic `ValidationError`) instead of surfacing later as a missing attribute somewhere downstream.
- `data/providers/schemas.py` has more classes (eight) than `models/schemas.py` did (three), one Request/Result pair per method plus two point-level `Object` classes, but each one is single-purpose and none of them do double duty the way the old flat models did.
- Anything that previously read `PriceBar.ticker`/`Quote.ticker` needs the ticker from the surrounding `Result` (or, inside a strategy, from the new `ticker` parameter) instead. `service/indicators/strategies.py` and every strategy test needed updating for this.
- `IndicatorData.price_history` changed from `list[PriceBar]` to `dict[int, PriceBar]` to match `PriceBarsResult.data`'s shape, so `Indicator` can pass a provider result's `data` straight through without reshaping it first.
