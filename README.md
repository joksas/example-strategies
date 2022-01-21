# Example Strategies

## Example Optimisation

Suppose we wanted to optimise mean reversion strategy using Sharpe ratio.
We could pick a number of companies and, to avoid overfitting, divide them into training and test sets.
Optimised parameters would be obtained using the training set and evaluated using the test set.
This is summarised below:
```python
import datetime
import random

from example_strategies import optimisation, strategies

# Top 10 companies by market cap in S&P 500 that went public before 2000.
tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "BRK-B", "JPM", "JNJ", "UNH", "PG", "HD"]
random.seed(0)
random.shuffle(tickers)
# 70% in the training set.
num_training = int(0.7 * len(tickers))

optimal_params, train_avg_sharpe, test_avg_sharpe = optimisation.grid_search(
    strategies.MeanRevertingStrategy,
    tickers[:num_training],
    tickers[num_training:],
    {
        "k": [10, 20, 50, 100],
        "num_std": [0.05, 0.1, 0.2, 0.5],
    },
    from_=datetime.date(2000, 1, 1),
    to=datetime.date(2019, 12, 31),
    metric="sharpe",
)
print(f'Optimal moving average length is {optimal_params["k"]} days.')
print(f'Optimal threshold is {optimal_params["num_std"]} SDs away from the mean.')
print("Average Sharpe ratio is")
print(f"* {train_avg_sharpe:.2f} in the training set")
print(f"* {test_avg_sharpe:.2f} in the test set")

```

When executed, the code should yield the following output:
```text
Optimal moving average length is 50 days.
Optimal threshold is 0.1 SDs away from the mean.
Average Sharpe ratio is
* 0.45 in the training set
* 0.32 in the test set
```

## Testing

Execute
```text
pytest tests
```
