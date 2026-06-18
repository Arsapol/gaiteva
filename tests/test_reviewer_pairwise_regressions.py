import unittest
from compat.pairwise import evaluate_pairwise

class ReviewerPairwiseRegressions(unittest.TestCase):
    def test_out_of_scope_context_is_unknown_not_silent_pass(self):
        report = evaluate_pairwise(["dextrose", "beta_alanine"], "oil_emulsion")
        self.assertTrue(report["has_unknowns"])
        self.assertEqual(report["overall_severity"], "unknown")
    def test_known_block_survives_unknown_pairs(self):
        report = evaluate_pairwise(["ascorbic_acid", "copper_tbcc", "l_tyrosine"], "wet_stored")
        self.assertEqual(report["max_known_severity"], "block")
        self.assertEqual(report["overall_severity"], "block")
