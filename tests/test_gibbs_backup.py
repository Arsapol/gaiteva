import unittest

from compat.gibbs import gibbs, screen_pair


class GibbsBackupRoleTest(unittest.TestCase):
    def test_gibbs_result_is_not_a_primary_gate_even_when_spontaneous(self):
        result = gibbs(dH_J=-57_000, dS_J_per_K=80)
        self.assertTrue(result["spontaneous"])
        self.assertEqual(result["gate_role"], "backup_explanation")
        self.assertIs(result["primary_gate"], False)
        self.assertEqual(result["gate_effect"], "advisory_only")
        self.assertIn("BACKUP SCREEN ONLY", result["caveat"])

    def test_screen_pair_echoes_backup_gate_metadata(self):
        result = screen_pair("acid", "base", dH_J=-57_000, dS_J_per_K=80)
        self.assertEqual(result["gate_role"], "backup_explanation")
        self.assertIs(result["primary_gate"], False)
        self.assertEqual(result["gate_effect"], "advisory_only")
        self.assertIn("BACKUP SCREEN ONLY", result["caveat"])


if __name__ == "__main__":
    unittest.main()
