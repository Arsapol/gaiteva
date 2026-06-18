import unittest
from compat.report import evaluate_formula

class ReviewerReportRegressions(unittest.TestCase):
    def test_unknown_product_type_fails_closed(self):
        with self.assertRaises(ValueError):
            evaluate_formula([("dextrose", 10.0)], product_type="hydration-drink", water_ml=100.0)
    def test_oral_drench_hypertonic_blocks_without_hydration_type(self):
        report = evaluate_formula([("dextrose", 30.0)], product_type="oral_drench", water_ml=100.0)
        self.assertEqual(report["overall"]["verdict"], "BLOCK")
