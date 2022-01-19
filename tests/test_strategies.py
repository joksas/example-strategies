import datetime

import backtrader as bt
import example_strategies as es
import yfinance as yf


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
