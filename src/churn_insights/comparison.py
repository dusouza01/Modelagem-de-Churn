"""Historical strategy comparison on a caller-supplied independent test set.

Random baselines are mathematical expectations for uniform sampling without
replacement, not fabricated customers or results from one favorable random draw.
"""
from numbers import Integral

import pandas as pd

from .prioritization import evaluate_capacity, rank_clients


def _validate(data, capacity):
    if isinstance(capacity, bool) or not isinstance(capacity, Integral) or capacity < 0:
        raise ValueError("Informe uma capacidade inteira não negativa.")
    if not data["Exited"].isin([0, 1]).all():
        raise ValueError("Exited deve conter apenas 0 ou 1, sem valores ausentes.")


def _summary(data, selected, captured):
    cancellations = int(data["Exited"].sum())
    return {
        "selected": selected,
        "available": len(data),
        "captured": captured,
        "cancellations": cancellations,
        "precision": captured / selected if selected else None,
        "recall": captured / cancellations if cancellations else None,
    }


def random_expectation(test_data: pd.DataFrame, capacity: int) -> dict:
    """Exact mean cancellation count over all equal-probability selections."""
    _validate(test_data, capacity)
    selected = min(int(capacity), len(test_data))
    captured = selected * float(test_data["Exited"].mean()) if selected else 0.0
    return _summary(test_data, selected, captured)


def inactivity_expectation(
    test_data: pd.DataFrame, capacity: int, *, complete_with_active: bool
) -> dict:
    """Uniform tie-breaking within activity groups; completion is explicit."""
    _validate(test_data, capacity)
    if not isinstance(complete_with_active, bool):
        raise ValueError("Defina explicitamente se a lista será completada com ativos.")
    if not test_data["IsActiveMember"].isin([0, 1]).all():
        raise ValueError("IsActiveMember deve conter apenas 0 ou 1.")
    inactive = test_data[test_data["IsActiveMember"] == 0]
    active = test_data[test_data["IsActiveMember"] == 1]
    inactive_count = min(int(capacity), len(inactive))
    active_count = min(int(capacity) - inactive_count, len(active)) if complete_with_active else 0
    captured = inactive_count * float(inactive["Exited"].mean()) if inactive_count else 0.0
    if active_count:
        captured += active_count * float(active["Exited"].mean())
    return _summary(test_data, inactive_count + active_count, captured)


def compare_strategies(
    test_data: pd.DataFrame, capacity: int, *, include_inactivity: bool,
    complete_with_active: bool,
) -> pd.DataFrame:
    """Compare all requested strategies on exactly the same population."""
    _validate(test_data, capacity)
    rows = [
        {"strategy": "Modelo", "result_type": "Observado no teste", **evaluate_capacity(test_data, capacity)},
        {"strategy": "Aleatória", "result_type": "Média esperada do sorteio", **random_expectation(test_data, capacity)},
    ]
    if include_inactivity:
        rows.append({
            "strategy": "Inativos primeiro", "result_type": "Média esperada do desempate",
            **inactivity_expectation(test_data, capacity, complete_with_active=complete_with_active),
        })
    for row in rows:
        selected = row["selected"]
        if row["strategy"] == "Modelo":
            predicted = float(rank_clients(test_data, capacity).churn_probability.sum())
        elif row["strategy"] == "Aleatória":
            predicted = selected * float(test_data.churn_probability.mean()) if selected else 0.0
        else:
            inactive = test_data[test_data.IsActiveMember == 0]
            active = test_data[test_data.IsActiveMember == 1]
            inactive_count = min(int(capacity), len(inactive))
            active_count = selected - inactive_count
            predicted = inactive_count * float(inactive.churn_probability.mean()) if inactive_count else 0.0
            if active_count:
                predicted += active_count * float(active.churn_probability.mean())
        row["predicted_cancellations"] = predicted
        row["predicted_rate"] = predicted / selected if selected else None
        row["probability_gap_pp"] = (row["predicted_rate"] - row["precision"]) * 100 if selected else None
    return pd.DataFrame(rows)
