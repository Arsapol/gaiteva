import unittest
from compat.profiles import use_case_gate_report

class ReviewerProfilesRegressions(unittest.TestCase):
    def test_missing_ph_is_not_conditional_pass(self):
        report = use_case_gate_report([("dextrose", 1.0)], use_case="acute_sublingual", water_ml=10.0)
        self.assertEqual(report["mucosal_tolerance_advisory"], "insufficient_data_missing_pH")
    def test_nonpositive_water_rejected(self):
        with self.assertRaises(ValueError):
            use_case_gate_report([("dextrose", 1.0)], use_case="hydration_drink", water_ml=0.0)
