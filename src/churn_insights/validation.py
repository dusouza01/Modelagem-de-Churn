"""Explicit data contract shared by training and CSV inference."""
import csv
from io import StringIO

import numpy as np
import pandas as pd

FEATURES = ["CreditScore", "Geography", "Gender", "Age", "Tenure", "Balance",
            "NumOfProducts", "HasCrCard", "IsActiveMember", "EstimatedSalary"]
IDENTITY = ["CustomerId", "Surname"]
CATEGORIES = ["Geography", "Gender"]
INTEGERS = ["CustomerId", "CreditScore", "Age", "Tenure", "NumOfProducts",
            "HasCrCard", "IsActiveMember", "Exited"]
MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 100_000


class DataValidationError(ValueError):
    """A file cannot safely be used under the declared data contract."""


def validate_data(frame, *, require_target=False, categories=None):
    required = IDENTITY + FEATURES + (["Exited"] if require_target else [])
    errors = []
    if frame.columns.duplicated().any():
        errors.append("Há nomes de colunas repetidos.")
    missing = [name for name in required if name not in frame]
    if missing:
        errors.append("Colunas ausentes: " + ", ".join(missing) + ".")
    if frame.empty or len(frame) > MAX_ROWS:
        errors.append(f"Informe entre 1 e {MAX_ROWS:,} linhas.")
    if errors:
        raise DataValidationError("\n".join(errors))
    columns = IDENTITY + FEATURES + (["Exited"] if "Exited" in frame else [])
    result = frame[columns].copy().reset_index(drop=True)
    for name in columns:
        values = result[name]
        if name in CATEGORIES + ["Surname"]:
            values = values.astype("string").str.strip()
            invalid = values.isna() | values.eq("")
            if categories is not None and name in CATEGORIES:
                invalid |= ~values.isin(categories[name])
        else:
            values = pd.to_numeric(values, errors="coerce")
            invalid = values.isna() | ~np.isfinite(values) | (values < 0)
            if name in INTEGERS:
                invalid |= (values % 1 != 0) | (values >= 2**63)
            if name in ["HasCrCard", "IsActiveMember", "Exited"]:
                invalid |= ~values.isin([0, 1])
        if invalid.any():
            lines = ", ".join(str(i + 2) for i in result.index[invalid][:5])
            errors.append(f"{name}: {int(invalid.sum())} valor(es) ausente(s) ou inválido(s); linhas {lines}.")
        else:
            result[name] = values.astype("int64") if name in INTEGERS else values
    if result.CustomerId.duplicated().any():
        errors.append("CustomerId deve ser único; há IDs repetidos.")
    if errors:
        raise DataValidationError("\n".join(errors))
    return result


def read_csv_bytes(payload, *, require_target=False, categories=None):
    if len(payload) > MAX_BYTES:
        raise DataValidationError("O limite é 10 MiB por arquivo.")
    try:
        text = payload.decode("utf-8-sig")
        reader = csv.reader(StringIO(text), delimiter=",", strict=True)
        header = next(reader)
        if len(header) != len(set(header)):
            raise DataValidationError("Há nomes de colunas repetidos no CSV.")
        for line, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise DataValidationError(f"Linha {line}: quantidade de campos diferente do cabeçalho.")
        frame = pd.read_csv(StringIO(text), dtype=str, keep_default_na=False)
    except (UnicodeDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError, StopIteration, csv.Error) as error:
        raise DataValidationError("CSV inválido. Use UTF-8, vírgulas entre campos e ponto decimal.") from error
    return validate_data(frame, require_target=require_target, categories=categories)
