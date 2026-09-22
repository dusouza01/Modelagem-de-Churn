"""Self-contained, spreadsheet-friendly historical strategy report."""
from datetime import datetime, timezone

import pandas as pd

from .comparison import compare_strategies


def comparison_csv(test_data, capacity, metadata, *, complete_with_active):
    results = compare_strategies(test_data, capacity, include_inactivity=True,
                                complete_with_active=complete_with_active)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rules = {
        "Modelo": "Maiores probabilidades calibradas; desempate por CustomerId",
        "Aleatória": "Seleção uniforme sem reposição; expectativa matemática exata",
        "Inativos primeiro": "IsActiveMember=0; desempate uniforme entre inativos; " + (
            "completa vagas por sorteio entre ativos" if complete_with_active else "não completa vagas com ativos"),
    }
    rows = []
    for row in results.to_dict(orient="records"):
        available, selected, captured = row["available"], row["selected"], row["captured"]
        rate = row["cancellations"] / available if available else None
        expected = selected * rate if rate is not None else None
        precision = row["precision"]
        rows.append({
            "Estratégia": row["strategy"],
            "Natureza do resultado": row["result_type"],
            "Capacidade solicitada (clientes)": capacity,
            "Clientes selecionados": selected,
            "Vagas não utilizadas": capacity - selected,
            "Utilização da capacidade (%)": selected / capacity * 100 if capacity else None,
            "Base de teste (clientes)": available,
            "Cancelamentos na base": row["cancellations"],
            "Taxa de churn da base (%)": rate * 100 if rate is not None else None,
            "Base selecionada (%)": selected / available * 100 if available else None,
            "Cancelamentos identificados": captured,
            "Selecionados sem cancelamento histórico": selected - captured,
            "Cancelamentos não identificados": row["cancellations"] - captured,
            "Cancelamentos estimados pelo modelo (soma das probabilidades)": row["predicted_cancellations"],
            "Probabilidade média estimada (%)": row["predicted_rate"] * 100 if pd.notna(row["predicted_rate"]) else None,
            "Estimado menos histórico (p.p.)": row["probability_gap_pp"],
            "Precisão da seleção (%)": precision * 100 if pd.notna(precision) else None,
            "Cobertura dos cancelamentos (%)": row["recall"] * 100 if pd.notna(row["recall"]) else None,
            "Cancelamentos esperados por sorteio de mesmo tamanho": expected,
            "Diferença de cancelamentos versus sorteio": captured - expected if expected is not None else None,
            "Diferença de precisão versus sorteio (p.p.)": (precision - rate) * 100 if pd.notna(precision) and rate is not None else None,
            "Lift versus sorteio (vezes)": precision / rate if pd.notna(precision) and rate else None,
            "Regra de seleção": rules[row["strategy"]],
            "População avaliada": "Teste histórico completo; filtros, público e risco mínimo da carteira não aplicados",
            "Modelo": "Random Forest com calibração sigmoide",
            "Versão do modelo": metadata["version"],
            "Treinamento (UTC)": metadata["created_at_utc"],
            "Exportação (UTC)": generated_at,
            "SHA-256 da base de referência": metadata["data_sha256"],
            "Interpretação": "Contagens de estratégias com sorteio são médias esperadas e podem ser fracionárias. Identificar churn não equivale a evitar cancelamento. Campos vazios indicam métrica sem denominador.",
        })
    return pd.DataFrame(rows).to_csv(index=False, sep=";", decimal=",", float_format="%.6f",
                                    na_rep="", lineterminator="\r\n").encode("utf-8-sig")
