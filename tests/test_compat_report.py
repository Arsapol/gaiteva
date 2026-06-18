import unittest

from compat import evaluate_formula, render_markdown
from compat_calc import COMPONENTS as FAILING_DRENCH, WATER_ML as FAILING_WATER_ML
from reformulate import LIQUID_ORS, WATER_ML as ORS_WATER_ML
from verify_dry_sku import FIGHT_DAY_DRINK, WATER_ML as DRINK_WATER_ML


def finding_ids(report):
    return {finding["id"] for finding in report["findings"]}


class CompatReportTests(unittest.TestCase):
    def test_failing_drench_report_blocks_with_schema_and_raw_gates(self):
        report = evaluate_formula(
            FAILING_DRENCH,
            product_type="hydration_drink",
            water_ml=FAILING_WATER_ML,
            target_ph=3.5,
        )
        self.assertEqual(report["schema_version"], "compat-eval-v0.1")
        self.assertEqual(report["overall"]["verdict"], "BLOCK")
        self.assertTrue(report["overall"]["blocking"])
        self.assertEqual(round(report["gates"]["osmolality"]["ors_gate"]["total_mosm_per_l"]), 1542)
        self.assertFalse(report["gates"]["osmolality"]["electrolyte_balance"]["complete_ors"])
        self.assertEqual(len(report["gates"]["solubility"]["bottlenecks"]), 2)
        ids = finding_ids(report)
        self.assertIn("osmolality.ors_gate", ids)
        self.assertIn("osmolality.electrolytes_incomplete", ids)
        self.assertTrue(any(f["severity"] == "BLOCKER" for f in report["findings"]))
        self.assertTrue(report["blocking_gates"])
        self.assertTrue(report["advisory_flags"])
        self.assertTrue(report["assumptions"])
        self.assertTrue(report["provenance"])
        self.assertEqual(report["next_validation"], report["validation_checklist"])

    def test_reformulated_ors_passes_with_complete_ors(self):
        report = evaluate_formula(LIQUID_ORS, product_type="hydration_drink", water_ml=ORS_WATER_ML)
        self.assertFalse(report["overall"]["blocking"])
        # high-aw shelf warning may make overall marginal, but hydration must pass.
        self.assertIn(report["overall"]["verdict"], {"PASS", "MARGINAL"})
        self.assertEqual(round(report["gates"]["osmolality"]["ors_gate"]["total_mosm_per_l"]), 274)
        self.assertTrue(report["gates"]["osmolality"]["electrolyte_balance"]["complete_ors"])
        self.assertEqual(report["gates"]["solubility"]["bottlenecks"], [])
        self.assertEqual(report["scores"]["hydration_cap"], 10.0)

    def test_dry_capsule_bypasses_standing_solution_gate(self):
        report = evaluate_formula([("l_tyrosine", 0.13)], product_type="dry_capsule")
        self.assertTrue(report["applicability"]["dry_ingestion"])
        self.assertFalse(report["gates"]["osmolality"]["applicable"])
        self.assertIn("osmolality.not_applicable", finding_ids(report))
        self.assertFalse(report["overall"]["blocking"])

    def test_reconstituted_dry_stick_drink_passes_current_fixture(self):
        report = evaluate_formula(FIGHT_DAY_DRINK, product_type="reconstituted_drink", water_ml=DRINK_WATER_ML)
        self.assertFalse(report["overall"]["blocking"])
        self.assertEqual(round(report["gates"]["osmolality"]["ors_gate"]["total_mosm_per_l"]), 291)
        self.assertTrue(report["gates"]["osmolality"]["electrolyte_balance"]["complete_ors"])
        self.assertEqual(report["gates"]["solubility"]["bottlenecks"], [])

    def test_markdown_renderer_uses_same_json_conclusions(self):
        report = evaluate_formula(LIQUID_ORS, product_type="hydration_drink", water_ml=ORS_WATER_ML)
        md = render_markdown(report)
        self.assertIn(report["schema_version"], md)
        self.assertIn(report["overall"]["verdict"], md)
        self.assertIn("osmolality.ors_gate", md)


if __name__ == "__main__":
    unittest.main()
