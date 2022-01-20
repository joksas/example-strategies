# Example Strategies

## Example Optimisation

Suppose we wanted to optimise a strategy using Sharpe ratio.
We could pick a number of companies and divide them into training (optimisation) and test sets.
Then, we could execute the following:
```python
import datetime
import random

from example_strategies import optimisation, strategies

# Top 10 companies by market cap in S&P 500 that went public before 2000.
tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "BRK-B", "JPM", "JNJ", "UNH", "PG", "HD"]
random.seed(0)
random.shuffle(tickers)

optimal_params, train_avg_sharpe, test_avg_sharpe = optimisation.grid_search(
    strategies.MeanRevertingStrategy,
    tickers[:7],
    tickers[7:],
    {
        "k": [10, 20, 50, 100, 200],
        "num_std": [0.1, 0.2, 0.5, 1.0, 2.0],
    },
    from_=datetime.date(2000, 1, 1),
    to=datetime.date(2019, 12, 31),
    metric="sharpe",
)
print(f'Optimal moving average length is {optimal_params["k"]} days.')
print(f'Optimal threshold is {optimal_params["num_std"]} standard deviations away from the mean.')
print(
    f"Sharpe ratio is {train_avg_sharpe} in the training set and {test_avg_sharpe} in the test set."
)
```

This should yield the following output:
```text
Optimal moving average length is 50 days.
Optimal threshold is 0.1 standard deviations away from the mean.
Sharpe ratio is 0.45781138450752384 in the training set and 0.2537772291180169 in the test set.
```

## Testing

Execute
```text
pytest tests
```
