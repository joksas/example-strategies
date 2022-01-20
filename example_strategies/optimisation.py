import datetime

import backtrader as bt
import requests_cache
import yfinance as yf

from example_strategies import strategies, utils

session = requests_cache.CachedSession(".yfinance.cache")
session.headers["User-agent"] = "example-strategies"


def optimise_mean_reverting_strategy(
    train_tickers: list[str],
    test_tickers: list[str],
    k_grid: list[int],
    num_std_grid: list[float],
    from_: datetime.date = datetime.date(2000, 1, 1),
    to: datetime.date = datetime.date(2019, 12, 31),
) -> tuple[int, float, float, float]:
    """Optimises mean-reverting strategy using grid search.

    Args:
        train_tickers: Tickers to use for training.
        test_tickers: Tickers to use for testing.
        k_grid: `k` values to try.
        num_std_grid: `num_std` values to try.

    Returns:
        optimal_k: Optimal number of points to use in moving average.
        optimal_num_std: Number of standard deviations from the mean to compute
            buy and sell thresholds.
        max_train_value: Maximum training portfolio value during optimisation.
        test_value: Test portfolio value when using optimised parameters.
    """
    base_amount = 1_000_000.00
    if train_tickers:
        train_amount = base_amount / len(train_tickers)
    if test_tickers:
        test_amount = base_amount / len(test_tickers)

    max_train_value = 0
    optimal_k = k_grid[0]
    optimal_num_std = num_std_grid[0]

    ticker_data = {}
    for ticker in train_tickers + test_tickers:
        ticker_data[ticker] = yf.download(ticker, from_, to, session=session)

    for k in k_grid:
        for num_std in num_std_grid:
            params = {
                "k": k,
                "num_std": num_std,
            }
            total_value = 0
            for ticker in train_tickers:
                cerebro = utils.get_cerebro(
                    strategies.MeanRevertingStrategy, ticker_data[ticker], train_amount, params
                )
                cerebro.run()
                total_value += cerebro.broker.getvalue()

            if total_value > max_train_value:
                optimal_k = k
                optimal_num_std = num_std
                max_train_value = total_value

    test_value = 0
    for ticker in test_tickers:
        params = {
            "k": optimal_k,
            "num_std": optimal_num_std,
        }
        cerebro = utils.get_cerebro(
            strategies.MeanRevertingStrategy, ticker_data[ticker], test_amount, params
        )
        cerebro.run()
        test_value += cerebro.broker.getvalue()

    return optimal_k, optimal_num_std, max_train_value, test_value
