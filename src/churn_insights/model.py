"""Local data loading and reproducible model training."""
from pathlib import Path

import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[2]
RISK_ORDER = ["Baixo", "Médio", "Alto"]


@st.cache_data
def load_data():
    return pd.read_csv(ROOT / "data" / "Churn_Modelling.csv").drop(columns="RowNumber", errors="ignore")


@st.cache_data(show_spinner=False)
def analyze_data(data):
    features = data.drop(columns=["CustomerId", "Surname", "Exited"])
    target = data["Exited"]
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )
    preprocessing = ColumnTransformer(
        [("categories", OneHotEncoder(handle_unknown="ignore"), ["Geography", "Gender"])],
        remainder="passthrough",
    )
    model = make_pipeline(preprocessing, RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
    ))
    model.fit(x_train, y_train)
    test_probability = model.predict_proba(x_test)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y_test, test_probability >= 0.5),
        "auc": roc_auc_score(y_test, test_probability),
        "features": len(features.columns),
        "test_count": len(y_test),
    }
    result = data.copy()
    result["churn_probability"] = model.predict_proba(features)[:, 1]
    result["risk_level"] = pd.cut(
        result["churn_probability"], bins=[-0.01, 0.33, 0.67, 1.01],
        labels=RISK_ORDER, right=False,
    ).astype(str)
    return result, metrics
