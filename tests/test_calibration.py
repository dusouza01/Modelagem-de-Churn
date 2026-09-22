"""Synthetic arithmetic fixtures, never displayed as business results."""
import unittest

from src.churn_insights.calibration import probability_diagnostics


class CalibrationTests(unittest.TestCase):
    def test_perfect_predictions_and_boundary_bins(self):
        result = probability_diagnostics([0, 1], [0.0, 1.0])
        self.assertEqual(result["brier"], 0)
        self.assertLess(result["log_loss"], 1e-12)
        table = result["reliability"]
        self.assertEqual(table.clients.sum(), 2)
        self.assertEqual(table.iloc[0].clients, 1)
        self.assertEqual(table.iloc[-1].clients, 1)
        self.assertTrue(table.loc[table.clients == 0, "observed"].isna().all())

    def test_means_and_brier_are_calculated(self):
        result = probability_diagnostics([0, 1], [0.2, 0.2])
        self.assertAlmostEqual(result["brier"], 0.34)
        populated = result["reliability"].query("clients > 0")
        self.assertEqual(len(populated), 1)
        self.assertAlmostEqual(populated.iloc[0].observed, 0.5)
        self.assertAlmostEqual(populated.iloc[0].predicted, 0.2)

    def test_invalid_predictions_rejected(self):
        for outcomes, probabilities in [([], []), ([0], [0.5, 0.2]), ([0], [float('nan')]), ([0], [1.1]), ([2], [0.5])]:
            with self.assertRaises(ValueError):
                probability_diagnostics(outcomes, probabilities)


if __name__ == "__main__":
    unittest.main()
