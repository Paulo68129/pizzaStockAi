from __future__ import annotations

import numpy as np
from sklearn.linear_model import LinearRegression


def forecast_demand(history: list[float], days: int = 7) -> list[float]:
    """Prevê demanda futura com regressão linear sobre o histórico."""
    if not history:
        return [0.0] * days
    if len(history) < 2:
        return [max(0.0, float(history[-1]))] * days

    x = np.arange(len(history)).reshape(-1, 1)
    y = np.array(history, dtype=float)
    model = LinearRegression().fit(x, y)
    future = np.arange(len(history), len(history) + days).reshape(-1, 1)
    return [max(0.0, round(float(value), 2)) for value in model.predict(future)]
