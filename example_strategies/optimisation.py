import datetime
import itertools
from typing import Any

import backtrader as bt
import backtrader.analyzers as btanalyzers
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
    metric: str = "sharpe",
    timeframe=bt.TimeFrame.Years,
) -> tuple[dict[str, Any], float, float]:
    """Optimises mean-reverting strategy using grid search.

    Args:
        strategy: Strategy to optimise.
        train_tickers: Tickers to use for training.
        test_tickers: Tickers to use for testing.
        params_grid: The values to try for each parameter.
        from_: The date to test from.
        to: The date to test to.
        metric: Metric to optimise. Should be one of `["sharpe", "returns"]`.
        timeframe: Timeframe on which to calculate the metrics.

    Returns:
        optimal_params: Optimal parameters.
        train_avg_metric: Training portfolio's best average metric value during
            optimisation.
        test_avg_metric: Test portfolio's average metric value when using
            optimised parameters.
    """
    base_amount = 1_000_000.00
    if train_tickers:
        train_amount = base_amount / len(train_tickers)
    if test_tickers:
        test_amount = base_amount / len(test_tickers)

    train_avg_metric = 0.0

    optimal_params = {}
    # Set to the first value in the grid.
    for param in params_grid:
        optimal_params[param] = params_grid[param][0]

    # Download the data now because it will be reused.
    ticker_data = {}
    for ticker in train_tickers + test_tickers:
        ticker_data[ticker] = yf.download(ticker, from_, to, session=session, progress=False)

    # Cartesian product.
    for values in itertools.product(*params_grid.values()):
        params = dict(zip(params_grid.keys(), values))
        total_value = 0
        for ticker in train_tickers:
            cerebro = utils.get_cerebro(strategy, ticker_data[ticker], train_amount, params)
            cerebro.addanalyzer(btanalyzers.SharpeRatio, timeframe=timeframe, _name="sharpe")
            cerebro.addanalyzer(btanalyzers.Returns, timeframe=timeframe, _name="returns")
            run = cerebro.run()

            # TODO: Support multi-stock strategies instead of averaging metrics.
            total_value += _get_metric_value(run, metric)

        avg_value = total_value / len(train_tickers)
        if _is_improved(metric, avg_value, train_avg_metric):
            for param in params:
                optimal_params[param] = params[param]
            train_avg_metric = avg_value

    test_avg_metric = 0.0
    for ticker in test_tickers:
        cerebro = utils.get_cerebro(strategy, ticker_data[ticker], test_amount, optimal_params)
        cerebro.addanalyzer(btanalyzers.SharpeRatio, timeframe=timeframe, _name="sharpe")
        cerebro.addanalyzer(btanalyzers.Returns, timeframe=timeframe, _name="returns")
        run = cerebro.run()
        test_avg_metric += _get_metric_value(run, metric)

    if test_tickers:
        test_avg_metric /= len(test_tickers)

    return optimal_params, train_avg_metric, test_avg_metric


def _get_metric_value(run, metric_name):
    analyzers = run[0].analyzers

    if metric_name == "sharpe":
        return analyzers.sharpe.get_analysis()["sharperatio"]

    if metric_name == "returns":
        return analyzers.returns.get_analysis()["rtot"]

    raise ValueError(f'Metric "{metric_name}" is not recognised.')


def _is_improved(metric_name: str, current, previous_best):
    if metric_name == "sharpe":
        if current > previous_best:
            return True
        return False

    if metric_name == "returns":
        if current > previous_best:
            return True
        return False

    raise ValueError(f'Metric "{metric_name}" is not recognised.')
