import unittest

from compat.arrhenius import assay_shelf_life_projection
from compat.osmolality import electrolyte_balance
from compat.pairwise import evaluate_pairwise
from compat.ph_module import citrate_ph_report
from compat.profiles import use_case_gate_report
from compat.redox import flag_from_components, redox_mechanism_ledger
from compat.report import evaluate_formula as evaluate_report
from compat.scoring import evaluate_formula as evaluate_score


class ReviewerRegressionTests(unittest.TestCase):
    def test_pairwise_out_of_scope_is_unknown_not_silent_pass(self):
        report = evaluate_pairwise(["dextrose", "beta_alanine"], "oil_emulsion")
        self.assertTrue(report["has_unknowns"])
        self.assertEqual(report["overall_severity"], "unknown")
        self.assertEqual(report["unmodeled_pairs"][0]["reason"], "matched rules do not model this phase_context")

    def test_pairwise_known_block_survives_unknown_pairs(self):
        report = evaluate_pairwise(["ascorbic_acid", "copper_tbcc", "l_tyrosine"], "wet_stored")
        self.assertEqual(report["max_known_severity"], "block")
        self.assertTrue(report["has_unknowns"])
        self.assertEqual(report["overall_severity"], "block")

    def test_electrolyte_balance_without_volume_is_not_ors_complete(self):
        report = electrolyte_balance([("sodium_chloride", 0.01)])
        self.assertFalse(report["complete_ors"])
        self.assertIn("water_ml required", report["reason"])

    def test_report_rejects_unknown_product_type(self):
        with self.assertRaises(ValueError):
            evaluate_report([("dextrose", 10.0)], product_type="hydration-drink", water_ml=100.0)

    def test_oral_drench_raw_hypertonic_blocks_even_without_hydration_type(self):
        report = evaluate_report([("dextrose", 30.0)], product_type="oral_drench", water_ml=100.0)
        self.assertEqual(report["overall"]["verdict"], "BLOCK")

    def test_acute_sublingual_missing_ph_is_insufficient_not_conditional_pass(self):
        report = use_case_gate_report([("dextrose", 1.0)], use_case="acute_sublingual", water_ml=10.0)
        self.assertEqual(report["mucosal_tolerance_advisory"], "insufficient_data_missing_pH")

    def test_scoring_rejects_unknown_product_and_dry_water_without_claim_is_dry(self):
        with self.assertRaises(ValueError):
            evaluate_score([], product_type="typo", water_ml=100.0)
        report = evaluate_score([], product_type="dry_capsule", water_ml=100.0, hydration_claim=False)
        self.assertFalse(report["applicability"]["solution_applies"])

    def test_redox_legacy_wrapper_does_not_assume_nac_is_wet_stored(self):
        legacy = flag_from_components([("n_acetylcysteine", 1.0)])
        self.assertFalse(legacy["applicable"])
        wet = flag_from_components([("n_acetylcysteine", 1.0)], storage_context="wet_stored")
        self.assertTrue(wet["applicable"])

    def test_redox_chelator_ratio_uses_mass_not_component_counts(self):
        report = redox_mechanism_ledger([
            ("trisodium_citrate", 2.94),
            ("copper_sulfate", 0.001),
        ], metal_ppm={"cu": 1.0})
        ratio = report["detected"].get("chelator_to_metal_molar_ratio") or report["detected"]
        self.assertTrue(report["detected"]["chelator"])

    def test_ph_report_does_not_invent_sorbate_when_absent(self):
        report = citrate_ph_report([("citric_acid", 0.7), ("trisodium_citrate", 0.3)], water_ml=1000.0)
        self.assertIsNone(report["preservative_active_fraction"])
        with self.assertRaises(ValueError):
            citrate_ph_report([("sodium_citrate", 0.3)], water_ml=1000.0)

    def test_assay_projection_rejects_mixed_storage_scope(self):
        rows = [
            {"temperature_C": 25.0, "time_days": 30.0, "measured_value": 99.0, "lot_id": "A"},
            {"temperature_C": 40.0, "time_days": 30.0, "measured_value": 95.0, "lot_id": "B"},
        ]
        with self.assertRaises(ValueError):
            assay_shelf_life_projection("ascorbate_oxidation", rows, analyte_or_marker="ascorbate", acceptance_limit=90.0)


if __name__ == "__main__":
    unittest.main()
