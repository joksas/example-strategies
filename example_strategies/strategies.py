import datetime
import logging
from collections import deque

import backtrader as bt
import numpy as np

logger = logging.getLogger(__name__)


class NoStrategy(bt.Strategy):
    """Do-nothing strategy."""

    def __init__(self):
        pass

    def next(self):
        pass


class BaseStrategy(bt.Strategy):
    """A class meant to be inherited by the actual strategy classes. Provides a
    few useful functions"""

    def __init__(self):
        self.order = None
        self.sum = 0.0
        self.executed_orders = []
        self.executed_days = []

    @staticmethod
    def _is_buy_str(order) -> str:
        if order.isbuy():
            return "buy"
        return "sell"

    def log(self, txt: str, dt: datetime.date = None, level: int = logging.INFO):
        if dt is None:
            dt = self.datas[0].datetime.date(0)
        pattern = "%s, %s"
        logger.log(level, pattern, dt, txt)

    def notify_order(self, order):
        size = abs(order.size)
        created_price = round(order.created.price, 2)
        executed_price = round(order.executed.price, 2)
        buy_str = self._is_buy_str(order)
        status_name = order.getstatusname()

        status_msg = f"{status_name}: {buy_str} {size} @"
        created_msg = f"{status_msg} ${created_price}".upper()
        executed_msg = f"{status_msg} ${executed_price}".upper()

        if order.status in [order.Submitted, order.Accepted]:
            self.log(created_msg, level=logging.DEBUG)
            return
        if order.status in [order.Completed]:
            self.log(executed_msg, level=logging.INFO)
            self.executed_orders.append(self.order)
            self.executed_days.append(len(self))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(created_msg, level=logging.WARNING)

        self.order = None

    def notify_trade(self, trade):
        """Adapted from <https://community.backtrader.com/topic/1802/problem-with-multiple-stocks>."""
        if not trade.isclosed:
            return

        self.sum += trade.pnlcomm

        self.log(
            f"OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}, SUM {self.sum:.2f}"
        )


class NaiveStrategy(BaseStrategy):
    """Adapted from <https://www.backtrader.com/docu/quickstart/quickstart>."""

    def __init__(self):
        BaseStrategy.__init__(self)

    def next(self):
        # Check if order is pending.
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Check if closes are decreasing two days in a row.
            if self.data[0] < self.data[-1] and self.data[-1] < self.data[-2]:
                self.order = self.buy()
        else:
            # Sell after 5 days.
            if len(self) >= self.executed_days[-1] + 5:
                self.order = self.sell()


class MeanRevertingStrategy(BaseStrategy):
    """Uses mean reverting strategy based on deviations from moving average,
    with thresholds determined using a scaled standard deviation.

    k (int): Number of points to use in moving average.
    num_std (float): Number of standard deviations from the mean to compute buy
        and sell thresholds.
    """

    params = (("k", 50), ("num_std", 1.0))

    def __init__(self):
        BaseStrategy.__init__(self)

    def next(self):
        if self.order:
            return

        # Not enough history for moving average.
        if len(self) < self.params.k:
            return

        data = np.array(self.data.get(size=self.params.k))
        std = np.std(data, ddof=1)
        mean = np.mean(data)
        current_price = data[-1]
        deviation = np.abs(current_price - mean)

        if deviation < self.params.num_std * std:
            return

        if current_price < mean and not self.position:
            self.order = self.buy()

        if current_price > mean and self.position:
            self.order = self.sell()


class MACrossoverStrategy(BaseStrategy):
    """Uses long-short moving average crossover to determine whether to buy or sell.

    fast_length (int): Number of days in fast moving average.
    slow_length (int): Number of days in slow moving average.
    """

    params = (("fast_length", 5), ("slow_length", 50))

    def __init__(self):
        BaseStrategy.__init__(self)
        ma_fast = bt.ind.SMA(period=self.params.fast_length)
        ma_slow = bt.ind.SMA(period=self.params.slow_length)

        self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.sell()


class CointegrationBollingerBandsStrategy(BaseStrategy):
    """Uses Bollinger Bands mean-reverting technique to determine when to buy
    and sell cointegrated stocks.

    Adapted from "Advanced Algorithmic Trading" by Michael L. Halls-Moore.
    """

    params = (
        ("lookback", 15),
        ("qty", 10000),
        ("z_entry", 1.5),
        ("z_exit", 0.5),
        ("weights", []),
    )

    def __init__(self):
        BaseStrategy.__init__(self)

        self.invested: str = None
        self.portfolio_value = deque(maxlen=self.params.lookback)

    def long(self):
        for weight, data in zip(self.params.weights, self.datas):
            amount = abs(int(weight * self.params.qty))
            if weight < 0.0:
                self.sell(data=data, size=amount)
            else:
                self.buy(data=data, size=amount)

    def short(self):
        for weight, data in zip(self.params.weights, self.datas):
            amount = abs(int(weight * self.params.qty))
            if weight < 0.0:
                self.buy(data=data, size=amount)
            else:
                self.sell(data=data, size=amount)

    def next(self):
        self.portfolio_value.append(np.dot([data[-1] for data in self.datas], self.params.weights))
        if len(self.portfolio_value) < self.params.lookback:
            return
        zscore = (self.portfolio_value[-1] - np.mean(self.portfolio_value[0])) / np.std(
            self.portfolio_value
        )

        if self.invested is None:
            if zscore < -self.params.z_entry:
                self.long()
                self.invested = "long"
            elif zscore > self.params.z_entry:
                self.short()
                self.invested = "short"
        else:
            if self.invested == "long" and zscore > -self.params.z_exit:
                self.short()
                self.invested = None
            elif self.invested == "short" and zscore < self.params.z_exit:
                self.long()
                self.invested = None
