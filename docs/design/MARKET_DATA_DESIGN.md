# Market Data Service Design

**Author:** Dylan Liesenfelt

**Date:** August 21, 2026

**Updated:** September 1, 2026

---

## 1. Purpose / Scope

The Market Data Service is responsible for all communication with external financial-data providers. It normalizes provider-specific responses into internal data models and calculates technical indicators on demand.

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

            + get_quote(ticker: str) Quote
            + get_quotes(tickers: list~str~) list~Quote~
            + get_ticker_info(ticker: str) TickerInfo
            + get_ticker_bars(ticker: str, start: int, end: int, granularity: str) list~PriceBar~
            + get_indicator(ticker: str, indicator: str, end: int, period: int, timeframe: str) IndicatorResult
        }

        class IndicatorStrategy {
            <<Interface>>
            + calculate(data: PriceBarsResult, request: IndicatorRequest) IndicatorResult
        }

        class Indicator {
            <<Context>>
            - strategy: IndicatorStrategy
            - request: IndicatorRequest
            + make_indicator() IndicatorResult
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

        class IndicatorRequest {
            <<BaseModel>>
            + request_id: dict
            + indicator_method: str
            + ticker: str
            + period: int
            + timeframe: str
            + multiplier: int
            + start: int
            + end: int
        }

        class IndicatorResult {
            <<BaseModel>>
            + request_id: dict
            + ticker: str
            + result: dict
        }
    }

    namespace data {
        class Provider {
            <<Interface>>
            + get_quotes(request: QuotesRequest) QuotesResult
            + get_ticker_info(request: TickerInfoRequest) TickerInfoResult
            + get_ticker_bars(request: PriceBarsRequest) PriceBarsResult
        }

        class MassiveProvider {
            <<Provider>>
        }

        class YahooProvider {
            <<Provider>>
            <<planned, not yet implemented>>
        }
    }

    namespace schemas {
        class QuotesRequest {
            <<BaseModel>>
            + request_id: dict
            + tickers: list~str~
        }

        class Quote {
            <<BaseModel>>
            + price: float
            + ts: int
        }

        class QuotesResult {
            <<BaseModel>>
            + request_id: dict
            + tickers: list~str~
            + data: dict~str, Quote~
        }

        class TickerInfoRequest {
            <<BaseModel>>
            + request_id: dict
            + ticker: str
        }

        class TickerInfoResult {
            <<BaseModel>>
            + request_id: dict
            + ticker: str
            + company_name: str
            + hq_location: dict~str, str~
            + logo_url: str
            + market_cap: float
        }

        class PriceBarsRequest {
            <<BaseModel>>
            + request_id: dict
            + ticker: str
            + multiplier: int
            + timeframe: str
            + start: int
            + end: int
        }

        class PriceBar {
            <<BaseModel>>
            + open: float
            + high: float
            + low: float
            + close: float
            + volume: int
            + ts: int
        }

        class PriceBarsResult {
            <<BaseModel>>
            + request_id: dict
            + ticker: str
            + data: dict~int, PriceBar~
        }
    }

    namespace utils {
        class Utils {
            <<Module>>
            + ms_now() int
        }
    }

    MarketDataRouter --> MarketDataService : delegates to
    MarketDataService --> Provider : retrieves data through
    MarketDataService --> Indicator : calculates with
    MarketDataService ..> IndicatorRequest : builds
    MarketDataService ..> IndicatorResult : returns

    MassiveProvider ..|> Provider
    YahooProvider ..|> Provider

    SMA ..|> IndicatorStrategy
    EMA ..|> IndicatorStrategy
    VWAP ..|> IndicatorStrategy
    ATR ..|> IndicatorStrategy

    Indicator --> IndicatorStrategy : delegates to
    Indicator --> IndicatorRequest : uses
    IndicatorStrategy ..> PriceBarsResult : accepts
    IndicatorStrategy ..> IndicatorResult : returns

    Provider ..> QuotesRequest : accepts
    Provider ..> QuotesResult : returns
    Provider ..> TickerInfoRequest : accepts
    Provider ..> TickerInfoResult : returns
    Provider ..> PriceBarsRequest : accepts
    Provider ..> PriceBarsResult : returns
    QuotesResult ..> Quote : contains
    PriceBarsResult ..> PriceBar : contains

    MassiveProvider ..> TimeUtils : uses
    SMA ..> TimeUtils : uses
