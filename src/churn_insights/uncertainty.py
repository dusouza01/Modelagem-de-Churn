"""Sampling uncertainty for observed churn rates, independent of model fitting."""
from statistics import NormalDist

import numpy as np


def observed_intervals(reliability):
    """Add pointwise 95% Wilson intervals; empty bins remain undefined."""
    result = reliability.copy()
    n = result.clients.where(result.clients > 0).astype(float)
    p = result.observed
    z = NormalDist().inv_cdf(0.975)
    denominator = 1 + z ** 2 / n
    center = (p + z ** 2 / (2 * n)) / denominator
    radius = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denominator
    result["lower"] = (center - radius).clip(0, 1)
    result["upper"] = (center + radius).clip(0, 1)
    return result
