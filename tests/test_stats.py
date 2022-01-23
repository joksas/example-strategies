import numpy as np
from example_strategies import stats


def test_hurst_exponent():
    np.random.seed(0)
    # Mean-reverting, gometric brownian motion and trending series. Adapted
    # from "Successful Algorithmic Trading" by Michael L. Halls-Moore.
    mr = np.log(np.random.randn(100000) + 1000)
    gbm = np.log(np.cumsum(np.random.randn(100000)) + 1000)
    tr = np.log(np.cumsum(np.random.randn(100000) + 1) + 1000)

    h_mr = stats.hurst_exponent(mr)
    h_gbm = stats.hurst_exponent(gbm)
    h_tr = stats.hurst_exponent(tr)

    assert h_mr < h_gbm < h_tr
    assert h_mr < 0.5
    assert h_tr > 0.5
