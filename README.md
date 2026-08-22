# StonksAPI

## Overview

StonksAPI is a backend API for exploring market data, technical indicators, custom stock indexes, and simulated trading strategies. It's built for research and educational purposes, letting you evaluate how a trading strategy would have performed, track custom-built stock indexes, and run strategies against a simulated ("paper trading") account, all without touching real markets or real money.

The system is API-only (see Disclaimer above), it does not ship with, and does not plan to ship, a user interface. For details on how the system is structured internally, see `ARCHITECTURE.md`, `REQUIREMENTS.md`, and the per-service `*_DESIGN.md` documents in this repository.

---

## Disclaimer

This project is provided for research and educational purposes only. Nothing produced by this system, including strategy evaluations, technical indicators, or index values, constitutes financial, investment, or trading advice. No `BUY`, `HOLD`, or `SELL` output should be interpreted as a recommendation to buy, sell, or hold any security. All paper-trading activity is simulated; no real funds or real brokerage transactions are involved.

Market data, company information, and related content available through this API are sourced from third-party data providers (including Massive.com) via an internal data service. This project does not own and makes no claim of ownership over any underlying market data. All rights to that data remain with the respective providers.

If you build an external application or interface using this API, you are responsible for attributing the original data source(s) as required by that provider's terms of use.

---

## Development

StonksAPI is built as a set of independently deployable backend services (API Gateway, Market Data Service, Index Service, Strategy Service, and Paper Trading Service) communicating over internal HTTP APIs. The backend is written using [FastAPI](https://fastapi.tiangolo.com/), with [PostgreSQL](https://www.postgresql.org/) used for services that require persistent relational storage.

Full design documentation for each service, including class diagrams, sequence diagrams, and data models, lives alongside this README:

- `ARCHITECTURE.md` — high-level system architecture and service communication
- `REQUIREMENTS.md` — functional and non-functional requirements
- `GATEWAY_DESIGN.md`, `MARKET_DATA_DESIGN.md`, `INDEXES_DESIGN.md`, `STRATEGY_DESIGN.md`, `PAPER_TRADING_DESIGN.md` — per-service design docs

This project is under active development. Local development instructions will be added here as the initial services are implemented.

---

## Installation and Usage

Detailed installation and usage instructions will be added once the initial services are implemented and ready for external use.

At a high level, running this project will require:

- Python (version TBD)
- PostgreSQL, for services with persistent storage (Index Service, Paper Trading Service)
- API credentials for the configured external market-data provider (Massive.com)

Check back here for setup steps, environment configuration, and example API requests as development progresses.

---

## Bugs and Feature Requests

If you run into a bug or have a feature request, please open an issue in this repository. When reporting a bug, include:

- What you expected to happen
- What actually happened
- Steps to reproduce the issue
- Any relevant request/response details or error messages

Since this project isn't yet accepting external contributions (see below), issues are the best way to get something on the radar for now.

---

## Contributing

No contributions are currently being accepted. This project is under active development and is not yet ready for external contributions. Please check back later. Thank you for your interest.
