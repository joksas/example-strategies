import datetime

import backtrader as bt
import example_strategies as es
import numpy as np
import requests_cache
import yfinance as yf

session = requests_cache.CachedSession(".yfinance.cache")
session.headers["User-agent"] = "example-strategies"


def test_no_strategy():
    amount = 1_000_000.00
    cerebro = bt.Cerebro()
    cerebro.addstrategy(es.NoStrategy)
    df = yf.download("MSFT", datetime.date(2019, 1, 1), datetime.date(2019, 1, 10))
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.broker.setcash(amount)

    assert cerebro.broker.getvalue() == amount
    cerebro.run()
    assert cerebro.broker.getvalue() == amount


def test_naive_strategy():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(es.NaiveStrategy)
    df = yf.download("MSFT", datetime.date(2000, 1, 1), datetime.date(2000, 1, 31), session=session)
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
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
    cerebro.addstrategy(es.MeanRevertingStrategy, k=k, num_std=num_std)
    df = yf.download("MSFT", datetime.date(2000, 1, 1), datetime.date(2000, 1, 31), session=session)

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
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
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
