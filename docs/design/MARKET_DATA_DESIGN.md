# Market Data Service Design

**Author:** Dylan Liesenfelt

**Date:** August 21, 2026

---

## 1. Purpose / Scope

The Market Data Service is responsible for all communication with external financial-data providers. It normalizes provider-specific responses into internal data models, caches recent data to reduce redundant external calls, and calculates technical indicators on demand.

Other internal services obtain market data exclusively through this service, none communicate with Massive.com or any other external provider directly.

## 2. Class Diagram

```mermaid
classDiagram
    direction LR

    namespace api {
        class MarketDataRouter {
            <<Router>>
            + get_quote(ticker: str) Quote
            + get_quotes(tickers: list~str~) list~Quote~
            + get_ticker_info(ticker: str) TickerInfo
            + get_ticker_bars(ticker: str, start: int, end: int, granularity: str) list~PriceBar~
            + get_indicator(ticker: str, indicator: str, end: int, period: int, timeframe: str) IndicatorResult
        }
    }

    namespace service {
        class MarketDataService {
            <<Service>>
            - provider: DataProvider
            - cache: MarketDataCache

            + get_quote(ticker: str) Quote
            + get_quotes(tickers: list~str~) list~Quote~
            + get_ticker_info(ticker: str) TickerInfo
            + get_ticker_bars(ticker: str, start: int, end: int, granularity: str) list~PriceBar~
            + get_indicator(ticker: str, indicator: str, end: int, period: int, timeframe: str) IndicatorResult
        }
    }

    namespace data {
        class MarketDataCache {
            + get(key: str) CacheEntry
            + set(key: str, entry: CacheEntry)
            + is_stale(key: str) bool
        }

        class CacheEntry {
            <<DataClass>>
            + data: Any
            + timestamp: datetime
        }

        class DataProvider {
            <<Interface>>
            + get_quote(ticker: str) Quote
            + get_quotes(tickers: list~str~) list~Quote~
            + get_ticker_info(ticker: str) TickerInfo
            + get_ticker_bars(ticker: str, start: int, end: int, granularity: str) list~PriceBar~
        }

        class MassiveProvider {
            <<Provider>>
        }

        class YahooProvider {
            <<Provider>>
        }
    }

    namespace models {
        class IndicatorStrategy {
            <<Interface>>
            + calculate(data: list~PriceBar~, params: IndicatorParams) IndicatorResult
        }

        class SMA {
            <<Indicator>>
        }

        class EMA {
            <<Indicator>>
        }

        class VWAP {
            <<Indicator>>
        }

        class ATR {
            <<Indicator>>
        }

        class Quote {
            <<DataClass>>
            + ticker: str
            + price: float
            + timestamp: datetime
        }

        class TickerInfo {
            <<DataClass>>
            + ticker: str
            + company_name: str
            + headquarters_location: str
            + logo_url: str
            + market_cap: float
            + share_float: int
        }

        class PriceBar {
            <<DataClass>>
            + ticker: str
            + timestamp: datetime
            + open: float
            + high: float
            + low: float
            + close: float
            + volume: int
        }

        class IndicatorParams {
            <<DataClass>>
            + period: int
            + timeframe: str
        }

        class IndicatorResult {
            <<DataClass>>
            + ticker: str
            + indicator: str
            + timeframe: str
            + values: list~IndicatorPoint~
        }

        class IndicatorPoint {
            <<DataClass>>
            + timestamp: datetime
            + value: float
        }
    }

    MarketDataRouter --> MarketDataService : delegates to
    MarketDataService --> MarketDataCache : uses
    MarketDataService --> DataProvider : retrieves data through
    MarketDataService --> IndicatorStrategy : calculates with

    MarketDataCache --> CacheEntry : stores

    MassiveProvider ..|> DataProvider
    YahooProvider ..|> DataProvider

    SMA ..|> IndicatorStrategy
    EMA ..|> IndicatorStrategy
    VWAP ..|> IndicatorStrategy
    ATR ..|> IndicatorStrategy

    DataProvider ..> Quote : returns
    DataProvider ..> TickerInfo : returns
    DataProvider ..> PriceBar : returns

    IndicatorStrategy ..> IndicatorParams : accepts
    IndicatorStrategy ..> IndicatorResult : returns
    IndicatorResult *-- IndicatorPoint : contains
```

