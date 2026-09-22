"""Verify exported metrics and localized CSV round-trip."""
from io import BytesIO
import unittest
import pandas as pd
from src.churn_insights.comparison_export import comparison_csv

class ComparisonExportTests(unittest.TestCase):
    def setUp(self):
        # Synthetic calculation fixtures, never displayed as project outcomes.
        self.data = pd.DataFrame({"CustomerId": [1, 2, 3, 4], "Exited": [1, 1, 0, 0],
                                  "IsActiveMember": [0, 1, 1, 1], "churn_probability": [.9, .8, .2, .1]})
        self.metadata = {"version": "test-version", "created_at_utc": "test-time", "data_sha256": "test-hash"}

    def export(self, data, capacity, complete=True):
        payload = comparison_csv(data, capacity, self.metadata, complete_with_active=complete)
        self.assertTrue(payload.startswith(b"\xef\xbb\xbf"))
        result = pd.read_csv(BytesIO(payload), sep=";", decimal=",", encoding="utf-8-sig")
        self.assertEqual(len(result), 3)
        self.assertTrue((result["Versão do modelo"] == "test-version").all())
        return result

    def test_metrics_and_localized_roundtrip(self):
        result = self.export(self.data, 2).set_index("Estratégia")
        model = result.loc["Modelo"]
        self.assertEqual(model["Precisão da seleção (%)"], 100)
        self.assertAlmostEqual(model["Probabilidade média estimada (%)"], 85)
        self.assertAlmostEqual(model["Cancelamentos estimados pelo modelo (soma das probabilidades)"], 1.7)
        self.assertAlmostEqual(model["Estimado menos histórico (p.p.)"], -15)
        self.assertEqual(model["Cobertura dos cancelamentos (%)"], 100)
        self.assertEqual(model["Lift versus sorteio (vezes)"], 2)
        self.assertEqual(model["Diferença de precisão versus sorteio (p.p.)"], 50)
        self.assertEqual(model["Diferença de cancelamentos versus sorteio"], 1)
        self.assertAlmostEqual(result.loc["Inativos primeiro", "Cancelamentos identificados"], 4/3, places=6)
        self.assertEqual(result.loc["Aleatória", "Lift versus sorteio (vezes)"], 1)

    def test_cap_and_missing_denominators(self):
        result = self.export(self.data, 10)
        self.assertTrue((result["Clientes selecionados"] == 4).all())
        self.assertTrue((result["Vagas não utilizadas"] == 6).all())
        self.assertTrue((result["Utilização da capacidade (%)"] == 40).all())
        result = self.export(self.data.assign(Exited=0), 2)
        self.assertTrue(result["Lift versus sorteio (vezes)"].isna().all())
        self.assertTrue(result["Cobertura dos cancelamentos (%)"].isna().all())
        result = self.export(self.data, 0)
        self.assertTrue(result["Precisão da seleção (%)"].isna().all())

    def test_incomplete_strategy_uses_own_sample_size(self):
        row = self.export(self.data, 3, complete=False).set_index("Estratégia").loc["Inativos primeiro"]
        self.assertEqual(row["Clientes selecionados"], 1)
        self.assertEqual(row["Cancelamentos esperados por sorteio de mesmo tamanho"], .5)
        self.assertEqual(row["Diferença de cancelamentos versus sorteio"], .5)

if __name__ == "__main__":
    unittest.main()
