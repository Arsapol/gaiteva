import unittest

from compat.profiles import get_use_case_profile, use_case_gate_report
from reformulate import LIQUID_ORS
from verify_dry_sku import FIGHT_DAY_DRINK
from concentrate import FINAL_PER_L, concentrate_per_l


class UseCaseProfileTests(unittest.TestCase):
    def test_hydration_drink_uses_blocking_ors_gate(self):
        report = use_case_gate_report(LIQUID_ORS, use_case="hydration_drink", water_ml=1000.0)
        self.assertFalse(report["hydration_blocking"])
        self.assertEqual(report["label_claim_allowed"], "hydration")
        self.assertEqual(report["liquid_gate"]["verdict"], "PASS")

    def test_dry_capsule_is_osmolality_exempt_without_standing_liquid_claim(self):
        report = use_case_gate_report([("l_tyrosine", 0.13)], use_case="dry_capsule")
        self.assertTrue(report["osmolality_exempt"])
        self.assertFalse(report["hydration_blocking"])
        self.assertIn("dose_uniformity_or_blend_uniformity", report["dry_state_advisory"])

    def test_reconstituted_dry_stick_runs_hydration_gate(self):
        report = use_case_gate_report(
            FIGHT_DAY_DRINK,
            use_case="dry_premix",
            water_ml=1000.0,
            standing_liquid_claim=True,
        )
        self.assertFalse(report["osmolality_exempt"])
        self.assertFalse(report["hydration_blocking"])
        self.assertEqual(report["liquid_gate"]["verdict"], "PASS")

    def test_acute_sublingual_does_not_get_hydration_claim(self):
        report = use_case_gate_report(
            [("dextrose", 9.0)],
            use_case="acute_sublingual",
            water_ml=50.0,
            ph=6.0,
            hydration_claim=True,
        )
        self.assertTrue(report["hydration_blocking"])
        self.assertIn("cannot carry hydration claim", report["blocking_reasons"][0])
        self.assertIn("oral_mucosal_tolerance_only", get_use_case_profile("acute_sublingual").allowed_claims)

    def test_wet_concentrate_reports_final_gate_and_storage_advisory(self):
        report = use_case_gate_report(
            FINAL_PER_L,
            use_case="wet_concentrate",
            water_ml=1000.0,
            hydration_claim=True,
            concentrate_components=concentrate_per_l(),
            concentrate_water_ml=1000.0,
        )
        self.assertFalse(report["hydration_blocking"])
        self.assertEqual(report["final_dilution_gate"]["verdict"], "PASS")
        self.assertIn("preservative_or_make_fresh_protocol", report["storage_stability_advisory"])
        self.assertIn("concentrate_solubility_advisory", report)


if __name__ == "__main__":
    unittest.main()
