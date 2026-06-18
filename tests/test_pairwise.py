import unittest

from compat.pairwise import evaluate_pairwise, format_pairwise_report, load_registry


class PairwiseRulesTest(unittest.TestCase):
    def test_registry_loads_and_has_required_rules(self):
        registry = load_registry()
        rule_ids = {rule["rule_id"] for rule in registry["rules"]}
        self.assertIn("PW-MAILLARD-REDUCING-SUGAR-PRIMARY-AMINE-001", rule_ids)
        self.assertIn("PW-ASCORBATE-TRANSITION-METAL-001", rule_ids)

    def test_wet_reducing_sugar_primary_amine_triggers_maillard(self):
        report = evaluate_pairwise(["dextrose", "beta_alanine"], "wet_stored")
        self.assertEqual(report["overall_severity"], "marginal")
        self.assertEqual(report["unknown_substances"], [])
        self.assertEqual(report["unmodeled_pairs"], [])
        self.assertEqual(report["rule_hits"][0]["rule_id"], "PW-MAILLARD-REDUCING-SUGAR-PRIMARY-AMINE-001")

    def test_dry_context_downgrades_but_keeps_evidence(self):
        report = evaluate_pairwise(["dextrose", "beta_alanine"], "dry")
        self.assertEqual(report["overall_severity"], "pass")
        self.assertEqual(report["rule_hits"][0]["applicability"], "mitigated-by-context")

    def test_ascorbate_copper_blocks_stored_wet(self):
        report = evaluate_pairwise(["ascorbic_acid", "copper_tbcc"], "wet_stored")
        severities = {hit["severity"] for hit in report["rule_hits"]}
        self.assertIn("block", severities)
        self.assertEqual(report["overall_severity"], "block")

    def test_unknown_substance_and_unmodeled_pair_are_explicit(self):
        report = evaluate_pairwise(["ascorbic_acid", "mystery_powder"], "wet_stored")
        self.assertEqual(report["overall_severity"], "unknown")
        self.assertEqual(report["unknown_substances"], ["mystery_powder"])
        self.assertEqual(len(report["unmodeled_pairs"]), 1)

    def test_format_mentions_gibbs_backup_role(self):
        report = evaluate_pairwise(["d_ribose", "ascorbic_acid"], "make_fresh")
        text = format_pairwise_report(report)
        self.assertIn("Gibbs role: backup-only", text)
        self.assertIn("PW-RIBOSE-ASCORBATE-REDOX-001", text)


if __name__ == "__main__":
    unittest.main()
