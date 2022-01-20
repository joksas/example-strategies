import backtrader as bt


def get_cerebro(strategy: bt.Strategy, ticker_data, value, params):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy, **params)
    data = bt.feeds.PandasData(dataname=ticker_data)
    cerebro.adddata(data)
    cerebro.broker.setcash(value)

    return cerebro
