"""Read-only prediction using an explicitly trained local model."""
from hashlib import sha256

import streamlit as st

from .artifacts import ROOT, ArtifactError, active_version, load_bundle
from .validation import FEATURES, read_csv_bytes, validate_data


def load_data():
    return read_csv_bytes((ROOT / "data" / "Churn_Modelling.csv").read_bytes(), require_target=True)


@st.cache_resource(show_spinner=False)
def _cached_bundle(model_version):
    return load_bundle(model_version)


def get_model():
    return _cached_bundle(active_version())


def predict_clients(data, bundle):
    result = validate_data(data, categories=bundle["categories"])
    result["churn_probability"] = bundle["estimator"].predict_proba(result[FEATURES])[:, 1]
    return result


def analyze_data(data):
    bundle, metadata = get_model()
    fingerprint = sha256((ROOT / "data" / "Churn_Modelling.csv").read_bytes()).hexdigest()
    if fingerprint != metadata["data_sha256"]:
        raise ArtifactError("A base local mudou desde o treinamento. Execute treinar.bat antes de atualizar a análise histórica.")
    return predict_clients(data, bundle), bundle["metrics"]
