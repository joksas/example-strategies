import datetime
import logging

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
        size = order.size
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
            # Buy using 95% of the available cash.
            self.order = self.order_target_value(target=0.95 * self.broker.get_cash())

        if current_price > mean and self.position:
            self.order = self.sell(size=self.position.size)
