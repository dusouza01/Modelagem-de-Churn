"""Versioned local artifacts, with integrity and runtime checks before loading."""
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import re
from uuid import uuid4

import joblib

from .validation import FEATURES

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models"
SCHEMA_VERSION = 1


class ArtifactError(ValueError):
    pass


def runtime_versions():
    return {"python": platform.python_version(), **{
        name: version(name) for name in ["scikit-learn", "numpy", "scipy", "pandas", "joblib"]}}


def save_bundle(bundle, data_bytes, directory=MODEL_DIR):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    model_version = now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    destination = directory / model_version
    destination.mkdir()
    artifact = destination / "model.joblib"
    joblib.dump(bundle, artifact, compress=3)
    metadata = {
        "schema_version": SCHEMA_VERSION, "version": model_version,
        "created_at_utc": now.isoformat(), "runtime": runtime_versions(),
        "data_sha256": sha256(data_bytes).hexdigest(),
        "artifact_sha256": sha256(artifact.read_bytes()).hexdigest(),
        "features": FEATURES, "categories": bundle["categories"],
        "source_sha256": {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in
                          ["src/churn_insights/training.py", "src/churn_insights/validation.py",
                           "src/churn_insights/calibration.py", "requirements.txt"]},
        "training": {"test_size": 0.2, "random_state": 42, "calibration": "sigmoid",
                     "folds": 5, "ensemble": False, "n_estimators": 100, "max_depth": 10},
        "metrics": {key: bundle["metrics"][key] for key in
                    ["accuracy", "auc", "features", "test_count", "train_count"]},
        "calibration": {name: {key: value[key] for key in ["brier", "log_loss"]}
                        for name, value in bundle["metrics"]["calibration"].items()},
    }
    (destination / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    pointer = directory / (".current-" + uuid4().hex + ".tmp")
    pointer.write_text(model_version, encoding="utf-8")
    os.replace(pointer, directory / "current.txt")
    return metadata


def active_version(directory=MODEL_DIR):
    try:
        value = (Path(directory) / "current.txt").read_text(encoding="utf-8").strip()
    except OSError as error:
        raise ArtifactError("Modelo ainda não preparado. Execute treinar.bat uma vez.") from error
    if not re.fullmatch(r"\d{8}T\d{6}Z-[a-f0-9]{8}", value):
        raise ArtifactError("Referência de modelo inválida. Execute treinar.bat.")
    return value


def load_bundle(model_version=None, directory=MODEL_DIR):
    directory = Path(directory)
    model_version = model_version or active_version(directory)
    if not re.fullmatch(r"\d{8}T\d{6}Z-[a-f0-9]{8}", model_version):
        raise ArtifactError("Versão inválida.")
    try:
        path = directory / model_version
        metadata = json.loads((path / "metadata.json").read_text(encoding="utf-8"))
        if metadata["schema_version"] != SCHEMA_VERSION or metadata["features"] != FEATURES or metadata["version"] != model_version:
            raise ArtifactError("Contrato do modelo incompatível. Execute treinar.bat.")
        if metadata["runtime"] != runtime_versions():
            raise ArtifactError("As dependências mudaram desde o treinamento. Execute treinar.bat para gerar uma versão compatível.")
        artifact = path / "model.joblib"
        if sha256(artifact.read_bytes()).hexdigest() != metadata["artifact_sha256"]:
            raise ArtifactError("Falha de integridade do modelo. Execute treinar.bat.")
        # Only locally generated artifacts are accepted. Hashes detect corruption,
        # not a malicious replacement of both the binary and its metadata.
        bundle = joblib.load(artifact)
        if not all(key in bundle for key in ["estimator", "metrics", "categories", "source_ids"]):
            raise ArtifactError("Conteúdo do modelo incompleto.")
        return bundle, metadata
    except ArtifactError:
        raise
    except Exception as error:
        raise ArtifactError("Não foi possível abrir o modelo local. Execute treinar.bat.") from error
