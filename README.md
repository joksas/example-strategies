# Example Strategies

[![Tests and linting](https://github.com/joksas/example-strategies/actions/workflows/tests-and-linting.yml/badge.svg)](https://github.com/joksas/example-strategies/actions/workflows/tests-and-linting.yml) [![CodeQL](https://github.com/joksas/example-strategies/actions/workflows/code-ql.yml/badge.svg)](https://github.com/joksas/example-strategies/actions/workflows/code-ql.yml)

This repository contains my attempts at implementing some simple statistical tests, trading strategies and optimisation techniques as I am learning about the fundamentals of quantitative trading.
It is very much work in progress.

## Estimating Stationarity

What strategy works best may depend on how stationary a particular stock is.
According to [this](https://www.quantstart.com/successful-algorithmic-trading-ebook/), one may use [Hurst exponent](https://en.wikipedia.org/wiki/Hurst_exponent) *H* to get an estimate of stock's stationarity:

* *H* < 0.5 -- time series is mean reverting
* *H* = 0.5 -- time series is a geometric Brownian motion (i.e. random walk)
* *H* > 0.5 -- time series is trending

One may also use [Augmented Dickey–Fuller (ADF) test](https://en.wikipedia.org/wiki/Augmented_Dickey%E2%80%93Fuller_test).
It allows to test the null hypothesis of whether the time series is *not* mean-reverting.

According to [this](https://www.quantstart.com/successful-algorithmic-trading-ebook/), it is difficult to find stocks that have mean-reverting behaviour.
However, it is possible to find a pair of companies in the same sector that will be subjected to similar market factors, and so their stock prices are likely to correlate.
Adjusted difference of those stock prices might produce mean-reverting series.

Instead of looking at two different companies, I decided to use two of Alphabet's stocks: GOOGL (with voting rights) and GOOG (with no voting rights).
Here is the code for the stationarity analysis of the two stocks in the year 2020 (see [this](/example_strategies/stats.py) for implementation details):
```python
import datetime

from example_strategies import data, stats

year = 2020
from_date, to_date = datetime.date(year, 1, 1), datetime.date(year, 12, 31)

# GOOGL stock price
googl = data.load("GOOGL", from_date=from_date, to_date=to_date)
googl_close = googl["Close"].to_numpy()

# GOOG stock price
goog = data.load("GOOG", from_date=from_date, to_date=to_date)
goog_close = goog["Close"].to_numpy()

# Pairs trading
hedge_ratio = stats.pairs_trading_hedge_ratio(googl_close, goog_close)
residuals = goog_close - hedge_ratio * googl_close

for name, close in [("GOOGL", googl_close), ("GOOG", goog_close), ("Pairs", residuals)]:
    hurst_exponent = stats.hurst_exponent(close)
    adf_p_value = stats.adf_p_val(close)
    print(f"{name}:\nHurst exponent = {hurst_exponent:.2f}; ADF p-value = {adf_p_value:.3f}\n")
```

When executed, the code should yield the following output:
```text
GOOGL:
Hurst exponent = 0.48; ADF p-value = 0.655

GOOG:
Hurst exponent = 0.48; ADF p-value = 0.646

Pairs:
Hurst exponent = 0.23; ADF p-value = 0.036
```

Pairs trading series has the lowest Hurst exponent, indicative of mean-reverting behaviour.
This is also suggested by the low *p*-value in the ADF test which indicates that the hypothesis of *non*-mean-reverting behaviour might be rejected.

## Example Optimisation

Suppose we wanted to optimise moving average crossover strategy using Sharpe ratio.
We could pick a number of companies and, to check if the procedure does not lead to overfitting, divide them into training and test sets.
Optimised parameters would be obtained using the training set and evaluated using the test set (see [this](/example_strategies/optimisation.py#L11) for implementation details).
This is summarised below:
```python
import datetime
import random

from example_strategies import optimisation, strategies

# Top 10 S&P 500 companies by market cap that went public before 2010.
tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "FB", "NVDA", "BRK-B", "JPM", "JNJ"]
random.seed(0)
random.shuffle(tickers)
# 70% in the training set.
num_training = int(0.7 * len(tickers))

optimal_params, train_avg_sharpe, test_avg_sharpe = optimisation.grid_search(
    strategies.MACrossoverStrategy,
    tickers[:num_training],
    tickers[num_training:],
    {
        "fast_length": [2, 5, 10],
        "slow_length": [20, 50, 100],
    },
    from_=datetime.date(2010, 1, 1),
    to=datetime.date(2019, 12, 31),
    metric="sharpe",
)
print(f'Optimal fast moving average length is {optimal_params["fast_length"]} days.')
print(f'Optimal slow moving average length is {optimal_params["slow_length"]} days.')
print("Sharpe ratio is")
print(f"* {train_avg_sharpe:.2f} in the training set")
print(f"* {test_avg_sharpe:.2f} in the test set")
```

When executed, the code should yield the following output:
```text
Optimal fast moving average length is 10 days.
Optimal slow moving average length is 50 days.
Sharpe ratio is
* 0.58 in the training set
* 0.52 in the test set
```

## Unit Testing

Execute
```text
pytest tests
```
