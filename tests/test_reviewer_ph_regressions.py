import unittest
from compat.ph_module import citrate_ph_report

class ReviewerPhRegressions(unittest.TestCase):
    def test_no_preservative_is_not_invented_and_citrate_form_must_be_exact(self):
        report = citrate_ph_report([("citric_acid", 0.7), ("trisodium_citrate", 0.3)], water_ml=1000.0)
        self.assertIsNone(report["preservative_active_fraction"])
        with self.assertRaises(ValueError):
            citrate_ph_report([("sodium_citrate", 0.3)], water_ml=1000.0)
