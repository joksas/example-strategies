import numpy as np
import numpy.typing as npt
from scipy import stats


def hurst_exponent(data: npt.ArrayLike, num_lags: int = 2 ** 6) -> float:
    """Computes Hurst exponent.

    Args:
        data: Time series data.
        num_lags: Number of lags to use in the estimation.

    Returns:
        Hurst exponent.
    """
    # Lags
    taus = np.arange(1, num_lags + 1)

    # Estimate of $\tau^{2H}$
    y_hat = [np.mean(np.power(data[tau:] - data[:-tau], 2)) for tau in taus]

    # We linearise the problem by taking the logarithm of both sides:
    # $\log(\hat{y}) = 2H \log(\tau)$
    # After this, we can estimate $H$ using linear regression. If one plots
    # $\log(\hat{y})$ against $2\log(\tau)$, $H$ will be the slope:
    h, _, _, _, _ = stats.linregress(2 * np.log(taus), np.log(y_hat))

    return h
