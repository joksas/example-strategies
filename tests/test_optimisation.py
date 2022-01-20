import datetime
import random

import backtrader as bt
from example_strategies import optimisation, strategies


def test_grid_search():
    """This simply tries to run the optimisation to make sure nothing
    breaks."""

    # Top 10 companies by market cap in S&P 500 that went public before 2000.
    tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "BRK-B", "JPM", "JNJ", "UNH", "PG", "HD"]
    random.seed(0)
    random.shuffle(tickers)

    optimal_params, train_avg_sharpe, test_avg_sharpe = optimisation.grid_search(
        strategies.MeanRevertingStrategy,
        tickers[:7],
        tickers[7:],
        {
            "k": [2, 5],
            "num_std": [0.1, 0.2, 0.5],
        },
        to=datetime.date(2000, 1, 31),
        timeframe=bt.TimeFrame.Weeks,
        metric="sharpe",
    )

    assert "k" in optimal_params
    assert "num_std" in optimal_params
    assert isinstance(train_avg_sharpe, float)
    assert isinstance(test_avg_sharpe, float)
