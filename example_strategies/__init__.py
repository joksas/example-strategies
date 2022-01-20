import logging
import sys

from example_strategies.strategies import (MeanRevertingStrategy,
                                           NaiveStrategy, NoStrategy)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format="%(asctime)s (%(levelname)s): %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
