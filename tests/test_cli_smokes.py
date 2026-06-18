import subprocess
import sys
import unittest


class CliSmokeTest(unittest.TestCase):
    maxDiff = None

    def run_script(self, script: str) -> str:
        completed = subprocess.run(
            [sys.executable, script],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.stderr, "")
        return completed.stdout

    def test_reformulate_preserves_liquid_ors_golden_output(self):
        out = self.run_script("reformulate.py")

        self.assertIn("Osmolarity : 274 mOsm/L  ->  PASS", out)
        self.assertIn("Electrolytes (mmol/L):  Na 74.1  K 20.1  Cl 64.6", out)
        self.assertIn("Glucose     (mmol/L):  77.7  glucose:Na 1.05", out)
        self.assertIn("Complete ORS? YES", out)
        self.assertIn("LEVER 0 VERDICT: PASS", out)

    def test_verify_dry_sku_preserves_drink_golden_output(self):
        out = self.run_script("verify_dry_sku.py")

        self.assertIn("Products 1 (focus capsule) & 2 (preload premix): eaten DRY.", out)
        self.assertIn("Osmolarity : 291 mOsm/L  ->  PASS", out)
        self.assertIn("Electrolytes (mmol/L): Na 52.7 (wiki ~53)  K 14.8", out)
        self.assertIn("Glucose     (mmol/L): 111.0  glucose:Na 2.11", out)
        self.assertIn("DRINK VERDICT: PASS", out)

    def test_compat_calc_preserves_negative_hydration_gate(self):
        out = self.run_script("compat_calc.py")

        self.assertIn("Osmolarity : 1542 mOsm/L  ->  BLOCK", out)
        self.assertIn("Electrolytes (mmol/L): Na 0.0  K 0.0  Cl 0.0", out)
        self.assertIn("Glucose     (mmol/L): 444.0  glucose:Na N/A", out)
        self.assertIn("complete ORS? NO", out)
        self.assertIn("glucose:Na ratio unavailable", out)


if __name__ == "__main__":
    unittest.main()
