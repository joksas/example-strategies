import datetime

import backtrader as bt
from example_strategies import data, strategies


def test_no_strategy():
    amount = 1_000_000.00
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategies.NoStrategy)
    financial_data = data.load("MSFT", datetime.date(2019, 1, 1), datetime.date(2019, 1, 10))
    bt_data = bt.feeds.PandasData(dataname=financial_data)
    cerebro.adddata(bt_data)
    cerebro.broker.setcash(amount)

    assert cerebro.broker.getvalue() == amount
    cerebro.run()
    assert cerebro.broker.getvalue() == amount


def test_naive_strategy():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategies.NaiveStrategy)
    financial_data = data.load("MSFT", datetime.date(2000, 1, 1), datetime.date(2000, 1, 31))
    bt_data = bt.feeds.PandasData(dataname=financial_data)
    cerebro.adddata(bt_data)
    cerebro.broker.setcash(1_000_000.00)
    cerebro.run()

    # Triplets of days when MSFT keeps decreasing:
    # * 10, 11, 12 -> buy here, will be able to sell on 21 (after 5 trading days)
    # * 18, 19, 20 -> can't buy
    # * 19, 20, 21 -> can't buy
    # * 20, 21, 24 -> buy here
    # * 25, 26, 27 -> can't buy
    # * 26, 27, 28 -> can't buy

    orders = cerebro.broker.orders
    assert len(orders) == 3

    assert orders[0].isbuy()
    assert bt.num2date(orders[0].created.dt) == datetime.datetime(2000, 1, 12)

    assert orders[1].issell()
    assert bt.num2date(orders[1].created.dt) == datetime.datetime(2000, 1, 21)

    assert orders[2].isbuy()
    assert bt.num2date(orders[2].created.dt) == datetime.datetime(2000, 1, 24)


def test_mean_reverting_strategy():
    amount = 1_000_000.00
    k = 5
    num_std = 1
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategies.MeanRevertingStrategy, k=k, num_std=num_std)
    financial_data = data.load("MSFT", datetime.date(2000, 1, 1), datetime.date(2000, 1, 31))

    # Days when deviation from moving average exceeds one standard deviation:
    # * 11 (BELOW)
    # * 12 (BELOW)
    # * 18 (ABOVE)
    # * 21 (BELOW)
    # * 24 (BELOW)
    # * 26 (BELOW)
    # * 27 (BELOW)
    # See:
    # ```python
    # print(
    #     (df.loc[:, "Close"] - df.loc[:, "Close"].rolling(k).mean())
    #     / df.loc[:, "Close"].rolling(k).std()
    # )
    # ```
    bt_data = bt.feeds.PandasData(dataname=financial_data)
    cerebro.adddata(bt_data)
    cerebro.broker.setcash(amount)
    cerebro.run()

    orders = cerebro.broker.orders

    assert len(orders) == 3

    assert orders[0].isbuy()
    assert bt.num2date(orders[0].created.dt) == datetime.datetime(2000, 1, 11)

    assert orders[1].issell()
    assert bt.num2date(orders[1].created.dt) == datetime.datetime(2000, 1, 18)

    assert orders[2].isbuy()
    assert bt.num2date(orders[2].created.dt) == datetime.datetime(2000, 1, 21)


def test_ma_crossover_strategy():
    amount = 1_000_000.00
    fast_length = 2
    slow_length = 10
    cerebro = bt.Cerebro()
    cerebro.addstrategy(
        strategies.MACrossoverStrategy, fast_length=fast_length, slow_length=slow_length
    )
    cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
    financial_data = data.load("MSFT", datetime.date(2000, 1, 1), datetime.date(2000, 1, 31))

    # Days when fast moving average exceeds slow moving average:
    # * 18
    # * 19
    # See:
    # ```python
    # print(
    #     df.loc[:, "Close"].rolling(fast_length).mean()
    #     > df.loc[:, "Close"].rolling(slow_length).mean(),
    # )
    # ```
    bt_data = bt.feeds.PandasData(dataname=financial_data)
    cerebro.adddata(bt_data)
    cerebro.broker.setcash(amount)
    cerebro.run()

    orders = cerebro.broker.orders

    assert len(orders) == 2

    assert orders[0].isbuy()
    assert bt.num2date(orders[0].created.dt) == datetime.datetime(2000, 1, 18)

    assert orders[1].issell()
    assert bt.num2date(orders[1].created.dt) == datetime.datetime(2000, 1, 20)
