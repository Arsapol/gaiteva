import unittest
from compat.arrhenius import assay_shelf_life_projection

class ReviewerArrheniusRegressions(unittest.TestCase):
    def test_mixed_storage_scope_rejected(self):
        rows = [
            {"temperature_C": 25.0, "time_days": 30.0, "measured_value": 99.0, "lot_id": "A"},
            {"temperature_C": 40.0, "time_days": 30.0, "measured_value": 95.0, "lot_id": "B"},
        ]
        with self.assertRaises(ValueError):
            assay_shelf_life_projection("ascorbate_oxidation", rows, analyte_or_marker="ascorbate", acceptance_limit=90.0)
