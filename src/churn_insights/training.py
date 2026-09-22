"""Offline training; never imported by the prediction path."""
from sklearn.compose import ColumnTransformer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from .calibration import probability_diagnostics
from .validation import FEATURES, CATEGORIES, validate_data

def train_bundle(data):
    data = validate_data(data, require_target=True)
    features = data[FEATURES]
    target = data["Exited"]
    if target.nunique() != 2:
        raise ValueError("O treinamento exige exemplos com Exited=0 e Exited=1.")
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )
    if y_train.value_counts().min() < 5 or y_test.nunique() != 2:
        raise ValueError("Dados insuficientes por classe para calibração em 5 partições e avaliação separada.")
    preprocessing = ColumnTransformer(
        [("categories", OneHotEncoder(handle_unknown="ignore"), ["Geography", "Gender"])],
        remainder="passthrough",
    )
    model = make_pipeline(preprocessing, RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
    ))
    # Calibration learns only from out-of-fold predictions within the training
    # partition. The external test set is never passed to fit or used to tune it.
    calibrated_model = CalibratedClassifierCV(
        model, method="sigmoid", ensemble=False,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42), n_jobs=1,
    )
    calibrated_model.fit(x_train, y_train)
    test_probability = calibrated_model.predict_proba(x_test)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y_test, test_probability >= 0.5),
        "auc": roc_auc_score(y_test, test_probability),
        "features": len(features.columns),
        "test_count": len(y_test),
        "train_count": len(y_train),
        "calibration": {
            "Calibrado": probability_diagnostics(y_test, test_probability),
        },
    }
    # Keep the untouched test partition available for historical top-N evaluation.
    # Outcomes are used only after ranking; they never enter model features.
    evaluation = data.loc[x_test.index].copy()
    evaluation["churn_probability"] = test_probability
    metrics["evaluation"] = evaluation
    return {"estimator": calibrated_model, "metrics": metrics,
            "categories": {name: sorted(x_train[name].unique().tolist()) for name in CATEGORIES},
            "source_ids": data.CustomerId.tolist()}
