import datetime
import itertools
from typing import Any

import backtrader as bt
import requests_cache
import yfinance as yf

from example_strategies import utils

session = requests_cache.CachedSession(".yfinance.cache")
session.headers["User-agent"] = "example-strategies"


def grid_search(
    strategy: bt.Strategy,
    train_tickers: list[str],
    test_tickers: list[str],
    params_grid: dict[str, Any],
    from_: datetime.date = datetime.date(2000, 1, 1),
    to: datetime.date = datetime.date(2019, 12, 31),
) -> tuple[dict[str, Any], float, float]:
    """Optimises mean-reverting strategy using grid search.

    Args:
        strategy: Strategy to optimise.
        train_tickers: Tickers to use for training.
        test_tickers: Tickers to use for testing.
        params_grid: The values to try for each parameter.
        from_: The date to test from.
        to: The date to test to.

    Returns:
        optimal_params: Optimal parameters.
        max_train_value: Maximum training portfolio value during optimisation.
        test_value: Test portfolio value when using optimised parameters.
    """
    base_amount = 1_000_000.00
    if train_tickers:
        train_amount = base_amount / len(train_tickers)
    if test_tickers:
        test_amount = base_amount / len(test_tickers)

    max_train_value = 0

    optimal_params = {}
    # Set to the first value in the grid.
    for param in params_grid:
        optimal_params[param] = params_grid[param][0]

    # Download the data now because it will be reused.
    ticker_data = {}
    for ticker in train_tickers + test_tickers:
        ticker_data[ticker] = yf.download(ticker, from_, to, session=session)

    # Cartesian product.
    for values in itertools.product(*params_grid.values()):
        params = dict(zip(params_grid.keys(), values))
        total_value = 0
        for ticker in train_tickers:
            cerebro = utils.get_cerebro(strategy, ticker_data[ticker], train_amount, params)
            cerebro.run()
            total_value += cerebro.broker.getvalue()

        if total_value > max_train_value:
            for param in params:
                optimal_params[param] = params[param]
            max_train_value = total_value

    test_value = 0
    for ticker in test_tickers:
        cerebro = utils.get_cerebro(strategy, ticker_data[ticker], test_amount, optimal_params)
        cerebro.run()
        test_value += cerebro.broker.getvalue()

    return optimal_params, max_train_value, test_value
