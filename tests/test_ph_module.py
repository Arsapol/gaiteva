import unittest

from compat.ph_module import citrate_alpha_fractions, citrate_ph_report, preservative_active_fraction


class TestPhModule(unittest.TestCase):
    def test_alpha_fractions_are_normalized_at_citric_pkas(self):
        for ph in (3.13, 4.76, 6.40):
            alpha = citrate_alpha_fractions(ph)
            total = alpha["H3Cit"] + alpha["H2Cit_minus"] + alpha["HCit_2minus"] + alpha["Cit_3minus"]
            self.assertAlmostEqual(total, 1.0, places=12)
            self.assertGreaterEqual(alpha["average_negative_charge"], 0.0)
            self.assertLessEqual(alpha["average_negative_charge"], 3.0)

    def test_ors_fixture_predicts_pH_and_buffer_capacity(self):
        report = citrate_ph_report([("citric_acid", 0.7), ("trisodium_citrate", 0.3)], water_ml=1000.0)
        self.assertIsNotNone(report["predicted_pH"])
        self.assertGreater(report["predicted_pH"], 3.0)
        self.assertLess(report["predicted_pH"], 4.5)
        self.assertGreater(report["buffer_capacity"]["beta_mmol_per_l_per_pH"], 0.0)
        self.assertIn("screening-grade", report["caveats"][0])

    def test_dilution_reduces_buffer_capacity(self):
        report = citrate_ph_report([("citric_acid", 0.7), ("trisodium_citrate", 0.3)], water_ml=100.0, dilution_water_ml=1000.0)
        neat_beta = report["buffer_capacity"]["beta_mmol_per_l_per_pH"]
        diluted_beta = report["dilution"]["buffer_capacity"]["beta_mmol_per_l_per_pH"]
        self.assertGreater(neat_beta, diluted_beta)

    def test_measured_ph_override_preserves_prediction_error(self):
        report = citrate_ph_report([("citric_acid", 0.7), ("trisodium_citrate", 0.3)], water_ml=1000.0, measured_pH=3.8)
        self.assertEqual(report["effective_pH"], 3.8)
        self.assertIsNotNone(report["prediction_error_pH"])

    def test_sorbate_active_fraction_changes_with_pH(self):
        low = preservative_active_fraction(3.5)["undissociated_fraction"]
        high = preservative_active_fraction(6.0)["undissociated_fraction"]
        self.assertGreater(low, high)


if __name__ == "__main__":
    unittest.main()
