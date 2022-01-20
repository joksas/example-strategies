import datetime
import logging

import backtrader as bt
import numpy as np

logger = logging.getLogger(__name__)


class NoStrategy(bt.Strategy):
    def __init__(self):
        pass

    def next(self):
        pass


class NaiveStrategy(bt.Strategy):
    """Adapted from <https://www.backtrader.com/docu/quickstart/quickstart>."""

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def log(self, txt: str, dt: datetime.date = None):
        dt = dt or self.datas[0].datetime.date(0)
        logger.info("%s, %s", dt, txt)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED, {order.executed.price:.2f}")
            elif order.issell():
                self.log(f"SELL EXECUTED, {order.executed.price:.2f}")

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        # Write down: no pending order
        self.order = None

    def next(self):
        self.log(f"Close, {self.dataclose[0]:.2f}")

        # Check if order is pending.
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Check if closes are decreasing two days in a row.
            if self.dataclose[0] < self.dataclose[-1] and self.dataclose[-1] < self.dataclose[-2]:
                self.log(f"BUY CREATE, {self.dataclose[0]:.2f}")
                self.order = self.buy()
        else:
            # Sell after 5 days.
            if len(self) >= (self.bar_executed + 5):
                self.log(f"SELL CREATE, {self.dataclose[0]:.2f}")
                self.order = self.sell()


class MeanRevertingStrategy(bt.Strategy):
    """
    k: Number of points to use in moving average.
    num_std: Number of standard deviations from the mean to compute buy
        and sell thresholds.
    """

    params = (("k", 50), ("num_std", 1.0))
