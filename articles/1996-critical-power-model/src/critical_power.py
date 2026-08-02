"""
Critical Power Model (2-parameter and 3-parameter formulations).

Based on Morton (1996): A 3-parameter critical power model.
https://doi.org/10.1080/00140139608964484
"""

import numpy as np
from scipy.optimize import curve_fit


def hyperbolic_model_2param(power, awc, cp):
    """
    2-parameter hyperbolic critical power model.

    (P - CP) * t = AWC  =>  t = AWC / (P - CP)

    Parameters
    ----------
    power : float or array-like
        Power output (watts).
    awc : float
        Anaerobic work capacity (joules).
    cp : float
        Critical power (watts).

    Returns
    -------
    float or array-like
        Time to exhaustion (seconds).
    """
    return awc / (power - cp)


def hyperbolic_model_3param(power, awc, cp, k):
    """
    3-parameter hyperbolic critical power model with time asymptote.

    (P - CP) * (t - k) = AWC  =>  t = AWC / (P - CP) + k

    Parameters
    ----------
    power : float or array-like
        Power output (watts).
    awc : float
        Anaerobic work capacity (joules).
    cp : float
        Critical power (watts).
    k : float
        Time asymptote (seconds). Negative in Morton's results.

    Returns
    -------
    float or array-like
        Time to exhaustion (seconds).
    """
    return awc / (power - cp) + k


def power_from_pmax(time, awc, cp, pmax):
    """
    Alternate 3-parameter parameterization using P_max instead of k.

    Relates k and P_max via: k = AWC / (CP - P_max)

    Parameters
    ----------
    time : float or array-like
        Time to exhaustion (seconds).
    awc : float
        Anaerobic work capacity (joules).
    cp : float
        Critical power (watts).
    pmax : float
        Maximal instantaneous power (watts).

    Returns
    -------
    float or array-like
        Power output (watts).
    """
    return cp + awc / (time - awc / (cp - pmax))


class ThreeParameterCPModel:
    """Fitted 3-parameter critical power model."""

    def __init__(self, awc, cp, k, awc_se=None, cp_se=None, k_se=None):
        """
        Initialize with fitted parameters.

        Parameters
        ----------
        awc : float
            Anaerobic work capacity (joules).
        cp : float
            Critical power (watts).
        k : float
            Time asymptote (seconds).
        awc_se : float, optional
            Standard error of AWC.
        cp_se : float, optional
            Standard error of CP.
        k_se : float, optional
            Standard error of k.
        """
        self.awc = awc
        self.cp = cp
        self.k = k
        self.awc_se = awc_se
        self.cp_se = cp_se
        self.k_se = k_se

    @property
    def pmax(self):
        """Maximal instantaneous power (watts)."""
        if self.k < 0:
            return self.cp + self.awc / (-self.k)
        return None

    def predict(self, power):
        """
        Predict time to exhaustion at given power.

        Parameters
        ----------
        power : float or array-like
            Power output (watts).

        Returns
        -------
        float or array-like
            Predicted time to exhaustion (seconds).
        """
        return hyperbolic_model_3param(power, self.awc, self.cp, self.k)

    def residuals(self, power, time):
        """
        Calculate residuals between predicted and observed times.

        Parameters
        ----------
        power : array-like
            Power outputs (watts).
        time : array-like
            Observed times to exhaustion (seconds).

        Returns
        -------
        array-like
            Residuals.
        """
        predicted = self.predict(power)
        return time - predicted

    def rss(self, power, time):
        """
        Residual sum of squares.

        Parameters
        ----------
        power : array-like
            Power outputs (watts).
        time : array-like
            Observed times to exhaustion (seconds).

        Returns
        -------
        float
            RSS.
        """
        return np.sum(self.residuals(power, time) ** 2)

    def rms(self, power, time):
        """
        Residual mean square.

        Parameters
        ----------
        power : array-like
            Power outputs (watts).
        time : array-like
            Observed times to exhaustion (seconds).

        Returns
        -------
        float
            RMS.
        """
        return self.rss(power, time) / len(power)


def fit_cp_model(power, time, model="3param", p0=None, weights=None, maxfev=10000):
    """
    Fit critical power model to data using weighted least squares.

    Parameters
    ----------
    power : array-like
        Power outputs (watts).
    time : array-like
        Times to exhaustion (seconds).
    model : str, default "3param"
        Model to fit: "2param" or "3param".
    p0 : tuple, optional
        Initial guess for parameters. If None, uses heuristics.
    weights : array-like, optional
        Weights for each observation. If None, all weights are 1.
        Following Morton's approach, weights are typically proportional to time^2.
    maxfev : int, default 10000
        Maximum number of function evaluations.

    Returns
    -------
    dict
        Dictionary with keys:
        - "model": fitted ThreeParameterCPModel or dict with awc, cp
        - "popt": optimized parameters
        - "pcov": covariance matrix
        - "residuals": residuals
        - "rss": residual sum of squares
        - "rms": residual mean square
    """
    power = np.asarray(power, dtype=float)
    time = np.asarray(time, dtype=float)

    weights = np.ones_like(time) if weights is None else np.asarray(weights, dtype=float)

    sigma = 1.0 / weights

    if model == "2param":

        def func(x, awc, cp):
            return hyperbolic_model_2param(x, awc, cp)

        if p0 is None:
            awc_init = np.mean(time) * np.mean(power - np.min(power))
            cp_init = np.min(power) + 10
            p0 = [max(awc_init, 1000), cp_init]

        popt, pcov = curve_fit(
            func, power, time, p0=p0, sigma=sigma, maxfev=maxfev, ftol=1e-9, xtol=1e-9
        )

        awc, cp = popt
        result_model = {"awc": awc, "cp": cp}

    elif model == "3param":

        def func(x, awc, cp, k):
            return hyperbolic_model_3param(x, awc, cp, k)

        if p0 is None:
            awc_init = np.mean(time) * np.mean(power - np.min(power))
            cp_init = np.min(power) + 10
            k_init = -10
            p0 = [max(awc_init, 1000), cp_init, k_init]

        try:
            popt, pcov = curve_fit(
                func, power, time, p0=p0, sigma=sigma, maxfev=maxfev, ftol=1e-9, xtol=1e-9
            )
        except RuntimeError:  # pragma: no cover
            popt, pcov = curve_fit(  # pragma: no cover
                func, power, time, p0=p0, maxfev=maxfev * 2, ftol=1e-5, xtol=1e-5
            )

        awc, cp, k = popt
        perr = np.sqrt(np.diag(pcov))

        result_model = ThreeParameterCPModel(
            awc=awc, cp=cp, k=k, awc_se=perr[0], cp_se=perr[1], k_se=perr[2]
        )

    else:
        raise ValueError(f"Unknown model: {model}. Use '2param' or '3param'.")

    predicted = func(power, *popt)
    residuals = time - predicted
    rss = np.sum(residuals**2)
    rms = rss / len(power)

    return {
        "model": result_model,
        "popt": popt,
        "pcov": pcov,
        "residuals": residuals,
        "rss": rss,
        "rms": rms,
    }
