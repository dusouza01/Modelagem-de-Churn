"""Explicit offline training: python train.py. No uploaded files are used."""
from src.churn_insights.artifacts import ROOT, save_bundle
from src.churn_insights.training import train_bundle
from src.churn_insights.validation import read_csv_bytes


def main():
    payload = (ROOT / "data" / "Churn_Modelling.csv").read_bytes()
    data = read_csv_bytes(payload, require_target=True)
    bundle = train_bundle(data)
    metadata = save_bundle(bundle, payload)
    print(f"Modelo salvo e ativado: {metadata['version']}")
    print(f"Treino: {metadata['metrics']['train_count']} | Teste: {metadata['metrics']['test_count']}")


if __name__ == "__main__":
    main()
