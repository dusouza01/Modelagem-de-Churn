"""Imported clients are scored without refitting or changing the reference base."""
from sklearn.metrics import accuracy_score, roc_auc_score

from .calibration import probability_diagnostics
from .model import predict_clients
from .validation import read_csv_bytes


def analyze_import(payload, bundle, *, historical):
    data = read_csv_bytes(payload, require_target=historical, categories=bundle["categories"])
    predictions = predict_clients(data, bundle)
    overlap = predictions.CustomerId.isin(bundle["source_ids"])
    metrics = None
    if historical and not overlap.any():
        target = predictions.Exited
        probabilities = predictions.churn_probability
        metrics = probability_diagnostics(target, probabilities)
        metrics["accuracy"] = float(accuracy_score(target, probabilities >= 0.5))
        metrics["auc"] = float(roc_auc_score(target, probabilities)) if target.nunique() == 2 else None
    return predictions, metrics, int(overlap.sum())
