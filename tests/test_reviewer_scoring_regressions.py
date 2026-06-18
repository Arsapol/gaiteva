import unittest
from compat.scoring import evaluate_formula

class ReviewerScoringRegressions(unittest.TestCase):
    def test_unknown_product_type_rejected_and_dry_no_claim_exempt(self):
        with self.assertRaises(ValueError):
            evaluate_formula([], product_type="typo", water_ml=100.0)
        report = evaluate_formula([], product_type="dry_capsule", water_ml=100.0, hydration_claim=False)
        self.assertFalse(report["applicability"]["solution_applies"])
