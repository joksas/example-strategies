import numpy as np
from example_strategies import stats


def test_hurst_exponent():
    np.random.seed(0)
    # Gometric Brownian Motion, Mean-Reverting and Trending Series. Adapted
    # from "Successful Algorithmic Trading" by Michael L. Halls-Moore.
    gbm = np.log(np.cumsum(np.random.randn(100000)) + 1000)
    mr = np.log(np.random.randn(100000) + 1000)
    tr = np.log(np.cumsum(np.random.randn(100000) + 1) + 1000)

    assert stats.hurst_exponent(mr) < stats.hurst_exponent(gbm) < stats.hurst_exponent(tr)
