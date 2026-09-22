"""Generate an auditable report from the active model, without training."""
import argparse
from hashlib import sha256
import json

from src.churn_insights.artifacts import ROOT, load_bundle
from src.churn_insights.comparison import compare_strategies


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capacidade", type=int, help="Quantidade escolhida para comparar estratégias; sem valor padrão.")
    args = parser.parse_args()
    if args.capacidade is not None and args.capacidade < 1:
        parser.error("A capacidade deve ser um inteiro positivo.")
    bundle, metadata = load_bundle()
    payload = (ROOT / "data" / "Churn_Modelling.csv").read_bytes()
    if sha256(payload).hexdigest() != metadata["data_sha256"]:
        parser.error("A base local mudou. Execute treinar.bat antes de gerar o relatório.")
    metrics = bundle["metrics"]
    report = {"model_version": metadata["version"], "trained_at_utc": metadata["created_at_utc"],
              "data_sha256": metadata["data_sha256"], "runtime": metadata["runtime"],
              "metrics": metadata["metrics"], "calibration": {"Calibrado": metadata["calibration"]["Calibrado"]},
              "requested_capacity": args.capacidade}
    lines = ["# Resultados do modelo ativo", "", "Gerado por `report.py` a partir do artefato local, sem novo treinamento.", "",
             f"- Versão: `{metadata['version']}`", f"- Treinado em UTC: `{metadata['created_at_utc']}`",
             f"- SHA-256 da base: `{metadata['data_sha256']}`",
             f"- Treino: {metrics['train_count']} clientes; teste: {metrics['test_count']} clientes.",
             f"- Variáveis preditoras: {metrics['features']}.", "", "## Avaliação separada", "",
             "| Métrica | Resultado |", "|---|---:|",
             f"| Acurácia (corte de 50%) | {metrics['accuracy']:.6f} |",
             f"| ROC AUC | {metrics['auc']:.6f} |", "",
             "| Probabilidades | Brier | Log loss |", "|---|---:|---:|"]
    for name, values in report["calibration"].items():
        lines.append(f"| {name} | {values['brier']:.6f} | {values['log_loss']:.6f} |")
    lines += ["", "## Comparação por capacidade", ""]
    if args.capacidade is None:
        lines.append("Não calculada: nenhuma capacidade foi informada. Para incluir, execute `python report.py --capacidade N`, substituindo N pela quantidade escolhida.")
    else:
        comparison = compare_strategies(metrics["evaluation"], args.capacidade,
                                        include_inactivity=True, complete_with_active=True)
        report["comparison"] = comparison.to_dict(orient="records")
        lines += [f"Capacidade solicitada: {args.capacidade}. A seleção é limitada ao tamanho do teste.", "",
                  "| Estratégia | Selecionados | Cancelamentos identificados | Precisão | Cobertura | Natureza |",
                  "|---|---:|---:|---:|---:|---|"]
        for row in report["comparison"]:
            lines.append(f"| {row['strategy']} | {row['selected']} | {row['captured']:.3f} | {row['precision']:.6f} | {row['recall']:.6f} | {row['result_type']} |")
    lines += ["", "## Limites da evidência", "",
              "As métricas usam o teste histórico completo. A carteira exibida também contém registros de treino e não deve ser usada para alegar desempenho independente.", "",
              "A base não registra datas nem resultados de campanhas. Cancelamentos identificados não são cancelamentos evitados; saldo não é receita recuperada. Não há garantia de desempenho futuro nem estimativa de retorno financeiro.", "",
              "As estratégias aleatórias são expectativas matemáticas, não campanhas observadas. O método de calibração foi definido no treino; o teste não foi usado para ajustar a calibração.", "",
              "O relatório representa a versão identificada acima. Gere novamente após ativar outro modelo.", ""]
    destination = ROOT / "doc"
    destination.mkdir(exist_ok=True)
    (destination / "resultados-modelo.md").write_text("\n".join(lines), encoding="utf-8")
    (destination / "resultados-modelo.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print("Relatórios gerados em doc/resultados-modelo.md e doc/resultados-modelo.json")


if __name__ == "__main__":
    main()
