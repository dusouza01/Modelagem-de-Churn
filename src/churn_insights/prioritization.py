"""Capacity-limited ranking and evaluation against observed test outcomes."""
from numbers import Integral, Real
from math import isfinite

import pandas as pd

PRIORITY_ORDER = ["Prioritário", "Fora da capacidade", "Abaixo do risco mínimo", "Já cancelou", "Não definido"]


def assign_priority(data: pd.DataFrame, capacity: int | None, *, include_exited: bool | None, minimum_risk: float | None = None) -> pd.DataFrame:
    """Apply an explicitly configured capacity to the supplied portfolio segment."""
    result = data.copy()
    result["priority"] = "Não definido"
    if capacity is None or include_exited is None or minimum_risk is None:
        return result
    if not isinstance(include_exited, bool):
        raise ValueError("Escolha o público da priorização.")
    if isinstance(minimum_risk, bool) or not isinstance(minimum_risk, Real) or not isfinite(minimum_risk) or not 0 <= minimum_risk <= 1:
        raise ValueError("O risco mínimo deve ser uma probabilidade entre 0 e 1.")
    eligible = result if include_exited else result[result.Exited == 0]
    eligible = eligible[eligible.churn_probability >= minimum_risk]
    selected = rank_clients(eligible, capacity)
    result["priority"] = "Fora da capacidade"
    result.loc[result.churn_probability < minimum_risk, "priority"] = "Abaixo do risco mínimo"
    if not include_exited:
        result.loc[result.Exited == 1, "priority"] = "Já cancelou"
    result.loc[result.CustomerId.isin(selected.CustomerId), "priority"] = "Prioritário"
    return result


def rank_clients(data: pd.DataFrame, capacity: int) -> pd.DataFrame:
    """Rank by predicted risk, breaking ties by customer ID, never outcome."""
    if isinstance(capacity, bool) or not isinstance(capacity, Integral) or capacity < 0:
        raise ValueError("A capacidade deve ser uma quantidade inteira não negativa.")
    return data.sort_values(
        ["churn_probability", "CustomerId"], ascending=[False, True]
    ).head(int(capacity)).copy()


def evaluate_capacity(test_data: pd.DataFrame, capacity: int) -> dict:
    """Measure historical cancellations captured in the independent test set."""
    selected = rank_clients(test_data, capacity)
    captured = int(selected["Exited"].sum())
    cancellations = int(test_data["Exited"].sum())
    return {
        "selected": len(selected),
        "available": len(test_data),
        "captured": captured,
        "cancellations": cancellations,
        "precision": captured / len(selected) if len(selected) else None,
        "recall": captured / cancellations if cancellations else None,
    }
