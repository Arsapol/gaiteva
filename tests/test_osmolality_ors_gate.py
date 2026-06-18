import unittest

from compat.osmolality import osmolality_report


LIQUID_ORS = [
    ("dextrose", 14.0),
    ("sodium_chloride", 2.6),
    ("potassium_chloride", 1.5),
    ("trisodium_citrate", 2.9),
    ("ascorbic_acid", 0.5),
    ("beta_alanine", 1.0),
    ("d_ribose", 2.0),
]

FIGHT_DAY_DRINK = [
    ("dextrose_monohydrate", 22.0),
    ("d_ribose", 5.0),
    ("sodium_chloride", 2.9),
    ("potassium_chloride", 1.1),
    ("l_citrulline", 1.15),
    ("citric_acid", 0.7),
    ("dmg", 0.4),
    ("trisodium_citrate", 0.3),
]


class VolumeAwareOrsGateTest(unittest.TestCase):
    def test_reformulated_liquid_ors_reports_volume_aware_values(self):
        report = osmolality_report(LIQUID_ORS, water_ml=1000.0)
        electro = report["electrolyte_balance"]

        self.assertFalse(report["blocking"])
        self.assertAlmostEqual(report["ors_gate"]["total_mosm_per_l"], 273.8, delta=0.5)
        self.assertAlmostEqual(electro["na_mmol_per_l"], 74.1, delta=0.2)
        self.assertAlmostEqual(electro["k_mmol_per_l"], 20.1, delta=0.2)
        self.assertAlmostEqual(electro["cl_mmol_per_l"], 64.6, delta=0.2)
        self.assertAlmostEqual(electro["glucose_mmol_per_l"], 77.7, delta=0.2)
        self.assertAlmostEqual(electro["glucose_to_na_ratio"], 1.05, delta=0.01)
        self.assertEqual(electro["completeness_warnings"], [])

    def test_fight_day_drink_reports_glucose_na_ratio(self):
        report = osmolality_report(FIGHT_DAY_DRINK, water_ml=1000.0)
        electro = report["electrolyte_balance"]

        self.assertFalse(report["blocking"])
        self.assertAlmostEqual(report["ors_gate"]["total_mosm_per_l"], 291.2, delta=0.5)
        self.assertAlmostEqual(electro["na_mmol_per_l"], 52.7, delta=0.2)
        self.assertAlmostEqual(electro["k_mmol_per_l"], 14.8, delta=0.2)
        self.assertAlmostEqual(electro["cl_mmol_per_l"], 64.4, delta=0.2)
        self.assertAlmostEqual(electro["glucose_mmol_per_l"], 111.0, delta=0.2)
        self.assertAlmostEqual(electro["glucose_to_na_ratio"], 2.11, delta=0.01)
        self.assertTrue(electro["complete_ors"])

    def test_trace_sodium_without_glucose_or_kcl_no_longer_passes_ors(self):
        report = osmolality_report([("sodium_chloride", 0.01)], water_ml=1000.0)
        electro = report["electrolyte_balance"]

        self.assertTrue(report["blocking"])
        self.assertFalse(electro["complete_ors"])
        self.assertIn("Na", "; ".join(electro["completeness_warnings"]))
        self.assertIn("glucose", "; ".join(electro["completeness_warnings"]))
        self.assertIn("glucose:Na ratio", "; ".join(electro["completeness_warnings"]))


if __name__ == "__main__":
    unittest.main()
