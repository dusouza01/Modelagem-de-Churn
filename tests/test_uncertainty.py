import unittest

import pandas as pd

from src.churn_insights.uncertainty import observed_intervals


class ObservedIntervalTests(unittest.TestCase):
    def test_known_wilson_interval_and_input_preservation(self):
        source = pd.DataFrame({"clients": [100], "observed": [0.5]})
        result = observed_intervals(source)
        self.assertAlmostEqual(result.lower[0], 0.4038315304)
        self.assertAlmostEqual(result.upper[0], 0.5961684696)
        self.assertNotIn("lower", source)

    def test_extremes_empty_groups_and_sample_size(self):
        result = observed_intervals(pd.DataFrame({
            "clients": [1, 1, 0, 10, 1000],
            "observed": [0, 1, float("nan"), 0.5, 0.5],
        }))
        self.assertAlmostEqual(result.lower[0], 0)
        self.assertGreater(result.upper[0], 0)
        self.assertAlmostEqual(result.upper[1], 1)
        self.assertLess(result.lower[1], 1)
        self.assertTrue(result.loc[2, ["lower", "upper"]].isna().all())
        self.assertGreater(result.upper[3] - result.lower[3], result.upper[4] - result.lower[4])
