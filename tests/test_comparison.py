"""Synthetic fixtures check arithmetic only; no fixture is shown in the app."""
import unittest

import pandas as pd

from src.churn_insights.comparison import compare_strategies, inactivity_expectation, random_expectation


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "CustomerId": [1, 2, 3, 4],
            "churn_probability": [0.9, 0.8, 0.2, 0.1],
            "Exited": [1, 0, 1, 0],
            "IsActiveMember": [0, 0, 1, 1],
        })

    def test_random_expectation_and_population_limit(self):
        self.assertEqual(random_expectation(self.data, 1)["captured"], 0.5)
        self.assertEqual(random_expectation(self.data, 2)["captured"], 1)
        result = random_expectation(self.data, 100)
        self.assertEqual(result["selected"], 4)
        self.assertEqual(result["captured"], 2)

    def test_completion_policy_changes_selected_count(self):
        complete = inactivity_expectation(self.data, 3, complete_with_active=True)
        incomplete = inactivity_expectation(self.data, 3, complete_with_active=False)
        self.assertEqual((complete["selected"], complete["captured"]), (3, 1.5))
        self.assertEqual((incomplete["selected"], incomplete["captured"]), (2, 1))

    def test_order_does_not_change_random_baselines(self):
        reversed_data = self.data.iloc[::-1]
        self.assertEqual(random_expectation(self.data, 1), random_expectation(reversed_data, 1))
        self.assertEqual(
            inactivity_expectation(self.data, 1, complete_with_active=True),
            inactivity_expectation(reversed_data, 1, complete_with_active=True),
        )

    def test_empty_and_zero_capacity(self):
        for frame, capacity in [(self.data.iloc[:0], 10), (self.data, 0)]:
            result = random_expectation(frame, capacity)
            self.assertEqual(result["captured"], 0)
            self.assertIsNone(result["precision"])
        self.assertIsNone(random_expectation(self.data.assign(Exited=0), 2)["recall"])

    def test_estimated_and_observed_probabilities(self):
        result = compare_strategies(self.data, 2, include_inactivity=True, complete_with_active=True).set_index("strategy")
        self.assertAlmostEqual(result.loc["Modelo", "predicted_rate"], .85)
        self.assertEqual(result.loc["Modelo", "precision"], .5)
        self.assertAlmostEqual(result.loc["Modelo", "probability_gap_pp"], 35)
        self.assertAlmostEqual(result.loc["Aleatória", "predicted_rate"], .5)
        self.assertAlmostEqual(result.loc["Inativos primeiro", "predicted_rate"], .85)
        completed = compare_strategies(self.data, 3, include_inactivity=True, complete_with_active=True).set_index("strategy")
        self.assertAlmostEqual(completed.loc["Inativos primeiro", "predicted_rate"], (1.7 + .15) / 3)
        full = compare_strategies(self.data, 100, include_inactivity=True, complete_with_active=True)
        self.assertTrue((abs(full.predicted_rate - .5) < 1e-10).all())
        empty = compare_strategies(self.data, 0, include_inactivity=True, complete_with_active=True)
        self.assertTrue(empty.predicted_rate.isna().all())

    def test_shared_population_and_explicit_strategy_choice(self):
        result = compare_strategies(self.data, 2, include_inactivity=True, complete_with_active=True)
        self.assertEqual(result.available.tolist(), [4, 4, 4])
        self.assertEqual(result.cancellations.tolist(), [2, 2, 2])
        self.assertEqual(result.selected.tolist(), [2, 2, 2])
        self.assertEqual(len(compare_strategies(self.data, 2, include_inactivity=False, complete_with_active=False)), 2)


if __name__ == "__main__":
    unittest.main()
