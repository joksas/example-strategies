import backtrader as bt


def get_cerebro(strategy: bt.Strategy, ticker_data, value, params, percent_size=90):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy, **params)
    data = bt.feeds.PandasData(dataname=ticker_data)
    cerebro.adddata(data)
    cerebro.broker.setcash(value)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=percent_size)

    return cerebro
