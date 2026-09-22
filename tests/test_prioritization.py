"""Run: python -m unittest discover -s tests -p test_prioritization.py."""
import unittest

import pandas as pd

from src.churn_insights.prioritization import assign_priority, evaluate_capacity, rank_clients


class PrioritizationTests(unittest.TestCase):
    def setUp(self):
        # Synthetic fixtures verify calculations; these are not dashboard data.
        self.data = pd.DataFrame({
            "CustomerId": [30, 20, 10, 40],
            "churn_probability": [0.8, 0.9, 0.8, 0.1],
            "Exited": [1, 0, 1, 0],
        })

    def test_ranking_uses_risk_and_deterministic_ties(self):
        self.assertEqual(rank_clients(self.data, 2).CustomerId.tolist(), [20, 10])
        changed_outcomes = self.data.assign(Exited=1 - self.data.Exited)
        self.assertEqual(rank_clients(changed_outcomes, 2).CustomerId.tolist(), [20, 10])

    def test_historical_metrics(self):
        result = evaluate_capacity(self.data, 2)
        self.assertEqual(result["captured"], 1)
        self.assertEqual(result["cancellations"], 2)
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["recall"], 0.5)

    def test_capacity_larger_than_available_never_duplicates_clients(self):
        result = evaluate_capacity(self.data, 100)
        self.assertEqual(result["selected"], 4)
        self.assertEqual(result["captured"], 2)
        self.assertEqual(result["recall"], 1)

    def test_empty_selection_and_no_cancellations(self):
        result = evaluate_capacity(self.data.iloc[:0], 2)
        self.assertEqual(result["selected"], 0)
        self.assertIsNone(result["precision"])
        self.assertIsNone(result["recall"])
        self.assertIsNone(evaluate_capacity(self.data.assign(Exited=0), 2)["recall"])
        self.assertEqual(len(rank_clients(self.data, 0)), 0)

    def test_invalid_capacity_rejected(self):
        for invalid in (-1, 1.5, True, "2"):
            with self.assertRaises(ValueError):
                rank_clients(self.data, invalid)

    def test_priority_requires_both_user_inputs(self):
        for capacity, scope in [(None, None), (2, None), (None, False)]:
            result = assign_priority(self.data, capacity, include_exited=scope)
            self.assertEqual(set(result.priority), {"Não definido"})

    def test_contact_scope_excludes_cancelled_customers(self):
        result = assign_priority(self.data, 1, include_exited=False, minimum_risk=0.0)
        self.assertEqual(result.query("priority == 'Prioritário'").CustomerId.tolist(), [20])
        self.assertTrue((result.loc[result.Exited == 1, "priority"] == "Já cancelou").all())
        self.assertNotIn("priority", self.data.columns)

    def test_threshold_never_backfills_below_minimum(self):
        result = assign_priority(self.data, 10, include_exited=True, minimum_risk=0.8)
        self.assertEqual(set(result.query("priority == 'Prioritário'").CustomerId), {10, 20, 30})
        self.assertEqual(result.loc[result.CustomerId == 40, "priority"].iloc[0], "Abaixo do risco mínimo")
        capped = assign_priority(self.data, 1, include_exited=True, minimum_risk=0.8)
        self.assertEqual((capped.priority == "Prioritário").sum(), 1)
        self.assertEqual((capped.priority == "Fora da capacidade").sum(), 2)
        self.assertEqual((assign_priority(self.data, 10, include_exited=True, minimum_risk=1).priority == "Prioritário").sum(), 0)
        self.assertTrue((assign_priority(self.data, 10, include_exited=True).priority == "Não definido").all())
        for invalid in [-0.1, 1.1, float("nan"), float("inf"), True]:
            with self.assertRaises(ValueError):
                assign_priority(self.data, 10, include_exited=True, minimum_risk=invalid)

    def test_demo_scope_and_oversized_capacity(self):
        result = assign_priority(self.data, 2, include_exited=True, minimum_risk=0.0)
        self.assertEqual(set(result.query("priority == 'Prioritário'").CustomerId), {20, 10})
        result = assign_priority(self.data, 100, include_exited=False, minimum_risk=0.0)
        self.assertEqual(len(result.query("priority == 'Prioritário'")), 2)


if __name__ == "__main__":
    unittest.main()
