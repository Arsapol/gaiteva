import unittest
from compat.redox import flag_from_components

class ReviewerRedoxRegressions(unittest.TestCase):
    def test_legacy_wrapper_does_not_assume_nac_wet_stored(self):
        self.assertFalse(flag_from_components([("n_acetylcysteine", 1.0)])["applicable"])
        self.assertTrue(flag_from_components([("n_acetylcysteine", 1.0)], storage_context="wet_stored")["applicable"])
