# Requirements Document

**Author:** Dylan Liesenfelt
**Date:** August 8, 2026

---

## 1. Functional Requirements

### Market Data

* **FR-001:** The system shall return the latest available market price for a requested stock ticker.

* **FR-002:** The system shall support requesting the latest available market price for multiple stock tickers in a single request.

* **FR-003:** The system shall return historical OHLCV price data for a requested stock ticker, date range, and supported timeframe.

* **FR-004:** The system shall return available company information for a requested stock ticker, including:

  * Company name
  * Headquarters location
  * Company logo
  * Market capitalization
  * Share float

### Technical Indicators

* **FR-005:** The system shall calculate supported technical analysis indicators for a requested stock ticker, date range, and timeframe on demand.

* **FR-006:** The system shall return the calculated indicator values and the timestamps associated with those values.

### Trading Strategies

* **FR-007:** The system shall evaluate a supported trading strategy for a requested stock ticker using the latest available market data.

* **FR-008:** The system shall return a `BUY`, `HOLD`, or `SELL` result from a strategy evaluation.

* **FR-009:** The system shall support evaluating a trading strategy at a requested historical point in time.

* **FR-010:** Historical strategy evaluations shall only use market data available at or before the requested evaluation timestamp.

* **FR-011:** The system shall return the individual signal or indicator results used to determine a strategy's final result when those results are available.

### Custom Stock Indexes

* **FR-012:** The system shall return the latest calculated value of a requested custom stock index.

* **FR-013:** The system shall return historical values for a requested custom stock index over a specified date range.

* **FR-014:** The system shall maintain historical values for configured custom stock indexes at a minimum granularity of 15 minutes.

* **FR-015:** The system shall detect missing intervals in the historical data of a custom stock index.

* **FR-016:** The system shall attempt to reconstruct missing custom index values when sufficient constituent market data is available.

* **FR-017:** The system shall maintain the definition of each custom stock index, including its constituent stocks and any information required to calculate the index.

### Paper Trading

* **FR-018:** The system shall support a single simulated paper-trading account per configured trading strategy.

* **FR-019:** The system shall automatically evaluate configured paper-trading strategies according to their configured execution schedules.

* **FR-020:** The system shall generate simulated trades when a paper-trading strategy produces an actionable trading signal.

* **FR-021:** The system shall maintain the state of each paper-trading account, including:

  * Available cash
  * Open positions
  * Position quantities
  * Average acquisition cost
  * Executed trades

* **FR-022:** The system shall persist paper-trading account state and transaction history.

* **FR-023:** The system shall maintain historical portfolio values for paper-trading accounts.

* **FR-024:** The system shall return performance information for a requested paper-trading strategy or account over a specified timeframe.

* **FR-025:** Paper-trading performance information shall include, when applicable:

  * Total return
  * Realized profit and loss
  * Unrealized profit and loss
  * Maximum drawdown
  * Number of trades
  * Win rate

---

## 2. Non-Functional Requirements

### Performance

* **NFR-001:** The system shall process API requests without requiring the user to directly interact with individual internal services.

* **NFR-002:** Requests to external data providers shall use bounded timeouts and shall not block indefinitely.

### Reliability

* **NFR-003:** Failure of an external market-data provider shall not cause unrelated internal services to terminate.

* **NFR-004:** Temporary failure of an external data provider shall be handled without corrupting internally persisted financial data.

* **NFR-005:** Failure of one internal service shall not result in corruption of data owned by another internal service.

### Data Integrity

* **NFR-006:** The system shall prevent duplicate historical custom-index records for the same index and timestamp.

* **NFR-007:** The system shall prevent duplicate paper-trading transactions representing the same simulated trade execution.

* **NFR-008:** Historical financial records shall preserve the timestamp associated with the source market data.

### Security

* **NFR-009:** The system shall validate externally supplied request parameters, including:

  * Stock ticker symbols
  * Date ranges
  * Timeframes
  * Strategy identifiers
  * Index identifiers

* **NFR-010:** Credentials and API keys for external providers shall not be exposed through public API responses.

### Maintainability

* **NFR-011:** Internal services consuming market data shall not depend directly on the response format of a specific third-party financial-data provider.

