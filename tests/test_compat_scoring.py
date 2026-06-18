import unittest

from compat.scoring import evaluate_formula, score_osmolality_report, score_solubility_report
from compat.osmolality import osmolality_report
from compat.solubility import additive_report


class CompatScoringTests(unittest.TestCase):
    def test_hypertonic_incomplete_ors_caps_hydration_without_hiding_blocker(self):
        report = osmolality_report([("dextrose", 5.0)], water_ml=20.0)
        scored = score_osmolality_report(report)

        self.assertLessEqual(scored["hydration_cap"], 2.5)
        self.assertTrue(any(f["severity"] == "BLOCKER" for f in scored["findings"]))
        self.assertTrue(any(f.get("cap", {}).get("metric") == "hydration" for f in scored["findings"]))

    def test_solubility_bottleneck_score_comes_from_existing_report(self):
        report = additive_report([("l_tyrosine", 0.2)], water_ml=20.0)
        scored = score_solubility_report(report)

        self.assertLess(scored["score"], 4.0)
        self.assertTrue(any(f["id"] == "solubility.bottleneck" for f in scored["findings"]))

    def test_dry_capsule_does_not_apply_standing_solution_osmolality(self):
        normalized = evaluate_formula(
            [("l_tyrosine", 0.2)],
            product_type="dry_capsule",
            hydration_claim=False,
        )

        self.assertFalse(normalized["applicability"]["standing_solution"])
        self.assertEqual(normalized["scores"]["hydration_cap"], 10.0)
        self.assertFalse(normalized["overall"]["blocking"])

    def test_evaluate_formula_keeps_blocker_separate_from_aggregate_score(self):
        normalized = evaluate_formula(
            [("dextrose", 5.0)],
            product_type="hydration_drink",
            water_ml=20.0,
            hydration_claim=True,
            preservative_validated=False,
        )

        self.assertEqual(normalized["schema_version"], "compat-eval-v0.1")
        self.assertEqual(normalized["overall"]["verdict"], "BLOCK")
        self.assertTrue(any(f["severity"] == "BLOCKER" for f in normalized["findings"]))
        self.assertTrue(normalized["scores"]["stats_card_adjustments"])


if __name__ == "__main__":
    unittest.main()
