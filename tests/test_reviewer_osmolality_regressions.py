import unittest
from compat.osmolality import electrolyte_balance

class ReviewerOsmolalityRegressions(unittest.TestCase):
    def test_volume_missing_is_not_complete_ors(self):
        report = electrolyte_balance([("sodium_chloride", 0.01)])
        self.assertFalse(report["complete_ors"])
        self.assertIn("water_ml required", report["reason"])