* **NFR-012:** Third-party financial-data responses shall be transformed into internal system-defined data models before being consumed by other services.

* **NFR-013:** Trading indicators shall be implemented independently from trading strategies so that indicators may be reused by multiple strategies.

* **NFR-014:** Trading strategy logic shall be separated from paper-trading account management.

### Observability

* **NFR-015:** Each incoming API request shall have a request or correlation identifier that can be propagated through downstream internal service calls.

* **NFR-016:** Services shall produce structured logs containing sufficient information to identify the service, event, timestamp, and associated request identifier when applicable.

* **NFR-017:** Each independently deployed service shall expose a health endpoint that can be used to determine whether the service is operational.

### External Service Resilience

* **NFR-019:** External market-data requests via web scraping will use timeouts to prevent abuse of providers.

* **NFR-020:** Retried external requests shall use a bounded retry policy.

* **NFR-021:** Failure to retrieve external market data shall result in a defined application error rather than an unhandled service exception.

---

## 3. System Constraints

* **CON-001:** The initial primary external market-data provider shall be Massive.com.

* **CON-002:** Market data returned by Massive.com may be delayed according to the limitations of the configured Massive.com subscription. (15 minuets)

* **CON-003:** PostgreSQL shall be used for persistent application data that requires relational storage.

* **CON-004:** Custom stock-index historical values shall support a minimum base granularity of 15 minutes.

* **CON-005:** The system shall expose its functionality through an API and shall not contain its own user interface.

* **CON-006:** The system backend architecture shall use FastAPI as its framework basis.

---

## 4. Architectural Boundaries

The system shall be divided into services with clearly defined responsibilities.

### API Gateway

The API Gateway shall act as the primary user-facing entry point to the system. High level interface layer, user shall not have direct acess to the lower level services.

Responsibilities include:

* Receiving external API requests
* Request validation
* Authentication where required
* Routing requests to internal services
* Coordinating requests requiring multiple internal services
* Returning normalized API responses
* Propagating request correlation identifiers

The API Gateway shall not contain financial calculation or trading-strategy business logic.

### External Data Service

The External Data service shall be responsible for communication with external financial-data sources.

Responsibilities include:

* Communicating with Massive.com
* Communicating with additional external data providers when required
* Transforming provider-specific responses into internal data models
* External request timeout handling
* Retry handling
* Market-data caching where appropriate

Other internal services shall obtain external market data through this service rather than communicating directly with external financial-data providers.

### Index Service

The Index service shall act as the source of truth for custom stock indexes.

Responsibilities include:

* Maintaining custom index definitions
* Maintaining index constituents
* Calculating custom index values
* Maintaining historical index values
* Detecting gaps in historical index data
* Reconstructing missing index data when possible

### Strategy Service

The Strategy service shall contain the business logic used to evaluate trading strategies.

Responsibilities include:

* Calculating or invoking supported technical indicators
* Combining indicators or signals according to defined strategy rules
* Evaluating strategies on demand
* Evaluating strategies for historical timestamps
* Returning `BUY`, `HOLD`, or `SELL` results
* Returning information explaining how a strategy result was produced

Strategy evaluation shall be stateless with respect to paper-trading account balances and positions.

### Paper Trading Service

The Paper Trading service shall manage persistent simulated trading activity.

Responsibilities include:

* Maintaining paper-trading accounts
* Scheduling strategy evaluations
* Processing actionable strategy results
* Executing simulated trades
* Maintaining simulated account cash
* Maintaining simulated positions
* Recording transaction history
* Recording portfolio-value history
* Calculating strategy and account performance metrics

---

## 5. General System Rules

* Internal services shall communicate through explicitly defined interfaces or API contracts.

* Services shall not directly modify data owned by another service.

* External financial-data provider schemas shall not be exposed as internal domain models.

* Historical strategy evaluations shall not use market data from after the requested evaluation timestamp.

* A failure to obtain optional external data shall not terminate unrelated functionality.

* Paper-trading operations shall not execute real financial transactions.

* Trading strategy results produced by the system are analytical outputs and shall not directly interact with brokerage accounts.