```

## 3. Sequence Diagrams

### 3.1 Get Ticker Quote

```mermaid
sequenceDiagram
    participant R as MarketDataRouter
    participant Svc as MarketDataService
    participant P as MassiveProvider

    R->>Svc: get_quote("AAPL")
    Svc->>P: get_quotes(QuotesRequest(tickers=["AAPL"]))
    P-->>Svc: QuotesResult
    Svc-->>R: Quote
```

### 3.2 Calculate Technical Indicator

```mermaid
sequenceDiagram
    participant R as MarketDataRouter
    participant Svc as MarketDataService
    participant P as MassiveProvider
    participant Ind as Indicator
    participant Strat as SMA

    R->>Svc: get_indicator("AAPL", "SMA", period, multiplier, timeframe)
    Svc->>P: get_ticker_bars(PriceBarsRequest(...))
    P-->>Svc: PriceBarsResult
    Svc->>Svc: build IndicatorRequest
    Svc->>Ind: Indicator(strategy=SMA(), request)
    Ind->>Strat: calculate(data, request)
    Strat-->>Ind: IndicatorResult
    Ind-->>Svc: IndicatorResult
    Svc-->>R: IndicatorResult
```

## 4. API / Endpoint Definitions

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /quotes/{ticker} | Latest quote for one ticker |
| GET | /quotes?tickers=A,B,C | Latest quotes for multiple tickers |
| GET | /tickers/{ticker}/info | Company info for a ticker |
| GET | /tickers/{ticker}/bars?start=&end=&granularity= | Historical OHLCV bars |
| GET | /tickers/{ticker}/indicators/{indicator}?period=&timeframe= | Calculated indicator values |

## 5. Data Model / Persistence

This service's `data/` layer has no database-backed repository, per ARCHITECTURE.md. Instead `data/` holds the provider adapters (`MassiveProvider`, `YahooProvider`) under `data/providers/`, and the DTOs each provider method accepts/returns (`data/providers/schemas.py`), one Request/Result pair per method, plus an `Object` class (`Quote`, `PriceBar`) for methods whose result holds more than one data point.

Quotes and bars are not persisted long-term here. Services that need persisted history (e.g. Index Service) store it in their own owned datastore, sourced from this service.

## 6. Error Handling

- All external requests use bounded timeouts (NFR-002), including web-scraping-based lookups (NFR-019).
- Retries against a provider use a bounded retry policy (NFR-020).
- If a provider fails after retries, the service returns a defined application error (e.g. `ProviderUnavailableError`), never an unhandled exception (NFR-021).
- A temporary provider failure does not corrupt internally persisted data (NFR-004).
- Provider-specific response shapes never reach calling services, everything is normalized into `QuotesResult`, `TickerInfoResult`, `PriceBarsResult`, etc. before returning (NFR-012, NFR-013).
- `MassiveProvider` failure does not crash unrelated internal services (NFR-003). A fallback provider (`YahooProvider`) may be attempted depending on configured provider priority.
- Because `MassiveProvider` and `YahooProvider` both implement `Provider`, `MarketDataService` can be unit tested against a fake provider that simulates a failure or slow response, without making a real network call (Liskov Substitution, supports TDD).

## 7. Dependencies

- Massive.com (primary provider, CON-001), via `data/providers/MassiveProvider.py`
- Yahoo (fallback provider, planned/not yet implemented), via `data/providers/YahooProvider.py`

This service has no dependency on any other internal service, it is a leaf node in the service graph.

## 8. Configuration

- Per-provider request timeout
- Retry count/backoff per provider
- Provider fallback order
- Supported indicators and their default parameters
- Supported bar granularities
