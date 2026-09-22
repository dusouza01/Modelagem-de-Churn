"""Data contract, persistence and no-retraining regression tests."""
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np
from streamlit.testing.v1 import AppTest

from src.churn_insights.artifacts import ArtifactError, ROOT, load_bundle, save_bundle
from src.churn_insights.importing import analyze_import
from src.churn_insights.model import load_data, predict_clients
from src.churn_insights.validation import DataValidationError, read_csv_bytes, validate_data


class EngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle, cls.metadata = load_bundle()
        cls.data = load_data().head(12)

    def payload(self, frame):
        return frame.to_csv(index=False).encode("utf-8-sig")

    def test_prediction_without_target_and_no_fit(self):
        with patch("sklearn.calibration.CalibratedClassifierCV.fit", side_effect=AssertionError("Prediction must never train")):
            result, metrics, overlap = analyze_import(self.payload(self.data.drop(columns="Exited")), self.bundle, historical=False)
        self.assertEqual(len(result), len(self.data))
        self.assertTrue(result.churn_probability.between(0, 1).all())
        self.assertIsNone(metrics)
        self.assertEqual(overlap, len(self.data))

    def test_missing_target_only_blocks_historical_mode(self):
        with self.assertRaisesRegex(DataValidationError, "Exited"):
            analyze_import(self.payload(self.data.drop(columns="Exited")), self.bundle, historical=True)

    def test_schema_rejections(self):
        for column, value in [("Balance", np.inf), ("Age", -1), ("Age", 2.5),
                              ("Surname", " "), ("Geography", "Unknown"),
                              ("HasCrCard", 3), ("Exited", 2), ("CreditScore", None)]:
            frame = self.data.copy()
            frame[column] = value
            with self.subTest(column=column, value=value), self.assertRaises(DataValidationError):
                validate_data(frame, categories=self.bundle["categories"])
        with self.assertRaisesRegex(DataValidationError, "IDs repetidos"):
            validate_data(self.data.assign(CustomerId=1))
        with self.assertRaisesRegex(DataValidationError, "Balance"):
            validate_data(self.data.drop(columns="Balance"))

    def test_csv_format_boundaries(self):
        for payload in [b"", b"a,a\n1,2", b"a,b\n1,2,3", b"\xff", b"x" * (10 * 1024 * 1024 + 1)]:
            with self.subTest(size=len(payload)), self.assertRaises(DataValidationError):
                read_csv_bytes(payload)

    def test_outcome_and_extra_columns_do_not_change_predictions(self):
        first = predict_clients(self.data, self.bundle)
        changed = self.data.assign(Exited=1 - self.data.Exited, extra=999)
        second = predict_clients(changed[list(reversed(changed.columns))], self.bundle)
        # Parallel tree sums can differ by machine precision between predictions.
        np.testing.assert_allclose(first.churn_probability, second.churn_probability, rtol=1e-12, atol=1e-15)

    def test_overlap_disables_independent_evaluation(self):
        _, metrics, overlap = analyze_import(self.payload(self.data), self.bundle, historical=True)
        self.assertIsNone(metrics)
        self.assertEqual(overlap, len(self.data))

    def test_import_evaluation_and_single_class(self):
        # Isolate the overlap branch with an empty registry; never used in the app.
        bundle = {**self.bundle, "source_ids": []}
        result, metrics, overlap = analyze_import(self.payload(self.data), bundle, historical=True)
        self.assertEqual(overlap, 0)
        self.assertAlmostEqual(metrics["brier"], float(((result.Exited - result.churn_probability) ** 2).mean()))
        _, metrics, _ = analyze_import(self.payload(self.data.assign(Exited=0)), bundle, historical=True)
        self.assertIsNone(metrics["auc"])

    def test_artifact_round_trip_versions_and_integrity(self):
        with TemporaryDirectory() as temporary:
            payload = (ROOT / "data" / "Churn_Modelling.csv").read_bytes()
            first = save_bundle(self.bundle, payload, temporary)
            second = save_bundle(self.bundle, payload, temporary)
            self.assertNotEqual(first["version"], second["version"])
            self.assertTrue((Path(temporary) / first["version"] / "model.joblib").exists())
            restored, metadata = load_bundle(directory=temporary)
            self.assertEqual(metadata["version"], second["version"])
            np.testing.assert_allclose(predict_clients(self.data, restored).churn_probability,
                                       predict_clients(self.data, self.bundle).churn_probability, rtol=1e-12, atol=1e-15)
            artifact = Path(temporary) / second["version"] / "model.joblib"
            artifact.write_bytes(b"broken")
            with patch("joblib.load") as loader, self.assertRaisesRegex(ArtifactError, "integridade"):
                load_bundle(directory=temporary)
            loader.assert_not_called()

    def test_incompatible_runtime_and_missing_model(self):
        with TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ArtifactError, "treinar.bat"):
                load_bundle(directory=temporary)
            metadata = save_bundle(self.bundle, b"test-only", temporary)
            path = Path(temporary) / metadata["version"] / "metadata.json"
            metadata["runtime"]["scikit-learn"] = "incompatible-test-version"
            path.write_text(json.dumps(metadata), encoding="utf-8")
            with patch("joblib.load") as loader, self.assertRaisesRegex(ArtifactError, "dependências"):
                load_bundle(directory=temporary)
            loader.assert_not_called()

    def test_import_interface(self):
        def page():
            from src.churn_insights.import_view import render_import
            render_import()
        app = AppTest.from_function(page, default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.selectbox(key="import_purpose").value)
        self.assertEqual(len(app.get("file_uploader")), 0)
        app.selectbox(key="import_purpose").set_value("Prever risco de clientes")
        with patch("streamlit.file_uploader", return_value=BytesIO(self.payload(self.data.drop(columns="Exited")))):
            app.run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe[0].value), len(self.data))
        app.selectbox(key="import_purpose").set_value("Avaliar resultados históricos")
        with patch("streamlit.file_uploader", return_value=BytesIO(self.payload(self.data.drop(columns="Exited")))):
            app.run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertEqual(len(app.dataframe), 0)


if __name__ == "__main__":
    unittest.main()
