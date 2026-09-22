"""Reliability diagnostics calculated exclusively from evaluation predictions."""
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss


def probability_diagnostics(outcomes, probabilities):
    outcomes = np.asarray(outcomes)
    probabilities = np.asarray(probabilities, dtype=float)
    if outcomes.ndim != 1 or probabilities.ndim != 1 or len(outcomes) != len(probabilities) or not len(outcomes):
        raise ValueError("Informe resultados e probabilidades de mesmo tamanho, não vazios.")
    if not np.isin(outcomes, [0, 1]).all() or not np.isfinite(probabilities).all():
        raise ValueError("Resultados devem ser binários e probabilidades devem ser finitas.")
    if ((probabilities < 0) | (probabilities > 1)).any():
        raise ValueError("Probabilidades devem estar entre zero e um.")
    frame = pd.DataFrame({"outcome": outcomes, "probability": probabilities})
    labels = [f"{value}–{value + 10}%" for value in range(0, 100, 10)]
    frame["interval"] = pd.cut(
        probabilities, bins=np.linspace(0, 1, 11), labels=labels, include_lowest=True,
    )
    reliability = frame.groupby("interval", observed=False).agg(
        clients=("outcome", "size"), predicted=("probability", "mean"),
        observed=("outcome", "mean"),
    ).reset_index()
    return {
        "brier": float(brier_score_loss(outcomes, probabilities)),
        "log_loss": float(log_loss(outcomes, probabilities, labels=[0, 1])),
        "reliability": reliability,
    }