## 3. Sequence Diagrams

### 3.1 Get Ticker Quote (cache hit/miss)

```mermaid
sequenceDiagram
    participant R as MarketDataRouter
    participant Svc as MarketDataService
    participant Cache as MarketDataCache
    participant P as MassiveProvider

    R->>Svc: get_quote("AAPL")
    Svc->>Cache: get("quote:AAPL")
    alt cache hit and fresh
        Cache-->>Svc: CacheEntry
        Svc-->>R: Quote
    else cache miss or stale
        Svc->>P: get_quote("AAPL")
        P-->>Svc: Quote
        Svc->>Cache: set("quote:AAPL", entry)
        Svc-->>R: Quote
    end
```

### 3.2 Calculate Technical Indicator

```mermaid
sequenceDiagram
    participant R as MarketDataRouter
    participant Svc as MarketDataService
    participant Cache as MarketDataCache
    participant P as MassiveProvider
    participant Ind as IndicatorStrategy

    R->>Svc: get_indicator("AAPL", "SMA", period, timeframe)
    Svc->>Cache: get(bars key)
    alt bars cached and fresh
        Cache-->>Svc: CacheEntry
    else bars missing or stale
        Svc->>P: get_ticker_bars("AAPL", start, end, timeframe)
        P-->>Svc: list~PriceBar~
        Svc->>Cache: set(bars key, entry)
    end
    Svc->>Ind: calculate(bars, params)
    Ind-->>Svc: IndicatorResult
    Svc-->>R: IndicatorResult
```

## 4. API / Endpoint Definitions

| Method | Endpoint | Description |
|---|---|---|
| GET | /quotes/{ticker} | Latest quote for one ticker |
| GET | /quotes?tickers=A,B,C | Latest quotes for multiple tickers |
| GET | /tickers/{ticker}/info | Company info for a ticker |
| GET | /tickers/{ticker}/bars?start=&end=&granularity= | Historical OHLCV bars |
| GET | /tickers/{ticker}/indicators/{indicator}?period=&timeframe= | Calculated indicator values |

## 5. Data Model / Persistence

This service's `data/` layer has no database-backed repository, per ARCHITECTURE.md. Instead `data/` holds `MarketDataCache` (backend TBD, in-memory) and the provider adapters (`MassiveProvider`, `YahooProvider`).

Quotes and bars are not persisted long-term here. Services that need persisted history (e.g. Index Service) store it in their own owned datastore, sourced from this service.

## 6. Error Handling

- All external requests use bounded timeouts (NFR-002), including web-scraping-based lookups (NFR-019).
- Retries against a provider use a bounded retry policy (NFR-020).
- If a provider fails after retries, the service returns a defined application error (e.g. `ProviderUnavailableError`), never an unhandled exception (NFR-021).
- A temporary provider failure does not corrupt cached or internally persisted data (NFR-004).
- Provider-specific response shapes never reach calling services, everything is normalized into `Quote`, `TickerInfo`, `PriceBar`, etc. before returning (NFR-012, NFR-013).
- `MassiveProvider` failure does not crash unrelated internal services (NFR-003). A fallback provider (`YahooProvider`) may be attempted depending on configured provider priority.
- Because `MassiveProvider` and `YahooProvider` both implement `DataProvider`, `MarketDataService` can be unit tested against a fake provider that simulates a failure or slow response, without making a real network call (Liskov Substitution, supports TDD).

## 7. Dependencies

- Massive.com (primary provider, CON-001), via `data/MassiveProvider`
- Yahoo (fallback provider), via `data/YahooProvider`

This service has no dependency on any other internal service, it is a leaf node in the service graph.

## 8. Configuration

- Cache TTL / staleness threshold (used by `is_stale()`)
- Per-provider request timeout
- Retry count/backoff per provider
- Provider fallback order
- Supported indicators and their default parameters
- Supported bar granularities
