# StonksAPI
The StonksAPI is a comprehensive stock market data and analysis application. The application is a standalone instance, we encourage others to run and modify the application for their own uses. If you would like to test it the most recent version of the application, you can do so by visiting the APIs doc endpoint at (http://not-yet-implemented/docs), or for a more user friendly experience visit https://www.bubbanaut.net/projects/stonksAPI.

## Legal Disclaimer
The stock information, market data, and analysis provided on by this application are for informational and educational purposes only. They do not constitute, and should not be construed as, investment or financial advice.

Investing in stocks involves significant risk, and the loss of principal is possible. Past performance is not indicative or a guarantee of future investment results. The securities mentioned may not be suitable for all investors.

You should carefully consider your investment objectives, risk tolerance, and financial situation before making any trades or investments. We strongly recommend consulting with a licensed financial advisor or certified professional regarding your specific financial circumstances before making any investment decisions.

All stock prices, market data, and performance metrics are subject to change without notice and are delayed by 15 minutes. We do not guarantee the accuracy, completeness, or timeliness of any information provided and will not be held liable for any losses or damages arising from the use of this data.

We hold no claim over the ownership of any stock prices, market data, or analysis provided by this application. All rights to the underlying data and information belong to their respective owners and sources.

## Contributing 
We are not currently accepting contributions from the public at this time.

### Market Data
Data provider service, the backbone of all other features. Collects and provides stock market data, including real-time quotes, historical prices, and other relevant information. Currently provided by Massive.com API at a 15-minute delay. 

** To be implemented in v0.1.0 **

#### Endpoints
- `/marketdata/quotes?{tickers}` - Get real-time stock quotes for a list of symbols.

- `/marketdata/historical?tickers={tickers}&start={start}&end={end}` - Retrieve historical stock price data for a list of symbols over a defined time range.

- `/marketdata/market_status` - Check the current status of the stock market (open, pre-market, after-hours). As well next trading day, upcomming holidays,  last trading day of the week, and month.

- `/marketdata/news` - Get the latest market news and headlines from various sources. 

- `/marketdata/news?tickers={tickers}` - Get the latest market news and headlines for a list of symbols.

- `/marketdata/ticker_info?tickers={tickers}` - Retrieve relevant information for a list of stock tickers. As well as a list of related tickers.

### Custom Indexes
A service that builds, maintains, and provides data related to custom stock indexes. 

The service builds and maintains the indexes in the background, while providing current and historical data for indexes to the users.

Planned Indexes:

- **US Strategic Power Index - SXPWX:** A composite index that tracks the performance of 10 other custom indexes that track strategically important and niche sectors of the US economy. The index is designed to provide a comprehensive view of the overall health and performance of the US economy, with a focus on key sectors that are critical to its long-term growth and stability. SXPWX is calculated as an equal weight of the sub-indexes. With each sub index weighted with a power normalized marketcap weight, this is done to allow smaller niche but innovative comppanies to provide value, instead of being overshadowed by giants of industry.

Sub-Indexes:
* SXPWB: Bread Basket - Food Sovereignty & Agricultural Export Dominance

* SXPWR: ISR - Intelligence, Surveillance & Reconnaissance

* SXPWA: Military Arsenal - Aerospace Defense & Weapons Systems

* SXPWS: Silicon Sovereignty - Semiconductors & Advanced Manufacturing

* SXPWD: Data Dominance - Cybersecurity, Cloud Infrastructure & Network Defense

* SXPWE: Frontier Energy - Nuclear Energy, Fuel Cycle & Next-Generation Reactors

* SXPWC: Critical Resources - Critical Minerals, Strategic Commodities

* SXPWI: Industrial Base - Manufacturing, Industrial Production & Supply Chain Resilience

* SXPWO: Bio-Defense - Biopharmaceuticals, Vaccines & Medical Countermeasures

* SXPWL: Logistics & Supply Chains - Strategic Logistics, Rail Infrastructure, and Transportation Networks

- **XSPEC - Extreme Speculative Index**: A composite index that tracks the performance of 10 highly speculative and innovative companies in niche fields. The index is power normalized marketcap weighted, at a much higher alpha value than the SXPWX indexes.


** To be implemented in v0.2.0 **

#### Endpoints
- `/indexes/{ticker}` - Provides current value of the custom index

- `/indexes/{ticker}?start={start}&end={end}` - Provides historical data on a range for a custom index

### Indicators
Feature that calculates and provides various technical indicators based on historical stock price data. ** To be implemented in v0.3.0 **

#### Endpoints
- `/indicators/{ticker}?indicator={indicator}&interval={interval}` - Calculate and retrieve the specified technical indicator for a given stock ticker for the most recent data over a defined interval.

- `/indicators/{ticker}?indicator={indicator}&start={start}&end={end}&interval={interval}` - Calculate and retrieve the specified technical indicator for a given stock ticker over a defined time range.

### Signals
Feature that generates buy/sell signals based on predefined technical analysis strategies and indicators. ** To be implemented in v0.3.0 **

#### Endpoints
- `/signals/{ticker}?signal={signal}&interval={interval}` - Generate and retrieve buy/sell signals for a given stock ticker based on predefined technical analysis strategies and indicators for the most recent data over a defined interval.

- `/signals/{ticker}?signal={signal}&start={start}&end={end}&interval={interval}` - Generate and retrieve buy/sell signals for a given stock ticker based on predefined technical analysis strategies and indicators.

### Trading Algos
Feature that brings together market data, technical indicators, and trading signals to create automated trading strategies and provide buy/sell signal and the related data that led to that result. ** To be implemented in v0.4.0 **

#### Endpoints
- `/trading_algos/{ticker}?algo={algo}&interval={interval}` - Execute and retrieve the results of a specified trading algorithm for a given stock ticker at a defined interval for the most recent data.

- `/trading_algos/{ticker}?algo={algo}&start={start}&end={end}&interval={interval}` - Execute and retrieve the results of a specified trading algorithm for a given stock ticker over a defined time range.

### Paper Trading
A background service that simulates trading based on the results of the trading algorithms. It provides trade logs and performance metrics of different trading strategies. This service only serves the historical and current data of the trade strategies users can not create startegies, the startegies are predefined by the system. ** To be implemented in v0.5.0 **
